"""C1 regression: concurrent suspension must be serialised (REQ-CRM-028).

Two **independent** SQLAlchemy sessions (therefore two independent PostgreSQL
transactions/connections) call ``CustomerService.suspend_customer`` for the same
ACTIVE customer at the same moment. A ``threading.Barrier`` releases both at once and
the audit-write hook proves the winner is holding the row lock while the loser is
blocked, so the interleaving is deterministic rather than timing-dependent.

``pytestmark = db_write``: this module commits (it must, for the rows to be visible
across sessions), so the C4 isolation guard skips it unless the target database looks
disposable - run it against a throwaway database, e.g.::

    DATABASE_URL=postgresql+psycopg://<user>@localhost:15432/elinkup_test pytest -m db_write
"""

import threading
import time
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text

from app.core.exceptions import AppError
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal, engine
from app.main import app
from app.models.crm import Customer, CustomerStatusHistory
from app.models.pf import AuditEvent
from app.schemas.crm.customer import CustomerSuspendRequest
from app.services.crm import customer_service as customer_service_module
from app.services.crm.customer_service import CustomerService
from tests.conftest import platform_admin_select

pytestmark = pytest.mark.db_write

REASON_CODE = "CREDIT_RISK"
COMMENT = "concurrent suspension probe"


# --------------------------------------------------------------------- bootstrap


@pytest.fixture(scope="module")
def bootstrapped():
    """Run the app lifespan once to create the schema and seed the platform tenant."""
    with TestClient(app):
        yield


@pytest.fixture(scope="module")
def actor(bootstrapped):
    """(tenant_id, user_id) of the seeded platform admin."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None, "platform admin missing - seed did not run"
        return admin.tenant_id, admin.user_id
    finally:
        clear_rls_context(db)
        db.close()


# ----------------------------------------------------------------------- helpers


def _create_active_customer(tenant_id) -> uuid.UUID:
    """Committed ACTIVE customer (visible to every other session)."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        row = Customer(
            tenant_id=tenant_id,
            customer_number=f"CONC-{uuid.uuid4().hex[:10]}",
            legal_name=f"Concurrency Probe {uuid.uuid4().hex[:8]}",
            status="ACTIVE",
            is_active=True,
            is_deleted=False,
        )
        db.add(row)
        db.commit()
        return row.customer_id
    finally:
        clear_rls_context(db)
        db.close()


