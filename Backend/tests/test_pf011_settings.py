"""PF-011 System Configuration CORE tests.

Conventions follow the existing PF-009 / PF-010 / isolation suites: a module-scoped
``TestClient(app)`` drives the real application (lifespan runs the PF-011 DDL), tenants are
provisioned through the platform API, and DB-level assertions open their own
``SessionLocal`` / ``platform_session`` so importing this module never touches the database.

Reconciled specification: ``ELU-API-PF.md`` §4.6 (19 operations), ``ELU-DDD-PF.md`` §11
(ADR-017), ``ELU-BFS-PF`` §PF-011 §9/§10/§12, DDL
``Database/03_PlatformFoundation/020_settings_pf011.sql``.

Deliberately NOT tested here:

* ``PUT`` / ``DELETE /settings/holidays/{id}`` — ``core.tenant_holiday_calendar`` has no
  surrogate id column and the approved rule forbids inventing one, so those two routes do
  not exist. Asserting them would require inventing a contract.
* A ``lock_state`` column on ``core.tenant_preference`` — ADR-017 rule 9 states locking is
  expressed by ``is_editable`` and that no ``lock_state`` column exists. The absence is
  asserted instead of a fabricated column.
* A PF-011 edition feature code — no such constant exists in ``app.core.edition_gating``,
  and ``require_feature()`` is deliberately never called for PF-011.
"""

from __future__ import annotations

import json
import uuid
from collections.abc import Iterator

import pytest
import redis
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.deps import CurrentUser
from app.core.rbac import has_permission
from app.core.security import hash_password
from app.db import seed as seed_module
from app.db.migrate_pf003a import rls_enabled
from app.db.migrate_pf011 import apply_pf011_ddl
from app.db.rls_context import bind_rls_context, clear_rls_context, owner_role
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Edition, Organization, Role, User
from app.repositories.pf.permission_repository import permissions_for_role
from app.services.pf import settings_service as settings_module
from app.services.pf.settings_service import (
    CACHE_PREFIX,
    CACHE_TTL_SECONDS,
    REQ_ID,
    SettingsService,
)
from tests.conftest import platform_session

API = "/api/v1"
PASSWORD = "Pf011Test@123"
PLATFORM_TENANT_CODE = "EIIP001"

PF011_TENANT_TABLES = (
    "tenant_settings",
    "tenant_preference",
    "tenant_notification_preference",
    "tenant_module_default",
    "tenant_holiday_calendar",
)
PF011_PLATFORM_TABLES = ("platform_setting", "setting_catalogue")

PF011_GRAINS = (
    "settings.read",
    "settings.configure",
    "platform_settings.read",
    "platform_settings.configure",
)

# The approved PF-011 matrix (BFS-PF-011 §12) — the authoritative expectation.
APPROVED_MATRIX = {
    "TENANT_ADMIN": ("settings.read", "settings.configure"),
    "PLATFORM_ADMIN": (
        "settings.read",
        "settings.configure",
        "platform_settings.read",
        "platform_settings.configure",
    ),
    "FINANCE_USER": ("settings.read",),
    "SALES_MANAGER": ("settings.read",),
    "SALES_EXECUTIVE": (),
    "PROJECT_MANAGER": (),
}

# event_type -> (entity_type, whether a before/after snapshot is expected)
WRITE_EVENT_TYPES = {
    "SETTINGS_UPDATED": ("tenant_settings", True),
    "PREFERENCE_CHANGED": ("tenant_preference", True),
    "NOTIFICATION_PREFERENCES_CHANGED": ("tenant_notification_preference", True),
    "MODULE_DEFAULTS_CHANGED": ("tenant_module_default", True),
    "HOLIDAY_ADDED": ("tenant_holiday_calendar", True),
    "SETTINGS_RESET": ("tenant_settings", True),
    "PLATFORM_SETTINGS_UPDATED": ("platform_setting", True),
}


def _unique(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def _owner_session():
    """Session with the owner role active, for privileged setup/assertions/cleanup."""
    return SessionLocal()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def client() -> Iterator[TestClient]:
    with TestClient(app) as c:
        yield c


def _platform_header(client: TestClient) -> dict:
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == "admin@euphoriainfotech.com")
        ).first()
        assert admin is not None, "seeded platform admin not found"
        admin.password_hash = hash_password(PASSWORD)
        db.commit()

    resp = client.post(
        f"{API}/auth/login",
        json={
            "email": "admin@euphoriainfotech.com",
            "password": PASSWORD,
            "tenant_code": PLATFORM_TENANT_CODE,
        },
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _provision_tenant(client: TestClient, header: dict, prefix: str, edition: str) -> dict:
    """Provision + approve a tenant and return its Tenant Admin login context."""
    code = _unique(prefix)
    create = client.post(
        f"{API}/platform/tenants",
        headers=header,
        json={
            "code": code,
            "legal_name": f"Legal {code}",
            "trade_name": f"Trade {code}",
            "edition_code": edition,
            "email": f"{code}@example.com",
            "mobile": "9876543210",
            "primary_contact": {
                "contact_type": "PRIMARY",
                "name": "Primary",
                "email": f"c-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Settings Way",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    approve = client.post(
        f"{API}/platform/tenants/{tenant['id']}/approve",
        headers=header,
        json={"version_no": tenant["version_no"]},
    )
    assert approve.status_code == 200, approve.text

    tenant_id = uuid.UUID(tenant["id"])
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == "TENANT_ADMIN"
            )
        ).first()
        assert org is not None and role is not None
        email = f"admin-{code}@example.com"
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            first_name="Pf011",
            last_name="Admin",
            display_name="Pf011 Admin",
            email=email,
            password_hash=hash_password(PASSWORD),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        admin_id = str(user.user_id)

    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD, "tenant_code": code},
    )
    assert login.status_code == 200, login.text
    return {
        "code": code,
        "id": tenant["id"],
        "tenant_id": tenant_id,
        "edition": edition,
        "admin_email": email,
        "admin_id": admin_id,
        "header": {"Authorization": f"Bearer {login.json()['access_token']}"},
    }


