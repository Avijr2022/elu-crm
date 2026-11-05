"""CRM-011 enterprise tenant isolation (RLS) for the CRM schema.

Covers ``Database/04_CRM/011_crm_rls_tenant_isolation.sql``: the ten CRM tables
that PF-003A does NOT own (that migration owns ``crm.lead`` / ``crm.opportunity``).

Scope of the assertions:

1. schema invariants - ENABLE + FORCE RLS and exactly one ``tenant_isolation``
   policy per table, with the PF-003A tenant/platform-context expression;
2. the PF-003A policies on ``crm.lead`` / ``crm.opportunity`` are unchanged;
3. a session with no tenant context sees nothing (fail closed) and cannot insert;
4. tenant A cannot SELECT tenant B rows;
5. tenant A cannot INSERT a row belonging to tenant B;
6. tenant A cannot UPDATE or DELETE tenant B rows;
7. ``app.platform_context=true`` keeps cross-tenant visibility;
8. re-running the migration is a no-op;
9. CRM lookup lazy seeding (``CrmLookupService.ensure_tenant_defaults``) runs
   under tenant RLS and stays tenant-scoped;
10. Finance-only customer suspension still works, including the
    ``crm.customer_status_history`` row and the ``customer.suspended`` audit event.

Conventions reused from the existing suite:

* the module is gated behind the ``db_write`` marker (see ``tests/conftest.py``),
  so it is skipped unless the target database is disposable;
* ``client`` (``TestClient(app)``) is a dependency of *every* fixture that touches
  the database, because on a fresh CI database ``elu_app``, the CRM tables and the
  PF-003A policies only exist after the app lifespan has run (see the conftest note
  about DB-order-neutral helpers);
* row fixtures are created inside ``platform_session()`` and committed, so the
  probe sessions (a *different* connection) really have to pass through RLS;
* cross-tenant probes always run as ``elu_app`` (``bind_rls_context`` issues
  ``SET LOCAL ROLE elu_app``) and assert ``current_user`` explicitly - a
  superuser/owner session would prove nothing about RLS enforcement.

Temporary tenants, users and rows are left in place (the database is disposable by
definition of the ``db_write`` gate); nothing is deleted from shared tenants.
"""

import json
import re
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import date
from pathlib import Path
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_crm import apply_crm_ddl
from app.db.rls_context import bind_rls_context, clear_rls_context, owner_role
from app.db.session import SessionLocal
from app.main import app
from app.models.crm import (
    Activity,
    ActivityLink,
    ActivityOutcome,
    ActivityType,
    Customer,
    CustomerAddress,
    CustomerContact,
    CustomerStatusHistory,
    CustomerTaxRegistration,
    OpportunityStage,
)
from app.models.pf import AuditEvent, Edition, Role, Tenant, User
from app.services.crm.lookup_service import CrmLookupService
from tests.conftest import (
    _is_disposable_database,
    _target_database_name,
    platform_admin_select,
    platform_session,
)

# C4 / REQ-CRM-028: the module starts the application lifespan (DDL + seed) and
# commits tenants, users and rows, so it must never run against a shared database.
pytestmark = pytest.mark.db_write

#: The ten tables approved for CRM-011, in the migration's declared order.
CRM_RLS_TABLES: tuple[str, ...] = (
    "customer",
    "customer_contact",
    "customer_address",
    "customer_tax_registration",
    "customer_status_history",
    "activity",
    "activity_link",
    "activity_type",
    "activity_outcome",
    "opportunity_stage",
)

#: Owned by PF-003A; CRM-011 must not touch them.
PF003A_OWNED_TABLES: tuple[str, ...] = ("lead", "opportunity")