def _suspend_in_own_session(
    tenant_id,
    customer_id,
    actor_id,
    payload,
    barrier,
    results,
    pids,
    pids_lock,
    worker_errors,
):
    """One worker = one session = one independent PostgreSQL transaction."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        # Publish THIS worker's own backend PID before the barrier, so the main thread
        # can ask PostgreSQL specifically about this connection rather than counting
        # any blocked backend in the database.
        pid = _backend_pid(db)
        with pids_lock:
            pids[threading.current_thread().name] = pid
        barrier.wait(timeout=20)
        try:
            CustomerService(db).suspend_customer(
                tenant_id, customer_id, payload, actor_id
            )
            results.append(("ok", 200))
        except AppError as exc:
            results.append(("err", exc.http_status, exc.code))
    except Exception as exc:  # pragma: no cover - diagnostic path
        with pids_lock:
            worker_errors.append(f"{threading.current_thread().name}: {exc!r}")
    finally:
        clear_rls_context(db)
        db.close()


def _backend_pid(db) -> int:
    """The PostgreSQL backend PID serving this very session."""
    return int(db.execute(text("select pg_backend_pid()")).scalar_one())


def _blocking_pids_of(pid: int) -> list[int]:
    """Backends currently blocking ``pid`` (empty when ``pid`` is not blocked)."""
    with engine.connect() as conn:
        blocking = conn.exec_driver_sql(
            "select pg_blocking_pids(%s)", (pid,)
        ).scalar_one()
    return [int(item) for item in (blocking or [])]


def _wait_until_blocked_by(
    blocked_pid: int,
    expected_blocker_pid: int,
    timeout: float = 20.0,
    interval: float = 0.05,
) -> list[int]:
    """Bounded poll until ``blocked_pid`` is blocked *by* ``expected_blocker_pid``.

    Returns the last observed blocker list so a failed assertion can report it.
    """
    deadline = time.monotonic() + timeout
    seen: list[int] = []
    while time.monotonic() < deadline:
        seen = _blocking_pids_of(blocked_pid)
        if expected_blocker_pid in seen:
            return seen
        time.sleep(interval)
    return seen


def _read_counts(tenant_id, customer_id):
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        history = db.scalar(
            select(func.count())
            .select_from(CustomerStatusHistory)
            .where(
                CustomerStatusHistory.tenant_id == tenant_id,
                CustomerStatusHistory.customer_id == customer_id,
                CustomerStatusHistory.to_status == "SUSPENDED",
            )
        )
        events = db.scalar(
            select(func.count())
            .select_from(AuditEvent)
            .where(
                AuditEvent.entity_id == customer_id,
                AuditEvent.event_type == "customer.suspended",
            )
        )
        row = db.scalars(
            select(Customer).where(Customer.customer_id == customer_id)
        ).first()
        assert row is not None
        return int(history or 0), int(events or 0), row.status, int(row.version_no or 0)
    finally:
        clear_rls_context(db)
        db.close()


# ------------------------------------------------------------------------- test


def test_concurrent_suspension_creates_exactly_one_record_set(actor, monkeypatch):
    """Two simultaneous requests: one wins, one gets 409, exactly one record set."""
    tenant_id, actor_id = actor
    customer_id = _create_active_customer(tenant_id)
    payload = CustomerSuspendRequest(reason_code=REASON_CODE, comment=COMMENT)

    barrier = threading.Barrier(2)
    lock_holder_ready = threading.Event()
    release_holder = threading.Event()
    holder = {}
    results: list[tuple] = []
    pids: dict[str, int] = {}
    pids_lock = threading.Lock()
    worker_errors: list[str] = []

    original_write_audit_event = customer_service_module.write_audit_event

    def blocking_write_audit_event(db, **kwargs):
        # Only the transaction that actually acquired the row lock can reach this
        # point: the other one is still blocked inside ``SELECT ... FOR UPDATE``.
        if not holder:
            holder["thread"] = threading.current_thread().name
            lock_holder_ready.set()
            release_holder.wait(timeout=20)
        return original_write_audit_event(db, **kwargs)

    monkeypatch.setattr(
        customer_service_module, "write_audit_event", blocking_write_audit_event
    )

    workers = [
        threading.Thread(
            target=_suspend_in_own_session,
            args=(
                tenant_id,
                customer_id,
                actor_id,
                payload,
                barrier,
                results,
                pids,
                pids_lock,
                worker_errors,
            ),
            name=f"c1-{index}",
            daemon=True,
        )
        for index in (1, 2)
    ]
    for worker in workers:
        worker.start()

    if not lock_holder_ready.wait(timeout=25):
        raise AssertionError(
            f"no request reached the audit write; worker_errors={worker_errors}"
        )
    try:
        # Deterministic, per-PID observation (no fixed sleep, no "any blocked backend"
        # heuristic): resolve which worker holds the lock, then ask PostgreSQL whether
        # the OTHER worker's backend is blocked specifically by the holder's backend.
        winner = holder.get("thread")
        assert winner is not None, "no winning worker was recorded"
        others = [name for name in pids if name != winner]
        assert len(pids) == 2 and len(others) == 1, f"unexpected worker PIDs: {pids}"
        loser = others[0]
        winner_pid, loser_pid = pids[winner], pids[loser]
        assert winner_pid != loser_pid, "workers shared one backend PID"

        blockers = _wait_until_blocked_by(loser_pid, winner_pid, timeout=20.0)
        assert winner_pid in blockers, (
            f"losing backend {loser_pid} was not blocked by winner {winner_pid}; "
            f"blockers={blockers}"
        )
        assert results == [], f"the second request was not blocked; results={results}"
    finally:
        # Always release the holder, otherwise a failed assertion would strand both
        # worker threads and hang the session.
        release_holder.set()

    for worker in workers:
        worker.join(timeout=30)
    assert not any(worker.is_alive() for worker in workers), "a worker did not finish"

    # ---- exactly one success and exactly one 409
    assert len(results) == 2, results
    successes = [r for r in results if r[0] == "ok"]
    conflicts = [r for r in results if r[0] == "err"]
    assert len(successes) == 1, results
    assert successes[0] == ("ok", 200), results
    assert len(conflicts) == 1, results
    assert conflicts[0][1] == 409, results
    assert conflicts[0][2] == "CONFLICT", results

    # ---- exactly one history row, one audit event, one version increment
    history_rows, audit_events, status, version_no = _read_counts(
        tenant_id, customer_id
    )
    assert history_rows == 1, f"duplicate history rows: {history_rows}"
    assert audit_events == 1, f"duplicate audit events: {audit_events}"
    assert status == "SUSPENDED"
    assert version_no == 2, f"version_no incremented {version_no - 1} times"

    # ---- the losing request left no trace of its own
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        actors = list(
            db.scalars(
                select(CustomerStatusHistory.actor_id).where(
                    CustomerStatusHistory.customer_id == customer_id
                )
            ).all()
        )
        assert actors == [actor_id]
        reasons = list(
            db.scalars(
                select(CustomerStatusHistory.reason).where(
                    CustomerStatusHistory.customer_id == customer_id
                )
            ).all()
        )
        assert reasons == [f"[{REASON_CODE}] {COMMENT}"]
    finally:
        clear_rls_context(db)
        db.close()