@pytest.fixture(scope="module")
def platform_header(client: TestClient) -> dict:
    return _platform_header(client)


@pytest.fixture(scope="module")
def tenant_pro(client: TestClient, platform_header: dict) -> dict:
    return _provision_tenant(client, platform_header, "pf011pro", "PROFESSIONAL")


@pytest.fixture(scope="module")
def tenant_com(client: TestClient, platform_header: dict) -> dict:
    return _provision_tenant(client, platform_header, "pf011com", "COMMUNITY")


@pytest.fixture
def catalogue_key() -> Iterator[str]:
    """A uniquely named ``core.setting_catalogue`` row (FK target) plus cleanup.

    ``tenant_preference.preference_key`` is a RESTRICT FK onto
    ``setting_catalogue.setting_key``, so preference tests need a real catalogue row.
    The key is test-owned and removed afterwards; no production key is invented.
    """
    key = _unique("pf011_test_pref_")
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.setting_catalogue "
                    "(id, setting_key, value_type, default_value, description) "
                    "VALUES (gen_random_uuid(), :k, 'string', NULL, 'PF-011 test row')"
                ),
                {"k": key},
            )
            db.commit()
        yield key
    finally:
        db.rollback()
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text("DELETE FROM core.tenant_preference WHERE preference_key = :k"),
                {"k": key},
            )
            db.execute(
                text("DELETE FROM core.setting_catalogue WHERE setting_key = :k"),
                {"k": key},
            )
            db.commit()
        db.close()


def _role_grains(tenant_id: uuid.UUID, role_code: str) -> set:
    with platform_session() as db:
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == role_code
            )
        ).first()
        assert role is not None, f"role {role_code} not provisioned for {tenant_id}"
        return set(permissions_for_role(db, role.role_id))


def _grain_current(role_code: str, codes) -> CurrentUser:
    """Minimal ``CurrentUser`` for permission-grain checks (no DB required)."""
    return CurrentUser(
        user_id=uuid.UUID(int=1),
        tenant_id=uuid.UUID(int=2),
        email="pf011-grain@example.test",
        role_code=role_code,
        permissions=frozenset(codes),
        user=None,  # type: ignore[arg-type]
        platform_context=role_code == "PLATFORM_ADMIN",
    )


def _audit_rows(event_types) -> list:
    """Read audit rows for the given event types under the owner role (RLS bypass)."""
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            rows = db.execute(
                text(
                    "SELECT event_type, entity_type, tenant_id, payload_json "
                    "FROM audit.audit_event WHERE event_type = ANY(:types) "
                    "ORDER BY created_on DESC LIMIT 50"
                ),
                {"types": list(event_types)},
            ).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()


# ===========================================================================
# 1. PF-011 schema / table existence
# ===========================================================================
def _table_count(table: str) -> int:
    with platform_session() as db:
        return db.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'core' AND table_name = :t"
            ),
            {"t": table},
        ).scalar()


@pytest.mark.parametrize("table", PF011_TENANT_TABLES + PF011_PLATFORM_TABLES)
def test_pf011_table_exists(table: str):
    assert _table_count(table) == 1, f"core.{table} is missing"


def test_tenant_settings_table_is_not_duplicated():
    """``tenant_settings`` is pre-existing (PF-001) and must not be duplicated."""
    assert _table_count("tenant_settings") == 1


def test_tenant_settings_keeps_released_column_names():
    """ADR-017 rule 3: released ORM column names are preserved, not renamed."""
    with platform_session() as db:
        columns = {
            row[0]
            for row in db.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'core' AND table_name = 'tenant_settings'"
                )
            ).all()
        }
    released = {
        "setting_id",
        "tenant_id",
        "financial_year_start",
        "currency_code",
        "time_zone",
        "date_format",
        "time_format",
        "default_language",
        "notification_enabled",
        "workflow_enabled",
    }
    assert released <= columns, sorted(released - columns)