#: Fragments every tenant-isolation expression must contain (PF-003A semantics).
POLICY_FRAGMENTS: tuple[str, ...] = (
    "app.platform_context",
    "app.tenant_id",
    "NULLIF",
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION_PATH = _REPO_ROOT / "Database" / "04_CRM" / "011_crm_rls_tenant_isolation.sql"
PF003A_PATH = _REPO_ROOT / "Database" / "03_PlatformFoundation" / "012_rls_pf003a.sql"

USER_PASSWORD = "Crm011Rls!234"
SUSPEND_REASON = "CREDIT_RISK"
SUSPEND_COMMENT = "CRM-011 RLS coverage - finance-only suspension"


# --------------------------------------------------------------------- helpers


def _qualified(table: str) -> str:
    """Fully qualified name for a whitelisted CRM table (no string interpolation risk)."""
    assert table in CRM_RLS_TABLES or table in PF003A_OWNED_TABLES, table
    return f"crm.{table}"


def _norm(expression: str | None) -> str:
    """Collapse whitespace so PostgreSQL's rendering can be compared."""
    return " ".join((expression or "").split())


def _current_role(db: Session) -> str:
    """The role the probe really executes as (``elu_app`` is NOBYPASSRLS)."""
    return db.execute(text("SELECT current_user")).scalar_one()


@contextmanager
def _rls_session(
    *, tenant_id: UUID | str | None = None, platform: bool = False
) -> Iterator[Session]:
    """Session bound to the application's real RLS context (``SET LOCAL ROLE elu_app``)."""
    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tenant_id, platform=platform)
        yield db
    finally:
        db.rollback()
        clear_rls_context(db)
        db.close()


def _rls_flags(db: Session, table: str) -> tuple[bool, bool]:
    """``(relrowsecurity, relforcerowsecurity)`` for a CRM table."""
    row = db.execute(
        text(
            "SELECT relrowsecurity, relforcerowsecurity "
            "FROM pg_class WHERE oid = to_regclass(:q)"
        ),
        {"q": _qualified(table)},
    ).one_or_none()
    assert row is not None, f"{_qualified(table)} does not exist"
    return bool(row[0]), bool(row[1])


def _policies(db: Session, table: str) -> list[tuple]:
    """All policies on a CRM table as plain tuples (stable for equality checks)."""
    rows = db.execute(
        text(
            "SELECT policyname, permissive, cmd, qual, with_check "
            "FROM pg_policies WHERE schemaname = 'crm' AND tablename = :t "
            "ORDER BY policyname"
        ),
        {"t": table},
    ).all()
    return [tuple(row) for row in rows]


def _count_visible(db: Session, table: str, tenant_id: UUID | str) -> int:
    """Rows of ``table`` visible to the current RLS context for one tenant."""
    return db.execute(
        text(f"SELECT count(*) FROM {_qualified(table)} WHERE tenant_id = :t"),
        {"t": tenant_id},
    ).scalar_one()


def _total_visible(db: Session, table: str) -> int:
    """Rows of ``table`` visible to the current RLS context, whatever the tenant."""
    return db.execute(text(f"SELECT count(*) FROM {_qualified(table)}")).scalar_one()


def _savepoint_rowcount(db: Session, sql: str, params: dict) -> int:
    """Run a DML statement inside a savepoint and always roll it back.

    The row count is observable, but a policy bug can never destroy fixture data.
    """
    savepoint = db.begin_nested()
    try:
        return db.execute(text(sql), params).rowcount
    finally:
        savepoint.rollback()


def _expect_rls_violation(db: Session, sql: str, params: dict) -> None:
    """The statement must be rejected by RLS (SQLSTATE 42501), not by a constraint."""
    with pytest.raises(DBAPIError) as excinfo:
        with db.begin_nested():
            db.execute(text(sql), params)
    sqlstate = getattr(excinfo.value.orig, "sqlstate", None)
    assert sqlstate == "42501", f"expected an RLS violation, got: {excinfo.value!r}"


def _apply_migration_011(db: Session) -> None:
    """Execute 011 exactly the way ``apply_crm_ddl`` does (owner role, one commit)."""
    sql = MIGRATION_PATH.read_text(encoding="utf-8")
    with owner_role():
        db.execute(text("RESET ROLE"))
        db.execute(text(sql))
        db.commit()


def _policy_bodies(sql_text: str) -> list[str]:
    """The ``$p$ ... $p$`` policy expressions contained in a migration."""
    return re.findall(r"\$p\$(.*?)\$p\$", sql_text, flags=re.DOTALL)


