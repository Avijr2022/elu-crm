"""PF-003A / ADR-015 tenant isolation suite (TC-PF-ISO-*)."""

from __future__ import annotations

import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password
from app.db.migrate_pf003a import RLS_TABLES, apply_pf003a_ddl, rls_enabled
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Branch, BranchAddress, Organization, Role, Tenant, User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf003a_ddl(db)
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()

    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.seed_admin_email,
            "password": settings.seed_admin_password,
            "tenant_code": "EIIP001",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def auth_header(platform_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {platform_token}"}


def _unique_code(prefix: str = "iso") -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def _register_and_approve(
    client: TestClient, auth_header: dict, code: str
) -> dict:
    create = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json={
            "code": code,
            "legal_name": f"Legal {code}",
            "trade_name": f"Trade {code}",
            "edition_code": "PROFESSIONAL",
            "email": f"{code}@example.com",
            "mobile": "9876543210",
            "primary_contact": {
                "contact_type": "PRIMARY",
                "name": "Primary Contact",
                "email": f"contact-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Isolation Street",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    apr = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=auth_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    return apr.json()


def _provision_tenant_admin(
    tenant_id: uuid.UUID, email: str, password: str
) -> uuid.UUID:
    """Create TENANT_ADMIN + org user under an existing tenant (platform session)."""
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        assert org is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == "TENANT_ADMIN"
            )
        ).first()
        if role is None:
            role = Role(
                tenant_id=tenant_id,
                role_code="TENANT_ADMIN",
                role_name="Tenant Admin",
                is_system=True,
            )
            db.add(role)
            db.flush()
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            employee_code=f"ISO{uuid.uuid4().hex[:6].upper()}",
            first_name="Iso",
            last_name="Admin",
            display_name="Iso Admin",
            email=email.lower(),
            password_hash=hash_password(password),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        return user.user_id


def _login_tenant(
    client: TestClient, email: str, password: str, tenant_code: str
) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": tenant_code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_migration_idempotent_and_rls_forced(client: TestClient) -> None:
    with platform_session() as db:
        apply_pf003a_ddl(db)
        apply_pf003a_ddl(db)
        for schema, table in RLS_TABLES:
            assert rls_enabled(db, schema, table), f"RLS not forced on {schema}.{table}"


def test_rls_blocks_without_context(client: TestClient) -> None:
    """Fail-closed: elu_app + empty GUCs → zero tenant rows (FORCE RLS)."""
    db = SessionLocal()
    try:
        clear_rls_context(db)
        # after_begin sets ROLE elu_app; leave tenant/platform GUCs empty.
        count = db.execute(text("SELECT count(*) FROM core.tenant")).scalar()
        assert count == 0
        lead_count = db.execute(text("SELECT count(*) FROM crm.lead")).scalar()
        assert lead_count == 0
    finally:
        clear_rls_context(db)
        db.close()


def test_rls_tenant_scope_sql(client: TestClient, auth_header: dict) -> None:
    a = _register_and_approve(client, auth_header, _unique_code("a"))
    b = _register_and_approve(client, auth_header, _unique_code("b"))
    tid_a = uuid.UUID(a["id"])
    tid_b = uuid.UUID(b["id"])

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tid_a, platform=False)
        rows = db.execute(text("SELECT tenant_id FROM core.tenant")).fetchall()
        assert len(rows) == 1
        assert rows[0][0] == tid_a

        bind_rls_context(db, tenant_id=tid_b, platform=False)
        rows_b = db.execute(text("SELECT tenant_id FROM core.tenant")).fetchall()
        assert len(rows_b) == 1
        assert rows_b[0][0] == tid_b
    finally:
        clear_rls_context(db)
        db.close()


def test_platform_context_bypass(client: TestClient, auth_header: dict) -> None:
    _register_and_approve(client, auth_header, _unique_code("p"))
    with platform_session() as db:
        count = db.execute(text("SELECT count(*) FROM core.tenant")).scalar()
        assert count >= 2  # Euphoria + at least one ISO tenant