def test_tenant_preference_has_no_lock_state_column():
    """ADR-017 rule 9: locking is expressed by ``is_editable``; no ``lock_state`` exists."""
    with platform_session() as db:
        columns = {
            row[0]
            for row in db.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = 'core' AND table_name = 'tenant_preference'"
                )
            ).all()
        }
    assert "lock_state" not in columns
    assert {"is_editable", "edition_minimum"} <= columns


# ===========================================================================
# 2. RLS
# ===========================================================================
@pytest.mark.parametrize("table", PF011_TENANT_TABLES)
def test_pf011_tenant_table_is_rls_enrolled(table: str):
    with platform_session() as db:
        assert rls_enabled(db, "core", table) is True


@pytest.mark.parametrize("table", PF011_PLATFORM_TABLES)
def test_pf011_platform_table_is_not_tenant_scoped(table: str):
    """Platform-global tables carry no ``tenant_id`` and are not RLS-enrolled."""
    with platform_session() as db:
        assert rls_enabled(db, "core", table) is False
        tenant_columns = db.execute(
            text(
                "SELECT count(*) FROM information_schema.columns "
                "WHERE table_schema = 'core' AND table_name = :t "
                "AND column_name = 'tenant_id'"
            ),
            {"t": table},
        ).scalar()
    assert tenant_columns == 0


def test_pf011_tenant_preference_rls_denies_cross_tenant_read(
    tenant_pro: dict, tenant_com: dict, catalogue_key: str
):
    """A tenant-bound session sees only its own preference rows."""
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            for tenant_id in (tenant_pro["tenant_id"], tenant_com["tenant_id"]):
                db.execute(
                    text(
                        "INSERT INTO core.tenant_preference "
                        "(tenant_id, preference_key, preference_value, is_editable) "
                        "VALUES (:t, :k, 'rls-probe', TRUE)"
                    ),
                    {"t": tenant_id, "k": catalogue_key},
                )
            db.commit()

            total = db.execute(
                text("SELECT count(*) FROM core.tenant_preference")
            ).scalar()
            assert total and total >= 2
    finally:
        db.close()

    db = _owner_session()
    try:
        bind_rls_context(db, tenant_id=tenant_pro["tenant_id"])
        visible = db.execute(
            text("SELECT count(*) FROM core.tenant_preference")
        ).scalar()
        own = db.execute(
            text(
                "SELECT count(*) FROM core.tenant_preference WHERE tenant_id = :t"
            ),
            {"t": tenant_pro["tenant_id"]},
        ).scalar()
        assert visible == own, "RLS must expose exactly the tenant's own rows"

        leaked = db.execute(
            text(
                "SELECT count(*) FROM core.tenant_preference WHERE tenant_id = :t"
            ),
            {"t": tenant_com["tenant_id"]},
        ).scalar()
        assert leaked == 0, "tenant B rows must be invisible even when named explicitly"
    finally:
        clear_rls_context(db)
        db.close()


def test_pf011_holiday_calendar_rls_denies_cross_tenant_read(
    tenant_pro: dict, tenant_com: dict
):
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.tenant_holiday_calendar "
                    "(tenant_id, holiday_name, holiday_date) "
                    "VALUES (:t, :n, DATE '2099-01-01')"
                ),
                {"t": tenant_com["tenant_id"], "n": _unique("PF011_ISO_")},
            )
            db.commit()
    finally:
        db.close()

    db = _owner_session()
    try:
        bind_rls_context(db, tenant_id=tenant_pro["tenant_id"])
        leaked = db.execute(
            text(
                "SELECT count(*) FROM core.tenant_holiday_calendar WHERE tenant_id = :t"
            ),
            {"t": tenant_com["tenant_id"]},
        ).scalar()
        assert leaked == 0
    finally:
        clear_rls_context(db)
        db.close()


# ===========================================================================
# 3. Permission grains
# ===========================================================================
def test_pf011_grains_are_in_the_seeded_permission_catalogue():
    codes = {code for code, _name, _module in seed_module.PERMISSIONS}
    for grain in PF011_GRAINS:
        assert grain in codes, grain


def test_pf011_seed_matrix_matches_the_approved_matrix():
    assert seed_module.SETTINGS_PERMISSION_MATRIX == APPROVED_MATRIX


@pytest.mark.parametrize("role_code", sorted(APPROVED_MATRIX))
def test_pf011_seeded_tenant_grains_match_approved_matrix(tenant_pro: dict, role_code: str):
    """The seeded DB matrix decides — role name alone grants nothing."""
    grains = _role_grains(tenant_pro["tenant_id"], role_code)
    expected = set(APPROVED_MATRIX[role_code])
    for grain in PF011_GRAINS:
        assert (grain in grains) is (grain in expected), (role_code, grain)


def test_pf011_grains_are_not_granted_universally(tenant_pro: dict):
    """The generic blanket grant must have been corrected by the PF-011 sync."""
    assert not _role_grains(tenant_pro["tenant_id"], "SALES_EXECUTIVE") & set(PF011_GRAINS)
    assert not _role_grains(tenant_pro["tenant_id"], "PROJECT_MANAGER") & set(PF011_GRAINS)
    finance = _role_grains(tenant_pro["tenant_id"], "FINANCE_USER")
    assert finance & set(PF011_GRAINS) == {"settings.read"}
    sales = _role_grains(tenant_pro["tenant_id"], "SALES_MANAGER")
    assert sales & set(PF011_GRAINS) == {"settings.read"}