def _insert_spec(table: str, tenant_id: UUID, parents: dict) -> tuple[str, dict]:
    """An INSERT of a row that belongs to ``tenant_id``.

    Parent rows (``parents``) belong to the same tenant, so foreign keys are
    satisfiable and the *only* reason for rejection is the RLS ``WITH CHECK``.
    """
    row_id = uuid.uuid4()
    if table == "customer":
        return (
            "INSERT INTO crm.customer "
            "(customer_id, tenant_id, customer_number, legal_name) "
            "VALUES (:id, :tid, :num, 'Cross Tenant')",
            {"id": row_id, "tid": tenant_id, "num": f"XT-{uuid.uuid4().hex[:10]}"},
        )
    if table == "customer_contact":
        return (
            "INSERT INTO crm.customer_contact "
            "(customer_contact_id, tenant_id, customer_id, first_name) "
            "VALUES (:id, :tid, :cid, 'Cross')",
            {"id": row_id, "tid": tenant_id, "cid": parents["customer_id"]},
        )
    if table == "customer_address":
        return (
            "INSERT INTO crm.customer_address "
            "(customer_address_id, tenant_id, customer_id, address_line1) "
            "VALUES (:id, :tid, :cid, '1 Cross Street')",
            {"id": row_id, "tid": tenant_id, "cid": parents["customer_id"]},
        )
    if table == "customer_tax_registration":
        return (
            "INSERT INTO crm.customer_tax_registration "
            "(customer_tax_registration_id, tenant_id, customer_id, tax_type, tax_number) "
            "VALUES (:id, :tid, :cid, 'GSTIN', :num)",
            {
                "id": row_id,
                "tid": tenant_id,
                "cid": parents["customer_id"],
                "num": f"27{uuid.uuid4().hex[:13].upper()}",
            },
        )
    if table == "customer_status_history":
        return (
            "INSERT INTO crm.customer_status_history "
            "(customer_status_history_id, tenant_id, customer_id, from_status, "
            " to_status, reason, actor_id) "
            "VALUES (:id, :tid, :cid, 'ACTIVE', 'SUSPENDED', 'cross tenant', :actor)",
            {
                "id": row_id,
                "tid": tenant_id,
                "cid": parents["customer_id"],
                "actor": parents["user_id"],
            },
        )
    if table == "activity":
        return (
            "INSERT INTO crm.activity "
            "(activity_id, tenant_id, subject, owner_id) "
            "VALUES (:id, :tid, 'Cross Tenant Activity', :owner)",
            {"id": row_id, "tid": tenant_id, "owner": parents["user_id"]},
        )
    if table == "activity_link":
        return (
            "INSERT INTO crm.activity_link "
            "(activity_link_id, tenant_id, activity_id, entity_type, entity_id) "
            "VALUES (:id, :tid, :aid, 'CUSTOMER', :eid)",
            {
                "id": row_id,
                "tid": tenant_id,
                "aid": parents["activity_id"],
                "eid": parents["customer_id"],
            },
        )
    if table == "activity_type":
        return (
            "INSERT INTO crm.activity_type (activity_type_id, tenant_id, code, name) "
            "VALUES (:id, :tid, :code, 'Cross Type')",
            {"id": row_id, "tid": tenant_id, "code": f"XT{uuid.uuid4().hex[:6].upper()}"},
        )
    if table == "activity_outcome":
        return (
            "INSERT INTO crm.activity_outcome "
            "(activity_outcome_id, tenant_id, activity_type_code, code, name) "
            "VALUES (:id, :tid, :tcode, :code, 'Cross Outcome')",
            {
                "id": row_id,
                "tid": tenant_id,
                "tcode": f"XT{uuid.uuid4().hex[:6].upper()}",
                "code": "OK",
            },
        )
    if table == "opportunity_stage":
        return (
            "INSERT INTO crm.opportunity_stage "
            "(opportunity_stage_id, tenant_id, code, name) "
            "VALUES (:id, :tid, :code, 'Cross Stage')",
            {"id": row_id, "tid": tenant_id, "code": f"XT{uuid.uuid4().hex[:6].upper()}"},
        )
    raise AssertionError(f"no insert spec for {table}")


# ------------------------------------------------------------------- fixtures


