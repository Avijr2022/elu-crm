"""H-1 regression: a generic PATCH must not overwrite a concurrent suspension.

The C1 suite proves suspension-vs-suspension serialisation. It does not cover the
other writer: ``PATCH /api/v1/crm/customers/{id}``. Before the H-1 correction
``update_customer`` read the customer **without** ``FOR UPDATE`` while
``suspend_customer`` read it **with** the lock, so this interleaving was possible:

    PATCH   reads status=ACTIVE (no lock) and keeps that row in its identity map
    SUSPEND locks, sets SUSPENDED, writes history + audit, commits
    PATCH   saves its stale snapshot -> status silently reverts, and the history
            row and ``customer.suspended`` audit event now describe a status that
            no longer holds

This module reproduces that interleaving deterministically and asserts the fixed
behaviour: the PATCH **waits** on the customer-row lock (proved with
``pg_blocking_pids()``, not with sleeps), then observes SUSPENDED and is rejected by
the existing 403 guard before it can write anything.

``pytestmark = db_write``: the test commits (it must, for the rows to be visible
across independent sessions), so the C4 isolation guard skips it unless the target
database looks disposable - run it against a throwaway database, e.g.::

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
from app.schemas.crm.customer import CustomerSuspendRequest, CustomerUpdate
from app.services.crm import customer_service as customer_service_module
from app.services.crm.customer_service import CustomerService
from tests.conftest import platform_admin_select

pytestmark = pytest.mark.db_write

REASON_CODE = "CREDIT_RISK"
COMMENT = "H-1 concurrent PATCH probe"

#: Upper bound for the suspension worker to reach the audit write (which it only
#: reaches while holding the row lock).
LOCK_HOLD_TIMEOUT = 25.0
#: Upper bound for the PATCH backend to appear as blocked by the suspender.
LOCK_WAIT_TIMEOUT = 20.0
#: Upper bound for either worker to finish once the lock is released.
JOIN_TIMEOUT = 30.0


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


def _create_active_customer(tenant_id) -> tuple[uuid.UUID, str]:
    """Committed ACTIVE customer (visible to every other session)."""
    legal_name = f"Patch Race Probe {uuid.uuid4().hex[:8]}"
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        row = Customer(
            tenant_id=tenant_id,
            customer_number=f"RACE-{uuid.uuid4().hex[:10]}",
            legal_name=legal_name,
            status="ACTIVE",
            is_active=True,
            is_deleted=False,
        )
        db.add(row)
        db.commit()
        return row.customer_id, legal_name
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
    timeout: float = LOCK_WAIT_TIMEOUT,
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


# ---------------------------------------------------------------------- workers


def _suspend_in_own_session(
    tenant_id,
    customer_id,
    actor_id,
    payload,
    results,
    pids,
    pids_lock,
    worker_errors,
):
    """Suspend in its own session. The patched audit hook parks it holding the lock."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        with pids_lock:
            pids["suspend"] = _backend_pid(db)
        try:
            CustomerService(db).suspend_customer(
                tenant_id, customer_id, payload, actor_id
            )
            results.append(("ok", 200, None))
        except AppError as exc:
            results.append(("err", exc.http_status, exc.code))
    except Exception as exc:  # pragma: no cover - diagnostic path
        with pids_lock:
            worker_errors.append(f"suspend worker: {exc!r}")
    finally:
        clear_rls_context(db)
        db.close()


def _patch_in_own_session(
    tenant_id,
    customer_id,
    payload,
    patch_started,
    results,
    pids,
    pids_lock,
    worker_errors,
):
    """PATCH in its own session, exactly as ``PATCH /crm/customers/{id}`` does."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        with pids_lock:
            pids["patch"] = _backend_pid(db)
        patch_started.set()
        try:
            CustomerService(db).update_customer(tenant_id, customer_id, payload)
            results.append(("ok", 200, None))
        except AppError as exc:
            results.append(("err", exc.http_status, exc.code))
    except Exception as exc:  # pragma: no cover - diagnostic path
        with pids_lock:
            worker_errors.append(f"patch worker: {exc!r}")
    finally:
        clear_rls_context(db)
        db.close()


def _final_state(tenant_id, customer_id):
    """(status, version_no, legal_name, suspended_history_rows, suspended_events)."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        row = db.scalars(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.customer_id == customer_id,
            )
        ).first()
        assert row is not None, "customer disappeared"
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
                AuditEvent.tenant_id == tenant_id,
                AuditEvent.entity_id == customer_id,
                AuditEvent.event_type == "customer.suspended",
            )
        )
        return (
            row.status,
            int(row.version_no or 0),
            row.legal_name,
            int(history or 0),
            int(events or 0),
        )
    finally:
        clear_rls_context(db)
        db.close()