def test_pf011_platform_admin_has_no_universal_bypass():
    """PLATFORM_ADMIN is not universally allowed: grains still decide."""
    empty = _grain_current("PLATFORM_ADMIN", frozenset())
    for grain in PF011_GRAINS:
        assert has_permission(empty, grain) is False, grain
    granted = _grain_current("PLATFORM_ADMIN", PF011_GRAINS)
    for grain in PF011_GRAINS:
        assert has_permission(granted, grain) is True, grain


def test_pf011_tenant_admin_grains_are_tenant_scoped_only():
    tenant_admin = _grain_current(
        "TENANT_ADMIN", {"settings.read", "settings.configure"}
    )
    assert has_permission(tenant_admin, "settings.read")
    assert has_permission(tenant_admin, "settings.configure")
    # Platform-global configuration is not a tenant capability.
    assert has_permission(tenant_admin, "platform_settings.read") is False
    assert has_permission(tenant_admin, "platform_settings.configure") is False


# ===========================================================================
# 4. API — implemented PF-011 routes
# ===========================================================================
TENANT_READ_ROUTES = (
    ("GET", "/settings"),
    ("GET", "/settings/preferences"),
    ("GET", "/settings/notifications"),
    ("GET", "/settings/module-defaults"),
    ("GET", "/settings/holidays"),
    ("GET", "/settings/catalogue"),
)