@pytest.fixture(scope="module")
def _verified_database() -> str:
    """Verify the target database is disposable *before* anything opens it.

    ``tests/conftest.py`` already skips ``db_write`` tests on a non-disposable
    database; this is the second, explicit check requested by the CRM-011 brief.
    Both helpers only parse ``DATABASE_URL`` - no connection is opened, which
    keeps the fixture safe on a fresh CI database (no ``elu_app`` role yet).

    There is deliberately **no** environment-variable escape hatch here: the
    CRM-011 tests seed tenants, rewrite password hashes and commit rows, so they
    are disposable-database-only by policy. ``ELU_ALLOW_SHARED_DB_WRITE`` (which
    only relaxes the conftest skip) must never lift this assertion.
    """
    name = _target_database_name()
    assert _is_disposable_database(name), (
        f"refusing to run CRM-011 RLS tests against non-disposable database {name!r}: "
        "CRM-011 tests are disposable-database-only; point DATABASE_URL at a "
        "*_test/_tests database (or one prefixed test_/tmp_)"
    )
    return name


@pytest.fixture(scope="module")
def client(_verified_database: str) -> Iterator[TestClient]:
    """Start the application (lifespan: roles, DDL, seed, CRM migrations incl. 011)."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def tenants(client: TestClient) -> dict[str, dict]:
    """Two disposable tenants, each with one committed row in all ten RLS tables."""
    with platform_session() as db:
        edition = db.scalars(select(Edition).order_by(Edition.code)).first()
        assert edition is not None, "no edition seeded - cannot create a temporary tenant"
        owner = db.scalars(platform_admin_select()).first()
        assert owner is not None, "seeded platform admin missing"

        # ``_seed_tenant_rows`` returns plain UUIDs (read right after flush), so the
        # values stay usable once this session closes and the ORM objects detach.
        created: dict[str, dict] = {}
        for tag in ("A", "B"):
            tenant = _new_tenant(db, edition.id, tag)
            data = _seed_tenant_rows(db, tenant, owner.user_id)
            data["user_id"] = owner.user_id
            data["tenant_code"] = tenant.tenant_code
            created[tag.lower()] = data
        db.commit()
        return created


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    return _login(
        client, settings.seed_admin_email, settings.seed_admin_password, "EIIP001"
    )


@pytest.fixture(scope="module")
def finance_user(client: TestClient, admin_token: str) -> str:
    return _role_token(client, "FINANCE_USER")


@pytest.fixture(scope="module")
def sales_manager_user(client: TestClient, admin_token: str) -> str:
    return _role_token(client, "SALES_MANAGER")


# --------------------------------------------------------------- row plumbing


def _new_tenant(db: Session, edition_id, tag: str) -> Tenant:
    """Temporary tenant (same shape as ``test_crm_tenant_composite_fks``)."""
    suffix = uuid.uuid4().hex[:8].upper()
    tenant = Tenant(
        tenant_code=f"CR11{tag}{suffix}"[:32],
        tenant_name=f"CRM-011 {tag} {suffix}",
        legal_name=f"CRM-011 {tag} {suffix} Ltd",
        edition_id=edition_id,
        organization_type="Pvt Ltd",
        email=f"crm011-{tag.lower()}-{suffix.lower()}@example.test",
        mobile="+9190" + str(uuid.uuid4().int)[:8],
        status="ACTIVE",
        activation_date=date.today(),
        is_active=True,
        is_deleted=False,
    )
    db.add(tenant)
    db.flush()
    return tenant


def _seed_tenant_rows(db: Session, tenant: Tenant, user_id) -> dict:
    """One row per RLS table, all belonging to ``tenant``."""
    customer = Customer(
        tenant_id=tenant.tenant_id,
        customer_number=f"CUS-{uuid.uuid4().hex[:12]}",
        legal_name=f"RLS Customer {uuid.uuid4().hex[:6]}",
        status="PROSPECT",
    )
    db.add(customer)
    db.flush()

    activity = Activity(
        tenant_id=tenant.tenant_id,
        subject=f"RLS Activity {uuid.uuid4().hex[:6]}",
        owner_id=user_id,
        status="COMPLETED",
    )
    db.add(activity)
    db.flush()

    db.add(
        CustomerContact(
            tenant_id=tenant.tenant_id,
            customer_id=customer.customer_id,
            first_name="Rls",
        )
    )
    db.add(
        CustomerAddress(
            tenant_id=tenant.tenant_id,
            customer_id=customer.customer_id,
            address_line1="1 RLS Street",
        )
    )
    db.add(
        CustomerTaxRegistration(
            tenant_id=tenant.tenant_id,
            customer_id=customer.customer_id,
            tax_type="GSTIN",
            tax_number=f"27{uuid.uuid4().hex[:13].upper()}",
        )
    )
    db.add(
        CustomerStatusHistory(
            tenant_id=tenant.tenant_id,
            customer_id=customer.customer_id,
            from_status="PROSPECT",
            to_status="ACTIVE",
            reason="rls seed",
            actor_id=user_id,
        )
    )
    db.add(
        ActivityLink(
            tenant_id=tenant.tenant_id,
            activity_id=activity.activity_id,
            entity_type="CUSTOMER",
            entity_id=customer.customer_id,
        )
    )
    db.add(
        ActivityType(
            tenant_id=tenant.tenant_id,
            code="SEEDTYPE",
            name="Seed Type",
        )
    )
    db.add(
        ActivityOutcome(
            tenant_id=tenant.tenant_id,
            activity_type_code="SEEDTYPE",
            code="OK",
            name="Seed Outcome",
        )
    )
    db.add(
        OpportunityStage(
            tenant_id=tenant.tenant_id,
            code="SEEDSTAGE",
            name="Seed Stage",
            sequence_no=99,
        )
    )
    db.flush()
    return {
        "tenant_id": tenant.tenant_id,
        "customer_id": customer.customer_id,
        "activity_id": activity.activity_id,
    }


# ------------------------------------------------------------------ API helpers


def _login(client: TestClient, email: str, password: str, tenant_code: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": tenant_code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _role_token(client: TestClient, role_code: str) -> str:
    """Create an ACTIVE user holding ``role_code`` in the seed tenant and log in."""
    email = f"crm011-{role_code.lower()}-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        assert role is not None, f"role {role_code} not seeded for the tenant"
        db.add(
            User(
                tenant_id=admin.tenant_id,
                organization_id=admin.organization_id,
                role_id=role.role_id,
                employee_code=f"R11{uuid.uuid4().hex[:6].upper()}",
                first_name="CRM011",
                last_name=role_code.title(),
                display_name=f"CRM011 {role_code}",
                email=email,
                password_hash=hash_password(USER_PASSWORD),
                account_status="ACTIVE",
            )
        )
        db.commit()
    return _login(client, email, USER_PASSWORD, "EIIP001")


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_active_customer(client: TestClient, token: str) -> str:
    """Create a customer and drive it PROSPECT -> ACTIVE (BR-CRM-043/044)."""
    headers = _auth(token)
    create = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"RLS Suspend {uuid.uuid4().hex[:8]}"},
    )
    assert create.status_code == 201, create.text
    cid = create.json()["customer_id"]

    contact = client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=headers,
        json={"first_name": "Primary", "is_primary": True},
    )
    assert contact.status_code == 201, contact.text
    address = client.post(
        f"/api/v1/crm/customers/{cid}/addresses",
        headers=headers,
        json={"address_type": "REGISTERED", "address_line1": "1 RLS Road"},
    )
    assert address.status_code == 201, address.text
    activate = client.patch(
        f"/api/v1/crm/customers/{cid}", headers=headers, json={"status": "ACTIVE"}
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"
    return cid


# ------------------------------------------------------- static / file checks


def test_migration_targets_exactly_the_ten_approved_tables():
    """Requirement 1 (scope): the migration applies to the 10 tables, in order."""
    sql = MIGRATION_PATH.read_text(encoding="utf-8")
    targets = tuple(re.findall(r"\(\s*'crm'\s*,\s*'(\w+)'\s*\)", sql))
    assert targets == CRM_RLS_TABLES
    for owned in PF003A_OWNED_TABLES:
        assert not re.search(rf"\(\s*'crm'\s*,\s*'{owned}'\s*\)", sql), (
            f"{owned} is owned by PF-003A and must not be a CRM-011 target"
        )


def test_migration_copies_the_pf003a_non_nullable_policy_verbatim():
    """The USING/WITH CHECK expression is the existing PF-003A one, not a new one."""
    pf003a_bodies = _policy_bodies(PF003A_PATH.read_text(encoding="utf-8"))
    non_nullable = [b for b in pf003a_bodies if "IS NOT NULL" not in b]
    assert len(non_nullable) == 1, "PF-003A non-nullable tenant policy not found"

    migration_bodies = _policy_bodies(MIGRATION_PATH.read_text(encoding="utf-8"))
    assert len(migration_bodies) == 1, "CRM-011 must define exactly one policy body"
    assert _norm(migration_bodies[0]) == _norm(non_nullable[0])


# ------------------------------------------------------------ requirement 1/2


def test_all_tables_have_forced_rls_and_the_tenant_isolation_policy(
    client: TestClient,
) -> None:
    """Requirement 1: ENABLE + FORCE RLS and exactly one PF-003A-shaped policy."""
    with platform_session() as db:
        assert _current_role(db) == "elu_app"
        for table in CRM_RLS_TABLES:
            assert _rls_flags(db, table) == (True, True), table
            policies = _policies(db, table)
            assert len(policies) == 1, (table, policies)
            name, permissive, cmd, qual, with_check = policies[0]
            assert name == "tenant_isolation", table
            assert permissive == "PERMISSIVE", table
            assert cmd == "ALL", table
            assert qual and with_check, (table, qual, with_check)
            for fragment in POLICY_FRAGMENTS:
                assert fragment in qual, (table, qual)
                assert fragment in with_check, (table, with_check)
            assert _norm(qual) == _norm(with_check), table


def test_pf003a_lead_and_opportunity_policies_are_unchanged(
    client: TestClient,
) -> None:
    """Requirement 2: 011 must not modify the PF-003A-owned policy surface."""
    with platform_session() as db:
        before = {
            table: (_rls_flags(db, table), _policies(db, table))
            for table in PF003A_OWNED_TABLES
        }
        for table in PF003A_OWNED_TABLES:
            assert before[table][1], f"PF-003A policy on crm.{table} is missing"
            assert before[table][1][0][0] == "tenant_isolation"

        _apply_migration_011(db)

        after = {
            table: (_rls_flags(db, table), _policies(db, table))
            for table in PF003A_OWNED_TABLES
        }
    assert after == before


# ------------------------------------------------------------------ requirement 3


def test_missing_tenant_context_fails_closed(
    client: TestClient, tenants: dict[str, dict]
) -> None:
    """Requirement 3: no tenant GUC and no platform context -> nothing is visible."""
    tenant_a = tenants["a"]
    with platform_session() as db:
        baselines = {table: _total_visible(db, table) for table in CRM_RLS_TABLES}

    with _rls_session() as db:
        assert _current_role(db) == "elu_app"
        for table in CRM_RLS_TABLES:
            assert _total_visible(db, table) == 0, table
            for key in ("a", "b"):
                assert _count_visible(db, table, tenants[key]["tenant_id"]) == 0, table

        # Writing is refused as well: the WITH CHECK half of the policy applies to
        # every CRM-011 table, not just ``customer``. Each statement runs inside its
        # own savepoint (``_expect_rls_violation``), so one expected 42501 cannot
        # abort the surrounding transaction or the remaining table probes.
        for table in CRM_RLS_TABLES:
            sql, params = _insert_spec(table, tenant_a["tenant_id"], tenant_a)
            _expect_rls_violation(db, sql, params)

    # The rejected INSERTs wrote nothing, on any of the ten tables.
    with platform_session() as db:
        for table in CRM_RLS_TABLES:
            assert _total_visible(db, table) == baselines[table], table

    # Non-vacuous: the same rows are visible once a tenant is bound.
    with _rls_session(tenant_id=tenant_a["tenant_id"]) as db:
        for table in CRM_RLS_TABLES:
            assert _count_visible(db, table, tenant_a["tenant_id"]) >= 1, table


# ------------------------------------------------------------- requirement 4/5/6


@pytest.mark.parametrize("table", CRM_RLS_TABLES)
def test_tenant_a_cannot_select_tenant_b_rows(
    client: TestClient, tenants: dict[str, dict], table: str
) -> None:
    """Requirement 4: B's rows are invisible inside A's RLS context."""
    tenant_a, tenant_b = tenants["a"], tenants["b"]
    with _rls_session(tenant_id=tenant_a["tenant_id"]) as db:
        assert _current_role(db) == "elu_app"
        assert _count_visible(db, table, tenant_b["tenant_id"]) == 0
        assert _count_visible(db, table, tenant_a["tenant_id"]) >= 1
    with platform_session() as db:
        assert _count_visible(db, table, tenant_b["tenant_id"]) >= 1


@pytest.mark.parametrize("table", CRM_RLS_TABLES)
def test_tenant_a_cannot_insert_a_tenant_b_row(
    client: TestClient, tenants: dict[str, dict], table: str
) -> None:
    """Requirement 5: the WITH CHECK clause rejects a foreign tenant_id."""
    tenant_b = tenants["b"]
    with platform_session() as db:
        baseline = _count_visible(db, table, tenant_b["tenant_id"])
    assert baseline >= 1, f"no fixture rows in crm.{table} - probe would be vacuous"

    with _rls_session(tenant_id=tenants["a"]["tenant_id"]) as db:
        assert _current_role(db) == "elu_app"
        sql, params = _insert_spec(table, tenant_b["tenant_id"], tenant_b)
        _expect_rls_violation(db, sql, params)

    with platform_session() as db:
        # Nothing was written: the rejected row must not exist.
        assert _count_visible(db, table, tenant_b["tenant_id"]) == baseline


@pytest.mark.parametrize("table", CRM_RLS_TABLES)
def test_tenant_a_cannot_update_or_delete_tenant_b_rows(
    client: TestClient, tenants: dict[str, dict], table: str
) -> None:
    """Requirement 6: UPDATE/DELETE invisibility, with the DML rolled back."""
    tenant_b = tenants["b"]["tenant_id"]
    with platform_session() as db:
        baseline = _count_visible(db, table, tenant_b)
    assert baseline >= 1, f"no fixture rows in crm.{table} - probe would be vacuous"

    with _rls_session(tenant_id=tenants["a"]["tenant_id"]) as db:
        assert _current_role(db) == "elu_app"
        # ``tenant_id = tenant_id`` keeps the statement harmless while the row
        # count still proves whether the rows were reachable at all.
        updated = _savepoint_rowcount(
            db,
            f"UPDATE {_qualified(table)} SET tenant_id = tenant_id WHERE tenant_id = :t",
            {"t": tenant_b},
        )
        assert updated == 0

        deleted = _savepoint_rowcount(
            db,
            f"DELETE FROM {_qualified(table)} WHERE tenant_id = :t",
            {"t": tenant_b},
        )
        assert deleted == 0

    with platform_session() as db:
        assert _count_visible(db, table, tenant_b) == baseline


# ------------------------------------------------------------------ requirement 7


def test_platform_context_retains_cross_tenant_visibility(
    client: TestClient, tenants: dict[str, dict]
) -> None:
    """Requirement 7: app.platform_context=true still sees every tenant."""
    with platform_session() as db:
        assert _current_role(db) == "elu_app"
        for table in CRM_RLS_TABLES:
            assert _count_visible(db, table, tenants["a"]["tenant_id"]) >= 1, table
            assert _count_visible(db, table, tenants["b"]["tenant_id"]) >= 1, table
            assert _total_visible(db, table) >= 2, table


# ------------------------------------------------------------------ requirement 8


def test_migration_is_idempotent(client: TestClient, tenants: dict[str, dict]) -> None:
    """Requirement 8: re-applying the migration changes neither policy nor data."""
    with platform_session() as db:
        before = {
            table: (_rls_flags(db, table), _policies(db, table))
            for table in CRM_RLS_TABLES
        }
        counts_before = {
            table: _count_visible(db, table, tenants["a"]["tenant_id"])
            for table in CRM_RLS_TABLES
        }

        _apply_migration_011(db)

        after = {
            table: (_rls_flags(db, table), _policies(db, table))
            for table in CRM_RLS_TABLES
        }
        counts_after = {
            table: _count_visible(db, table, tenants["a"]["tenant_id"])
            for table in CRM_RLS_TABLES
        }

    assert after == before
    assert counts_after == counts_before
    for table in CRM_RLS_TABLES:
        assert len(after[table][1]) == 1, f"duplicate policy created on {table}"

    # The runner-level applicator must be a no-op too (it re-runs 001-011).
    with platform_session() as db:
        apply_crm_ddl(db)
        for table in CRM_RLS_TABLES:
            assert _rls_flags(db, table) == (True, True), table
            assert len(_policies(db, table)) == 1, table


# ------------------------------------------------------------------ requirement 9


def test_lookup_lazy_seeding_runs_under_tenant_rls(
    client: TestClient, tenants: dict[str, dict]
) -> None:
    """Requirement 9: default lookups seed as elu_app inside one tenant only."""
    tenant_a = tenants["a"]["tenant_id"]

    with _rls_session(tenant_id=tenant_a) as db:
        assert _current_role(db) == "elu_app"
        CrmLookupService(db).ensure_tenant_defaults(tenant_a)

    with platform_session() as db:
        type_codes = set(
            db.scalars(
                select(ActivityType.code).where(ActivityType.tenant_id == tenant_a)
            ).all()
        )
        assert {"NOTE", "CALL", "MEETING", "EMAIL", "TASK", "SYSTEM"} <= type_codes

        stage_codes = set(
            db.scalars(
                select(OpportunityStage.code).where(
                    OpportunityStage.tenant_id == tenant_a
                )
            ).all()
        )
        assert "QUALIFICATION" in stage_codes

        outcomes = {
            (outcome.activity_type_code, outcome.code)
            for outcome in db.scalars(
                select(ActivityOutcome).where(ActivityOutcome.tenant_id == tenant_a)
            ).all()
        }
        assert ("CALL", "INTERESTED") in outcomes

    # A second call is a no-op: no duplicated default rows.
    with _rls_session(tenant_id=tenant_a) as db:
        CrmLookupService(db).ensure_tenant_defaults(tenant_a)
        duplicates = db.execute(
            text(
                "SELECT count(*) FROM crm.activity_type "
                "WHERE tenant_id = :t AND code = 'CALL'"
            ),
            {"t": tenant_a},
        ).scalar_one()
        assert duplicates == 1

    # The seeded rows stay tenant-scoped: tenant B cannot see them.
    with _rls_session(tenant_id=tenants["b"]["tenant_id"]) as db:
        assert _count_visible(db, "activity_type", tenant_a) == 0
        assert _count_visible(db, "opportunity_stage", tenant_a) == 0
        assert _count_visible(db, "activity_outcome", tenant_a) == 0
        assert (
            db.execute(
                text(
                    "SELECT count(*) FROM crm.activity_type "
                    "WHERE tenant_id = :t AND code = 'CALL'"
                ),
                {"t": tenant_a},
            ).scalar_one()
            == 0
        )


# ----------------------------------------------------------------- requirement 10


def test_finance_only_customer_suspension_with_history_and_audit(
    client: TestClient,
    admin_token: str,
    finance_user: str,
    sales_manager_user: str,
) -> None:
    """Requirement 10: suspension still works under RLS - history and audit too."""
    cid = _create_active_customer(client, admin_token)

    payload = {"reason_code": SUSPEND_REASON, "comment": SUSPEND_COMMENT}

    denied = client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        headers=_auth(sales_manager_user),
        json=payload,
    )
    assert denied.status_code == 403, denied.text

    accepted = client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        headers=_auth(finance_user),
        json=payload,
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["status"] == "SUSPENDED"

    with platform_session() as db:
        history = db.scalars(
            select(CustomerStatusHistory)
            .where(CustomerStatusHistory.customer_id == UUID(cid))
            .order_by(CustomerStatusHistory.changed_on)
        ).all()
        suspensions = [
            (row.from_status, row.to_status)
            for row in history
            if row.to_status == "SUSPENDED"
        ]
        assert suspensions == [("ACTIVE", "SUSPENDED")]

        events = db.scalars(
            select(AuditEvent).where(
                AuditEvent.entity_id == UUID(cid),
                AuditEvent.event_type == "customer.suspended",
            )
        ).all()
        assert len(events) == 1, "expected exactly one customer.suspended audit event"
        event = events[0]
        assert event.entity_type == "customer"
        assert event.tenant_id is not None
        audit_payload = json.loads(event.payload_json or "{}")
        assert audit_payload["to_status"] == "SUSPENDED"
        assert audit_payload["reason_code"] == SUSPEND_REASON