def test_tc_pf_iso_04_platform_admin_list(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/platform/tenants", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["total"] >= 1


def test_tc_pf_iso_01_cross_tenant_profile_and_lead(
    client: TestClient, auth_header: dict
) -> None:
    code_a = _unique_code("ta")
    code_b = _unique_code("tb")
    tenant_a = _register_and_approve(client, auth_header, code_a)
    tenant_b = _register_and_approve(client, auth_header, code_b)
    tid_a = uuid.UUID(tenant_a["id"])
    tid_b = uuid.UUID(tenant_b["id"])

    pwd = "IsoTest!234"
    email_a = f"admin-{code_a}@example.com"
    email_b = f"admin-{code_b}@example.com"
    _provision_tenant_admin(tid_a, email_a, pwd)
    _provision_tenant_admin(tid_b, email_b, pwd)

    token_a = _login_tenant(client, email_a, pwd, code_a)
    token_b = _login_tenant(client, email_b, pwd, code_b)
    hdr_a = {"Authorization": f"Bearer {token_a}"}
    hdr_b = {"Authorization": f"Bearer {token_b}"}

    # Own profile OK
    own = client.get("/api/v1/tenant/profile", headers=hdr_a)
    assert own.status_code == 200
    assert own.json()["id"] == str(tid_a)

    # Platform cross-tenant read forbidden for Tenant Admin (not IDOR leak)
    cross = client.get(f"/api/v1/platform/tenants/{tid_b}", headers=hdr_a)
    assert cross.status_code == 403

    # CRM lead isolation: B creates lead; A cannot read by id → 404
    create_lead = client.post(
        "/api/v1/crm/leads",
        headers=hdr_b,
        json={"full_name": "Secret Lead B", "company_name": "B Corp"},
    )
    assert create_lead.status_code == 201, create_lead.text
    lead_id = create_lead.json()["lead_id"]

    stolen = client.get(f"/api/v1/crm/leads/{lead_id}", headers=hdr_a)
    assert stolen.status_code == 404, stolen.text

    ok = client.get(f"/api/v1/crm/leads/{lead_id}", headers=hdr_b)
    assert ok.status_code == 200
    assert ok.json()["tenant_id"] == str(tid_b)


def test_tc_pf_iso_02_foreign_tenant_id_ignored_on_lead(
    client: TestClient, auth_header: dict
) -> None:
    code = _unique_code("fx")
    tenant = _register_and_approve(client, auth_header, code)
    tid = uuid.UUID(tenant["id"])
    email = f"admin-{code}@example.com"
    pwd = "IsoTest!234"
    _provision_tenant_admin(tid, email, pwd)
    token = _login_tenant(client, email, pwd, code)
    hdr = {"Authorization": f"Bearer {token}"}

    foreign = str(uuid.uuid4())
    resp = client.post(
        "/api/v1/crm/leads",
        headers=hdr,
        json={
            "full_name": "No Spoof",
            "tenant_id": foreign,  # extra field — must be ignored by schema
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["tenant_id"] == str(tid)
    assert resp.json()["tenant_id"] != foreign


def test_tc_pf_iso_03_soft_deleted_user_invisible(
    client: TestClient, auth_header: dict
) -> None:
    code = _unique_code("sd")
    tenant = _register_and_approve(client, auth_header, code)
    tid = uuid.UUID(tenant["id"])
    email = f"admin-{code}@example.com"
    pwd = "IsoTest!234"
    user_id = _provision_tenant_admin(tid, email, pwd)

    with platform_session() as db:
        user = db.get(User, user_id)
        assert user is not None
        user.is_deleted = True
        user.is_active = False
        db.commit()

    # Login must fail for soft-deleted user (auth bootstrap sees row but status gate)
    # Repository get_by_email typically filters is_deleted — expect 401.
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": pwd, "tenant_code": code},
    )
    assert resp.status_code in (401, 403), resp.text

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tid, platform=False)
        visible = db.execute(
            text(
                "SELECT count(*) FROM core.users "
                "WHERE user_id = :uid AND COALESCE(is_deleted, false) = false"
            ),
            {"uid": user_id},
        ).scalar()
        assert visible == 0
    finally:
        clear_rls_context(db)
        db.close()


def test_jwt_tenant_spoof_rejected(client: TestClient, auth_header: dict) -> None:
    code_a = _unique_code("ja")
    code_b = _unique_code("jb")
    tenant_a = _register_and_approve(client, auth_header, code_a)
    tenant_b = _register_and_approve(client, auth_header, code_b)
    tid_a = uuid.UUID(tenant_a["id"])
    tid_b = uuid.UUID(tenant_b["id"])
    email = f"admin-{code_a}@example.com"
    pwd = "IsoTest!234"
    user_id = _provision_tenant_admin(tid_a, email, pwd)

    spoof = create_access_token(
        user_id=user_id,
        tenant_id=tid_b,  # claim B while user belongs to A
        email=email,
        role_code="TENANT_ADMIN",
    )
    resp = client.get(
        "/api/v1/tenant/profile",
        headers={"Authorization": f"Bearer {spoof}"},
    )
    assert resp.status_code == 401, resp.text


def test_set_local_guc_visible_in_session(client: TestClient) -> None:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        tid = admin.tenant_id

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tid, platform=False)
        guc = db.execute(
            text("SELECT current_setting('app.tenant_id', true)")
        ).scalar()
        assert guc == str(tid)
        pc = db.execute(
            text("SELECT current_setting('app.platform_context', true)")
        ).scalar()
        assert pc in ("", None)
    finally:
        clear_rls_context(db)
        db.close()