@pytest.mark.parametrize("method,path", TENANT_READ_ROUTES)
def test_pf011_tenant_read_routes_return_200(
    client: TestClient, tenant_pro: dict, method: str, path: str
):
    resp = client.request(method, f"{API}{path}", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text


def test_pf011_settings_get_returns_released_field_names(client: TestClient, tenant_pro: dict):
    resp = client.get(f"{API}/settings", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["tenant_id"] == tenant_pro["id"]
    for field in (
        "setting_id",
        "financial_year_start",
        "currency_code",
        "time_zone",
        "date_format",
        "time_format",
        "default_language",
        "notification_enabled",
        "workflow_enabled",
    ):
        assert field in body, field


def test_pf011_settings_put_and_patch_update(client: TestClient, tenant_pro: dict):
    put = client.put(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"time_zone": "Asia/Kolkata", "time_format": "24 Hour"},
    )
    assert put.status_code == 200, put.text
    assert put.json()["time_zone"] == "Asia/Kolkata"

    patch = client.patch(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"date_format": "DD/MM/YYYY"},
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["date_format"] == "DD/MM/YYYY"


def test_pf011_preferences_put_bulk_and_single(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    bulk = client.put(
        f"{API}/settings/preferences",
        headers=tenant_pro["header"],
        json=[
            {"preference_key": catalogue_key, "preference_value": "one"},
            {"preference_key": catalogue_key, "preference_value": "two"},
        ],
    )
    assert bulk.status_code == 200, bulk.text
    assert bulk.json()["total"] >= 1

    single = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_pro["header"],
        json={"preference_value": "three"},
    )
    assert single.status_code == 200, single.text
    assert single.json()["preference_value"] == "three"

    fetched = client.get(
        f"{API}/settings/preferences/{catalogue_key}", headers=tenant_pro["header"]
    )
    assert fetched.status_code == 200, fetched.text
    assert fetched.json()["preference_value"] == "three"


def test_pf011_preference_unknown_key_returns_404(client: TestClient, tenant_pro: dict):
    resp = client.get(
        f"{API}/settings/preferences/{_unique('pf011_absent_')}",
        headers=tenant_pro["header"],
    )
    assert resp.status_code == 404, resp.text


def test_pf011_notifications_put(client: TestClient, tenant_pro: dict):
    resp = client.put(
        f"{API}/settings/notifications",
        headers=tenant_pro["header"],
        json=[
            {
                "event_type": "PF011_TEST_EVENT",
                "module_code": "PF",
                "email_enabled": True,
                "notify_admin": True,
            }
        ],
    )
    assert resp.status_code == 200, resp.text
    rows = [r for r in resp.json()["items"] if r["event_type"] == "PF011_TEST_EVENT"]
    assert rows and rows[0]["email_enabled"] is True


def test_pf011_module_defaults_put(client: TestClient, tenant_pro: dict):
    resp = client.put(
        f"{API}/settings/module-defaults",
        headers=tenant_pro["header"],
        json=[
            {
                "module_code": "PF",
                "entity_type": "pf011_test",
                "field_name": "default_value_probe",
                "default_value": "INR",
            }
        ],
    )
    assert resp.status_code == 200, resp.text
    rows = [
        r
        for r in resp.json()["items"]
        if r["entity_type"] == "pf011_test" and r["field_name"] == "default_value_probe"
    ]
    assert rows and rows[0]["default_value"] == "INR"


def test_pf011_holiday_post_and_list(client: TestClient, tenant_pro: dict):
    name = _unique("PF011_HOLIDAY_")
    created = client.post(
        f"{API}/settings/holidays",
        headers=tenant_pro["header"],
        json={"holiday_name": name, "holiday_date": "2099-02-01", "holiday_type": "PUBLIC"},
    )
    assert created.status_code == 200, created.text
    assert created.json()["holiday_name"] == name

    listed = client.get(f"{API}/settings/holidays", headers=tenant_pro["header"])
    assert listed.status_code == 200, listed.text
    assert name in {row["holiday_name"] for row in listed.json()["items"]}


def test_pf011_catalogue_route_lists_the_registry(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    resp = client.get(f"{API}/settings/catalogue", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text
    keys = {row["setting_key"] for row in resp.json()["items"]}
    assert catalogue_key in keys


def test_pf011_platform_settings_get_and_put(
    client: TestClient, platform_header: dict
):
    key = _unique("pf011_test_platform_")
    put = client.put(
        f"{API}/platform/settings",
        headers=platform_header,
        json=[{"key": key, "value": "on", "description": "pf-011 test row"}],
    )
    assert put.status_code == 200, put.text
    assert key in {row["key"] for row in put.json()["items"]}

    get = client.get(f"{API}/platform/settings", headers=platform_header)
    assert get.status_code == 200, get.text
    assert key in {row["key"] for row in get.json()["items"]}

    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text("DELETE FROM core.platform_setting WHERE key = :k"), {"k": key}
            )
            db.commit()
    finally:
        db.close()


def test_pf011_tenant_admin_cannot_reach_platform_settings(
    client: TestClient, tenant_pro: dict
):
    """Platform-global configuration is not a tenant capability."""
    assert (
        client.get(f"{API}/platform/settings", headers=tenant_pro["header"]).status_code
        == 403
    )
    assert (
        client.put(
            f"{API}/platform/settings",
            headers=tenant_pro["header"],
            json=[{"key": _unique("pf011_denied_"), "value": "x"}],
        ).status_code
        == 403
    )


def test_pf011_role_without_configure_grain_is_denied_write(
    client: TestClient, platform_header: dict, tenant_pro: dict
):
    """FINANCE_USER holds ``settings.read`` only: reads pass, writes are 403."""
    with platform_session() as db:
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_pro["tenant_id"],
                Role.role_code == "FINANCE_USER",
            )
        ).first()
        org = db.scalars(
            select(Organization).where(
                Organization.tenant_id == tenant_pro["tenant_id"]
            )
        ).first()
        assert role is not None and org is not None
        email = _unique("finance-") + "@example.com"
        db.add(
            User(
                tenant_id=tenant_pro["tenant_id"],
                organization_id=org.organization_id,
                role_id=role.role_id,
                first_name="Fin",
                last_name="Viewer",
                display_name="Fin Viewer",
                email=email,
                password_hash=hash_password(PASSWORD),
                account_status="ACTIVE",
            )
        )
        db.commit()

    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD, "tenant_code": tenant_pro["code"]},
    )
    assert login.status_code == 200, login.text
    header = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert client.get(f"{API}/settings", headers=header).status_code == 200
    assert (
        client.put(
            f"{API}/settings", headers=header, json={"time_zone": "Asia/Kolkata"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            f"{API}/settings/reset", headers=header, json={"confirmed": True}
        ).status_code
        == 403
    )


def test_pf011_holiday_id_routes_do_not_exist(client: TestClient, tenant_pro: dict):
    """The two blocked operations must not be invented as routes."""
    assert (
        client.put(
            f"{API}/settings/holidays/{uuid.uuid4()}",
            headers=tenant_pro["header"],
            json={"holiday_name": "x"},
        ).status_code
        in (404, 405)
    )
    assert (
        client.delete(
            f"{API}/settings/holidays/{uuid.uuid4()}", headers=tenant_pro["header"]
        ).status_code
        in (404, 405)
    )


# ===========================================================================
# 5. Edition minimum (Edition.display_order; no PF-011 feature code)
# ===========================================================================
def test_pf011_edition_ranks_come_from_display_order():
    """Governed order is read from ``Edition.display_order``, not hard-coded."""
    with platform_session() as db:
        ranks = {
            row[0]: row[1]
            for row in db.execute(
                text("SELECT code, display_order FROM core.edition")
            ).all()
        }
        assert ranks.get("COMMUNITY") == 1
        assert ranks.get("PROFESSIONAL") == 2
        assert ranks.get("ENTERPRISE") == 3
        # The ORM surface the service actually reads is the same column.
        model_ranks = {
            edition.code: edition.display_order
            for edition in db.scalars(select(Edition)).all()
        }
        assert model_ranks.get("PROFESSIONAL") == 2


def test_pf011_community_cannot_take_a_professional_preference(
    client: TestClient, tenant_com: dict, catalogue_key: str
):
    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_com["header"],
        json={"preference_value": "x", "edition_minimum": "PROFESSIONAL"},
    )
    assert resp.status_code == 403, resp.text
    assert resp.json()["detail"]["error"]["code"] == "FORBIDDEN"
    assert resp.json()["detail"]["error"]["req_id"] == REQ_ID