# ------------------------------------------------------------------------- test


def test_patch_cannot_overwrite_a_concurrent_suspension(actor, monkeypatch):
    """Suspension holds the row lock first; the PATCH waits, then is rejected (H-1)."""
    tenant_id, actor_id = actor
    customer_id, original_legal_name = _create_active_customer(tenant_id)

    suspend_payload = CustomerSuspendRequest(reason_code=REASON_CODE, comment=COMMENT)
    # A PATCH that would revert the lifecycle state if it were allowed to win.
    patch_payload = CustomerUpdate(
        status="INACTIVE", legal_name="RACE Patch Must Not Apply"
    )

    lock_held = threading.Event()
    release_lock = threading.Event()
    patch_started = threading.Event()

    pids: dict[str, int] = {}
    pids_lock = threading.Lock()
    worker_errors: list[str] = []
    suspend_results: list[tuple] = []
    patch_results: list[tuple] = []

    original_write_audit_event = customer_service_module.write_audit_event

    def blocking_write_audit_event(db, **kwargs):
        # Reached only after ``suspend_customer`` acquired the customer-row lock via
        # ``SELECT ... FOR UPDATE``. Parking here holds that lock for the whole wait.
        lock_held.set()
        release_lock.wait(timeout=LOCK_HOLD_TIMEOUT)
        return original_write_audit_event(db, **kwargs)

    monkeypatch.setattr(
        customer_service_module, "write_audit_event", blocking_write_audit_event
    )

    suspender = threading.Thread(
        target=_suspend_in_own_session,
        args=(
            tenant_id,
            customer_id,
            actor_id,
            suspend_payload,
            suspend_results,
            pids,
            pids_lock,
            worker_errors,
        ),
        name="h1-suspend",
        daemon=True,
    )
    patcher = threading.Thread(
        target=_patch_in_own_session,
        args=(
            tenant_id,
            customer_id,
            patch_payload,
            patch_started,
            patch_results,
            pids,
            pids_lock,
            worker_errors,
        ),
        name="h1-patch",
        daemon=True,
    )

    suspender.start()
    assert lock_held.wait(timeout=LOCK_HOLD_TIMEOUT), (
        "suspension never acquired the customer-row lock; "
        f"errors={worker_errors} results={suspend_results}"
    )

    patcher.start()
    try:
        assert patch_started.wait(timeout=LOCK_HOLD_TIMEOUT), (
            f"PATCH worker never started; errors={worker_errors}"
        )
        suspend_pid = pids["suspend"]
        patch_pid = pids["patch"]
        assert suspend_pid != patch_pid, "workers shared one backend PID"

        # Deterministic, per-PID lock-wait proof: the PATCH backend must be blocked
        # specifically by the backend that holds the suspension's row lock.
        blockers = _wait_until_blocked_by(patch_pid, suspend_pid, timeout=LOCK_WAIT_TIMEOUT)
        assert suspend_pid in blockers, (
            f"PATCH backend {patch_pid} was not blocked by the suspending backend "
            f"{suspend_pid} - the customer-row lock did not serialise the writers; "
            f"blockers={blockers} results={patch_results}"
        )
        assert patch_results == [], (
            "PATCH completed while the suspension held the row lock; "
            f"results={patch_results}"
        )
    finally:
        # Always release, otherwise a failed assertion would strand both workers and
        # hold the row lock for the rest of the session.
        release_lock.set()

    for worker in (suspender, patcher):
        worker.join(timeout=JOIN_TIMEOUT)
    assert not any(worker.is_alive() for worker in (suspender, patcher)), (
        "a worker did not finish"
    )
    assert worker_errors == [], worker_errors

    # ---- suspension succeeded exactly once; the PATCH was rejected
    assert suspend_results == [("ok", 200, None)], suspend_results
    assert patch_results == [("err", 403, "FORBIDDEN")], (
        f"expected the existing 403 ForbiddenError, got {patch_results}"
    )

    # ---- post-conditions: suspension intact, no duplicate trail, PATCH wrote nothing
    status, version_no, legal_name, history_rows, events = _final_state(
        tenant_id, customer_id
    )
    assert status == "SUSPENDED", (
        f"the PATCH overwrote the suspension: status={status!r}"
    )
    assert version_no == 2, f"expected one increment (suspension), got version_no={version_no}"
    assert legal_name == original_legal_name, (
        "the rejected PATCH still applied a field: "
        f"legal_name={legal_name!r} expected={original_legal_name!r}"
    )
    assert history_rows == 1, f"duplicate suspension history rows: {history_rows}"
    assert events == 1, f"duplicate customer.suspended audit events: {events}"