def test_edition_tables_have_no_rls(client: TestClient) -> None:
    with platform_session() as db:
        for table in ("edition", "feature_catalogue", "permission"):
            row = db.execute(
                text(
                    """
                    SELECT c.relrowsecurity
                    FROM pg_class c
                    JOIN pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = 'core' AND c.relname = :t
                    """
                ),
                {"t": table},
            ).first()
            assert row is not None
            assert row[0] is False


def test_pf004_cross_tenant_organization_get(
    client: TestClient, auth_header: dict
) -> None:
    """Tenant A cannot GET Tenant B organization by id (404)."""
    code_a = _unique_code("oa")
    code_b = _unique_code("ob")
    tenant_a = _register_and_approve(client, auth_header, code_a)
    tenant_b = _register_and_approve(client, auth_header, code_b)
    tid_a = uuid.UUID(tenant_a["id"])
    tid_b = uuid.UUID(tenant_b["id"])
    pwd = "IsoTest!234"
    email_a = f"admin-{code_a}@example.com"
    email_b = f"admin-{code_b}@example.com"
    _provision_tenant_admin(tid_a, email_a, pwd)
    _provision_tenant_admin(tid_b, email_b, pwd)
    hdr_a = {
        "Authorization": f"Bearer {_login_tenant(client, email_a, pwd, code_a)}"
    }
    hdr_b = {
        "Authorization": f"Bearer {_login_tenant(client, email_b, pwd, code_b)}"
    }

    root_b = client.get("/api/v1/org/organizations/root", headers=hdr_b)
    assert root_b.status_code == 200, root_b.text
    org_b_id = root_b.json()["id"]

    stolen = client.get(f"/api/v1/org/organizations/{org_b_id}", headers=hdr_a)
    assert stolen.status_code == 404, stolen.text

    own = client.get(f"/api/v1/org/organizations/{org_b_id}", headers=hdr_b)
    assert own.status_code == 200, own.text