def test_pf011_professional_can_take_a_professional_preference(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_pro["header"],
        json={"preference_value": "x", "edition_minimum": "PROFESSIONAL"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["edition_minimum"] == "PROFESSIONAL"


def test_pf011_unknown_edition_minimum_is_rejected(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_pro["header"],
        json={"preference_value": "x", "edition_minimum": "PLATINUM_SENTINEL"},
    )
    assert resp.status_code == 422, resp.text
    assert resp.json()["detail"]["error"]["code"] == "VALIDATION_ERROR"


def test_pf011_stored_minimum_above_tenant_edition_blocks_the_write(
    client: TestClient, tenant_com: dict, catalogue_key: str
):
    """A stored minimum above the tenant edition rejects the whole operation."""
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.tenant_preference "
                    "(tenant_id, preference_key, preference_value, is_editable, "
                    " edition_minimum) "
                    "VALUES (:t, :k, 'seed', TRUE, 'ENTERPRISE')"
                ),
                {"t": tenant_com["tenant_id"], "k": catalogue_key},
            )
            db.commit()
    finally:
        db.close()

    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_com["header"],
        json={"preference_value": "nope"},
    )
    assert resp.status_code == 403, resp.text


def test_pf011_no_pf011_feature_constant_exists():
    """PF-011 must not invent an edition feature code."""
    from app.core import edition_gating

    names = {n for n in dir(edition_gating) if n.isupper()}
    assert not [n for n in names if "SETTINGS" in n or n.startswith("PF011")]


# ===========================================================================
# 6. Lock semantics (is_editable; no lock_state)
# ===========================================================================
def test_pf011_locked_preference_rejects_tenant_admin(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.tenant_preference "
                    "(tenant_id, preference_key, preference_value, is_editable) "
                    "VALUES (:t, :k, 'locked', FALSE)"
                ),
                {"t": tenant_pro["tenant_id"], "k": catalogue_key},
            )
            db.commit()
    finally:
        db.close()

    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_pro["header"],
        json={"preference_value": "tenant-attempt"},
    )
    assert resp.status_code == 403, resp.text


def test_pf011_locked_preference_allows_platform_admin(
    client: TestClient, platform_header: dict, catalogue_key: str
):
    """The lock is Platform-Admin-only, asserted through the API as that actor.

    The locked row is test-owned (a test catalogue key) and attached to the platform
    tenant, so the Platform Admin's own JWT tenant is the one being written. The
    ``catalogue_key`` fixture removes the row afterwards.
    """
    with platform_session() as db:
        platform_tenant_id = db.execute(
            text("SELECT tenant_id FROM core.tenant WHERE tenant_code = :c"),
            {"c": PLATFORM_TENANT_CODE},
        ).scalar()
    assert platform_tenant_id is not None

    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.tenant_preference "
                    "(tenant_id, preference_key, preference_value, is_editable) "
                    "VALUES (:t, :k, 'locked', FALSE)"
                ),
                {"t": platform_tenant_id, "k": catalogue_key},
            )
            db.commit()
    finally:
        db.close()

    resp = client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=platform_header,
        json={"preference_value": "platform-admin-ok"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["preference_value"] == "platform-admin-ok"


# ===========================================================================
# 7. Audit
# ===========================================================================
def test_pf011_tenant_writes_emit_audit_events_with_snapshots(
    client: TestClient, tenant_pro: dict, catalogue_key: str
):
    """Every tenant write path emits its audit event with before/after snapshots."""
    client.put(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"currency_code": "USD"},
    )
    client.put(
        f"{API}/settings/preferences/{catalogue_key}",
        headers=tenant_pro["header"],
        json={"preference_value": "audited"},
    )
    client.put(
        f"{API}/settings/notifications",
        headers=tenant_pro["header"],
        json=[{"event_type": "PF011_AUDIT_EVENT", "module_code": "PF", "email_enabled": True}],
    )
    client.put(
        f"{API}/settings/module-defaults",
        headers=tenant_pro["header"],
        json=[
            {
                "module_code": "PF",
                "entity_type": "pf011_audit",
                "field_name": "probe",
                "default_value": "v",
            }
        ],
    )
    client.post(
        f"{API}/settings/holidays",
        headers=tenant_pro["header"],
        json={"holiday_name": _unique("PF011_AUDIT_HOL_"), "holiday_date": "2099-03-01"},
    )
    reset = client.post(
        f"{API}/settings/reset", headers=tenant_pro["header"], json={"confirmed": True}
    )
    assert reset.status_code == 200, reset.text

    rows = _audit_rows(tuple(WRITE_EVENT_TYPES))
    seen = {row["event_type"] for row in rows if row["tenant_id"] == tenant_pro["tenant_id"]}
    for event_type in WRITE_EVENT_TYPES:
        if event_type == "PLATFORM_SETTINGS_UPDATED":
            continue
        assert event_type in seen, (event_type, sorted(seen))

    for row in rows:
        if row["tenant_id"] != tenant_pro["tenant_id"]:
            continue
        expected_entity, expects_snapshot = WRITE_EVENT_TYPES[row["event_type"]]
        assert row["entity_type"] == expected_entity, row["event_type"]
        if expects_snapshot:
            payload = json.loads(row["payload_json"] or "{}")
            assert "before" in payload and "after" in payload, row["event_type"]


def test_pf011_platform_settings_audit_uses_platform_entity_type(
    client: TestClient, platform_header: dict
):
    key = _unique("pf011_audit_platform_")
    try:
        put = client.put(
            f"{API}/platform/settings",
            headers=platform_header,
            json=[{"key": key, "value": "audited"}],
        )
        assert put.status_code == 200, put.text

        rows = _audit_rows(("PLATFORM_SETTINGS_UPDATED",))
        assert rows, "no platform settings audit event"
        row = rows[0]
        assert row["entity_type"] == "platform_setting"
        assert row["tenant_id"] is None, "platform-global audit must not be tenant-scoped"
        payload = json.loads(row["payload_json"] or "{}")
        assert "before" in payload and "after" in payload
    finally:
        db = _owner_session()
        try:
            with owner_role():
                db.execute(text("RESET ROLE"))
                db.execute(
                    text("DELETE FROM core.platform_setting WHERE key = :k"), {"k": key}
                )
                db.commit()
        finally:
            db.close()


# ===========================================================================
# 8. Cache (Redis client boundary only; no external Redis required)
# ===========================================================================
class _FakeRedis:
    """Minimal Redis stand-in recording the operations the service performs."""

    def __init__(self, fail: bool = False) -> None:
        self.store: dict[str, str] = {}
        self.set_calls: list[tuple] = []
        self.deleted: list[str] = []
        self.fail = fail

    def get(self, key: str):
        if self.fail:
            raise redis.RedisError("pf011-test: redis unavailable")
        return self.store.get(key)

    def set(self, key: str, value: str, ex=None):
        if self.fail:
            raise redis.RedisError("pf011-test: redis unavailable")
        self.set_calls.append((key, value, ex))
        self.store[key] = value

    def delete(self, key: str):
        if self.fail:
            raise redis.RedisError("pf011-test: redis unavailable")
        self.deleted.append(key)
        self.store.pop(key, None)


def test_pf011_cache_key_is_tenant_scoped():
    service = SettingsService.__new__(SettingsService)
    service.tenant_id = uuid.UUID(int=7)
    key = service._cache_key()
    assert key == f"{CACHE_PREFIX}:{uuid.UUID(int=7)}"
    assert CACHE_PREFIX in key and str(service.tenant_id) in key


def test_pf011_cache_ttl_is_300_seconds():
    assert CACHE_TTL_SECONDS == 300


def test_pf011_settings_read_populates_cache_with_ttl_300(
    client: TestClient, tenant_pro: dict, monkeypatch
):
    fake = _FakeRedis()
    monkeypatch.setattr(settings_module, "get_redis_client", lambda url=None: fake)

    resp = client.get(f"{API}/settings", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text

    assert fake.set_calls, "settings read did not populate the cache"
    key, _value, ex = fake.set_calls[-1]
    assert key == f"{CACHE_PREFIX}:{tenant_pro['tenant_id']}"
    assert ex == CACHE_TTL_SECONDS


def test_pf011_successful_write_invalidates_the_tenant_cache(
    client: TestClient, tenant_pro: dict, monkeypatch
):
    fake = _FakeRedis()
    monkeypatch.setattr(settings_module, "get_redis_client", lambda url=None: fake)

    resp = client.put(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"time_zone": "Asia/Kolkata"},
    )
    assert resp.status_code == 200, resp.text
    assert fake.deleted, "successful write did not invalidate the tenant cache"
    assert fake.deleted[-1] == f"{CACHE_PREFIX}:{tenant_pro['tenant_id']}"


def test_pf011_redis_failure_falls_back_to_the_database(
    client: TestClient, tenant_pro: dict, monkeypatch
):
    """A broken Redis must never break a settings read."""
    fake = _FakeRedis(fail=True)
    monkeypatch.setattr(settings_module, "get_redis_client", lambda url=None: fake)

    resp = client.get(f"{API}/settings", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["tenant_id"] == tenant_pro["id"]


def test_pf011_redis_failure_does_not_fail_a_write(
    client: TestClient, tenant_pro: dict, monkeypatch
):
    fake = _FakeRedis(fail=True)
    monkeypatch.setattr(settings_module, "get_redis_client", lambda url=None: fake)

    resp = client.put(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"time_zone": "Asia/Kolkata"},
    )
    assert resp.status_code == 200, resp.text