def test_tc_pf_iso_05_branch_cross_tenant(
    client: TestClient, auth_header: dict
) -> None:
    """TC-PF-ISO-05 (ADR-015): branch / branch_address never cross tenants."""
    code_a = _unique_code("ba")
    code_b = _unique_code("bb")
    tenant_a = _register_and_approve(client, auth_header, code_a)
    tenant_b = _register_and_approve(client, auth_header, code_b)
    tid_a = uuid.UUID(tenant_a["id"])
    tid_b = uuid.UUID(tenant_b["id"])
    pwd = "IsoTest!234"
    email_a = f"admin-{code_a}@example.com"
    email_b = f"admin-{code_b}@example.com"
    _provision_tenant_admin(tid_a, email_a, pwd)
    _provision_tenant_admin(tid_b, email_b, pwd)
    hdr_a = {"Authorization": f"Bearer {_login_tenant(client, email_a, pwd, code_a)}"}
    hdr_b = {"Authorization": f"Bearer {_login_tenant(client, email_b, pwd, code_b)}"}

    # Tenant B owns one branch (with address)
    org_b = client.get("/api/v1/org/organizations/root", headers=hdr_b)
    assert org_b.status_code == 200, org_b.text
    created = client.post(
        "/api/v1/org/branches",
        headers=hdr_b,
        json={
            "code": "ISOB-01",
            "name": "Iso Branch B",
            "branch_type": "HEAD_OFFICE",
            "organization_id": org_b.json()["id"],
            "status": "ACTIVE",
            "address": {
                "address_line_1": "1 Isolation Street",
                "city": "Kolkata",
                "country_code": "IN",
            },
        },
    )
    assert created.status_code == 201, created.text
    branch_id = created.json()["id"]
    version_no = created.json()["version_no"]

    # Tenant A cannot read, mutate or delete tenant B's branch (404, not a leak)
    assert client.get(f"/api/v1/org/branches/{branch_id}", headers=hdr_a).status_code == 404
    assert (
        client.patch(
            f"/api/v1/org/branches/{branch_id}",
            headers=hdr_a,
            json={"name": "Stolen", "version_no": version_no},
        ).status_code
        == 404
    )
    assert client.delete(f"/api/v1/org/branches/{branch_id}", headers=hdr_a).status_code == 404

    # Tenant A's list never contains tenant B's branch
    listing_a = client.get("/api/v1/org/branches", headers=hdr_a)
    assert listing_a.status_code == 200, listing_a.text
    assert all(i["id"] != branch_id for i in listing_a.json()["items"])

    # Tenant A cannot attach tenant B's organization to its own branch
    foreign_org = client.post(
        "/api/v1/org/branches",
        headers=hdr_a,
        json={
            "code": "ISOA-01",
            "name": "Iso Branch A",
            "branch_type": "BRANCH",
            "organization_id": org_b.json()["id"],
        },
    )
    assert foreign_org.status_code == 404, foreign_org.text

    # RLS evidence: tenant A's SQL context sees neither B's branch nor its address,
    # while tenant B's context sees both.
    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tid_a, platform=False)
        assert (
            db.execute(
                text("SELECT count(*) FROM core.branch WHERE branch_id = :b"),
                {"b": branch_id},
            ).scalar()
            == 0
        )
        assert (
            db.execute(
                text("SELECT count(*) FROM core.branch_address WHERE tenant_id = :t"),
                {"t": tid_b},
            ).scalar()
            == 0
        )

        bind_rls_context(db, tenant_id=tid_b, platform=False)
        assert (
            db.execute(
                text("SELECT count(*) FROM core.branch WHERE branch_id = :b"),
                {"b": branch_id},
            ).scalar()
            == 1
        )
        assert (
            db.execute(
                text("SELECT count(*) FROM core.branch_address WHERE tenant_id = :t"),
                {"t": tid_b},
            ).scalar()
            == 1
        )
    finally:
        clear_rls_context(db)
        db.close()

    with platform_session() as db:
        rows = db.scalars(
            select(Branch).where(Branch.tenant_id == tid_b, Branch.branch_code == "ISOB-01")
        ).all()
        assert len(rows) == 1
        addresses = db.scalars(
            select(BranchAddress).where(BranchAddress.tenant_id == tid_b)
        ).all()
        assert len(addresses) == 1