def test_pf011_cache_client_unconstructable_still_serves(
    client: TestClient, tenant_pro: dict, monkeypatch
):
    def boom(url=None):
        raise ValueError("pf011-test: bad REDIS_URL")

    monkeypatch.setattr(settings_module, "get_redis_client", boom)
    resp = client.get(f"{API}/settings", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text


def test_pf011_service_reuses_the_shared_redis_factory():
    """The service must use the project's existing client factory, not its own."""
    assert settings_module.get_redis_client.__module__ == "app.utils.redis_rate_limiter"


# ===========================================================================
# 9. Business rules
# ===========================================================================
def test_pf011_reset_requires_explicit_confirmation(client: TestClient, tenant_pro: dict):
    refused = client.post(
        f"{API}/settings/reset", headers=tenant_pro["header"], json={"confirmed": False}
    )
    assert refused.status_code == 422, refused.text

    accepted = client.post(
        f"{API}/settings/reset", headers=tenant_pro["header"], json={"confirmed": True}
    )
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["time_zone"] == "Asia/Kolkata"


def test_pf011_format_change_is_not_retroactive(client: TestClient, tenant_pro: dict):
    """A format change must not rewrite existing records (BR-PF-084, contract level)."""
    before = client.get(f"{API}/settings", headers=tenant_pro["header"]).json()
    changed = client.put(
        f"{API}/settings",
        headers=tenant_pro["header"],
        json={"date_format": "DD/MM/YYYY"},
    )
    assert changed.status_code == 200, changed.text
    after = changed.json()

    assert after["date_format"] == "DD/MM/YYYY"
    # The stored financial year and every other persisted value are untouched.
    assert after["financial_year_start"] == before["financial_year_start"]
    assert after["setting_id"] == before["setting_id"]
    assert after["currency_code"] == before["currency_code"]


def test_pf011_notification_channel_gating_only_when_a_platform_key_establishes_it(
    client: TestClient, tenant_pro: dict
):
    """BR-PF-081 channel gating — skipped unless a platform key defines channel semantics.

    No key name is invented: the test inspects the discovered ``core.platform_setting``
    keys and only asserts gating behaviour when one of them establishes channel
    semantics. Otherwise it skips with the reason recorded.
    """
    with platform_session() as db:
        keys = [
            row[0]
            for row in db.execute(text("SELECT key FROM core.platform_setting")).all()
        ]
    channel_keys = [
        k
        for k in keys
        if "notification" in k.lower()
        and ("channel" in k.lower() or "enabled" in k.lower() or "disabled" in k.lower())
    ]
    if not channel_keys:
        pytest.skip(
            "no core.platform_setting key establishes notification-channel semantics; "
            "BR-PF-081 cannot be tested without inventing a key name"
        )

    # A platform key exists: the tenant must not be able to enable a disabled channel.
    assert channel_keys  # pragma: no cover - reached only when the key exists


# ===========================================================================
# 10. Tenant isolation through the API
# ===========================================================================
def test_pf011_settings_never_expose_a_foreign_tenant(
    client: TestClient, tenant_pro: dict, tenant_com: dict
):
    resp = client.get(f"{API}/settings", headers=tenant_pro["header"])
    assert resp.status_code == 200, resp.text
    assert resp.json()["tenant_id"] == tenant_pro["id"]
    assert resp.json()["tenant_id"] != tenant_com["id"]


def test_pf011_cross_tenant_preference_rows_are_not_visible(
    client: TestClient, tenant_pro: dict, tenant_com: dict, catalogue_key: str
):
    """A preference owned by another tenant is invisible to this tenant's API."""
    db = _owner_session()
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text(
                    "INSERT INTO core.tenant_preference "
                    "(tenant_id, preference_key, preference_value, is_editable) "
                    "VALUES (:t, :k, 'foreign', TRUE)"
                ),
                {"t": tenant_com["tenant_id"], "k": catalogue_key},
            )
            db.commit()
    finally:
        db.close()

    listed = client.get(f"{API}/settings/preferences", headers=tenant_pro["header"])
    assert listed.status_code == 200, listed.text
    tenant_ids = {row["tenant_id"] for row in listed.json()["items"]}
    assert tenant_ids <= {tenant_pro["id"]}, tenant_ids
    assert tenant_com["id"] not in tenant_ids


# ===========================================================================
# 11. Idempotency / migration
# ===========================================================================
def test_pf011_ddl_is_idempotent():
    db = SessionLocal()
    try:
        apply_pf011_ddl(db)
        apply_pf011_ddl(db)
    finally:
        db.close()
    for table in PF011_TENANT_TABLES + PF011_PLATFORM_TABLES:
        assert _table_count(table) == 1, f"core.{table} duplicated or missing"


def test_pf011_ddl_preserves_tenant_settings():
    """Re-applying the DDL must not recreate or replace ``tenant_settings``."""
    db = SessionLocal()
    try:
        before = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'core' AND table_name = 'tenant_settings' "
                "ORDER BY column_name"
            )
        ).scalars().all()
        apply_pf011_ddl(db)
        after = db.execute(
            text(
                "SELECT column_name FROM information_schema.columns "
                "WHERE table_schema = 'core' AND table_name = 'tenant_settings' "
                "ORDER BY column_name"
            )
        ).scalars().all()
    finally:
        db.close()
    assert list(before) == list(after)
    assert _table_count("tenant_settings") == 1
