"""PF-007 Business Unit Management tests (Batch 1 — schema + domain layer).

Coverage follows the authorized Batch 1 scope and the approved D1-D11 decisions:
edition gating (BR-PF-046), tenant isolation, the authoritative §12 permission matrix
(incl. D2 export and D3 read-only Project Manager), code uniqueness (BR-PF-047, including
cross-tenant reuse), BU-manager validation (BR-PF-048), the edition quota (BR-PF-050),
organization immutability (D7), the §5 lifecycle with ARCHIVED terminal, optimistic
locking, soft delete, RLS enforcement and the deferred-scope absence checks.

Conventions mirror the PF-004/PF-005/PF-006 suites: ``TestClient`` against
``app.main.app``, module-scoped tenants provisioned through the platform API, and the
shared ``platform_session`` helper for DB-level assertions. The suite uses dedicated
tenants per concern so that (for example) the 20-business-unit quota test cannot disturb
the tenants used by the other tests.

Deliberately NOT covered (out of Batch 1 scope): opportunity/project/invoice linkage
(D6), reporting/XLSX-PDF export formatting (D8), notifications, history API (D1),
``users.business_unit_id`` (PF-008) and Flutter (D10).
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf003a import RLS_TABLES
from app.db.migrate_pf007 import apply_pf007_ddl
from app.db.rls_context import clear_rls_context
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Organization, Role, Tenant, User
from tests.conftest import platform_admin_select, platform_session

BUSINESS_UNITS = "/api/v1/org/business-units"
ORGANIZATIONS = "/api/v1/org/organizations"
TENANTS = "/api/v1/platform/tenants"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf007_ddl(db)
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
def platform_header(platform_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {platform_token}"}


# --------------------------------------------------------------------- helpers
def _unique(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def _register_and_approve(
    client: TestClient,
    platform_header: dict,
    code: str,
    edition_code: str = "PROFESSIONAL",
) -> dict:
    create = client.post(
        TENANTS,
        headers=platform_header,
        json={
            "code": code,
            "legal_name": f"Legal {code}",
            "trade_name": f"Trade {code}",
            "edition_code": edition_code,
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
                "line1": "1 Business Unit Street",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    apr = client.post(
        f"{TENANTS}/{tenant['id']}/approve",
        headers=platform_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    return apr.json()


def _provision_user(
    tenant_id: uuid.UUID,
    role_code: str,
    email: str,
    password: str,
    *,
    account_status: str = "ACTIVE",
    is_active: bool = True,
) -> uuid.UUID:
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        assert org is not None
        role = db.scalars(
            select(Role).where(Role.tenant_id == tenant_id, Role.role_code == role_code)
        ).first()
        if role is None:
            role = Role(
                tenant_id=tenant_id,
                role_code=role_code,
                role_name=role_code.replace("_", " ").title(),
                is_system=True,
            )
            db.add(role)
            db.flush()
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            employee_code=f"{role_code[:3]}{uuid.uuid4().hex[:6].upper()}",
            first_name=role_code.split("_")[0].title(),
            last_name="User",
            display_name=f"{role_code} User",
            email=email.lower(),
            password_hash=hash_password(password),
            account_status=account_status,
            is_active=is_active,
        )
        db.add(user)
        db.commit()
        return user.user_id


def _login(client: TestClient, email: str, password: str, tenant_code: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": tenant_code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _new_tenant_admin(
    client: TestClient,
    platform_header: dict,
    prefix: str = "bu",
    edition_code: str = "PROFESSIONAL",
) -> dict:
    """Provision a tenant + TENANT_ADMIN (+ read-only/denied actors) and return context."""
    code = _unique(prefix)
    tenant = _register_and_approve(client, platform_header, code, edition_code)
    tenant_id = uuid.UUID(tenant["id"])
    email = f"ta-{code}@example.com"
    password = "BuAdmin!234"
    _provision_user(tenant_id, "TENANT_ADMIN", email, password)
    headers = {"Authorization": f"Bearer {_login(client, email, password, code)}"}
    root = client.get(f"{ORGANIZATIONS}/root", headers=headers)
    assert root.status_code == 200, root.text
    ctx: dict = {
        "code": code,
        "tenant_id": tenant_id,
        "email": email,
        "password": password,
        "headers": headers,
        "org_id": root.json()["id"],
        "edition": edition_code,
        "users": {},
    }
    for role_code in (
        "SALES_MANAGER",
        "PROJECT_MANAGER",
        "FINANCE_USER",
        "SUPPORT_AGENT",
    ):
        actor_email = f"{role_code.lower()}-{code}@example.com"
        actor_password = "BuUser!234"
        _provision_user(tenant_id, role_code, actor_email, actor_password)
        ctx["users"][role_code] = {
            "headers": {
                "Authorization": f"Bearer {_login(client, actor_email, actor_password, code)}"
            }
        }
    return ctx


def _second_org(client: TestClient, ctx: dict) -> str:
    """Create a second organization in the same tenant (D7 immutability tests).

    PF-004 BR-PF-028 forbids a second ROOT organization, so the second organization is a
    child of the tenant's root organization.
    """
    resp = client.post(
        ORGANIZATIONS,
        headers=ctx["headers"],
        json={
            "code": _unique("O"),
            "name": f"Second Org {uuid.uuid4().hex[:6]}",
            "parent_organization_id": ctx["org_id"],
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_bu(
    client: TestClient,
    ctx: dict,
    *,
    headers: dict | None = None,
    name: str = "Business Unit",
    organization_id: str | None = None,
    code: str | None = None,
    **extra,
):
    payload: dict = {
        "code": code or _unique("BU"),
        "name": name,
        "organization_id": organization_id or ctx["org_id"],
    }
    payload.update(extra)
    return client.post(BUSINESS_UNITS, headers=headers or ctx["headers"], json=payload)


def _new_bu(client: TestClient, ctx: dict, **kwargs) -> dict:
    resp = _create_bu(client, ctx, **kwargs)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _error_code(resp) -> str | None:
    """Read the API error code from either response shape.

    Gate errors raised in the router reach the ``AppError`` handler (top-level
    ``{"error": ...}``); service errors are converted to ``HTTPException``
    (``{"detail": {"error": ...}}``).
    """
    body = resp.json()
    if "error" in body:
        return body["error"].get("code")
    return (body.get("detail") or {}).get("error", {}).get("code")


@pytest.fixture(scope="module")
def tenanta(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "bua")


@pytest.fixture(scope="module")
def tenantb(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "bub")


@pytest.fixture(scope="module")
def tenant_community(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "buc", "COMMUNITY")


@pytest.fixture(scope="module")
def tenant_enterprise(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "bue", "ENTERPRISE")


@pytest.fixture(scope="module")
def tenant_quota(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "buq")


# ================================================== A. API smoke (CRUD surface)
def test_create_get_and_list(client: TestClient, tenanta: dict) -> None:
    created = _new_bu(client, tenanta, name="Smoke BU")
    assert created["code"].isupper()
    assert created["status"] == "ACTIVE"
    assert created["version_no"] == 1
    assert created["tenant_id"] == str(tenanta["tenant_id"])
    assert created["organization_id"] == tenanta["org_id"]

    got = client.get(f"{BUSINESS_UNITS}/{created['id']}", headers=tenanta["headers"])
    assert got.status_code == 200, got.text
    assert got.json()["id"] == created["id"]

    listing = client.get(
        BUSINESS_UNITS, headers=tenanta["headers"], params={"page_size": 100}
    )
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert body["total"] >= 1
    assert created["id"] in [i["id"] for i in body["items"]]

    search = client.get(
        f"{BUSINESS_UNITS}/search",
        headers=tenanta["headers"],
        params={"q": created["code"]},
    )
    assert search.status_code == 200, search.text
    assert created["id"] in [i["id"] for i in search.json()["items"]]


def test_approved_endpoint_set(client: TestClient) -> None:
    """Exactly the eight BFS §10 paths exist — no history path (D1)."""
    paths = client.get("/openapi.json").json()["paths"]
    base = "/api/v1/org/business-units"
    for path in (
        base,
        f"{base}/search",
        f"{base}/export",
        f"{base}/{{business_unit_id}}",
    ):
        assert path in paths, path
    assert f"{base}/{{business_unit_id}}/history" not in paths
    assert f"{base}/export.csv" not in paths
    methods = set(paths[base].keys())
    assert {"get", "post"}.issubset(methods)
    assert set(paths[f"{base}/{{business_unit_id}}"].keys()) >= {
        "get",
        "put",
        "patch",
        "delete",
    }


def test_patch_and_put(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Patch BU")
    patched = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"name": "Patched BU", "version_no": bu["version_no"]},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "Patched BU"
    # code is immutable — it is not an accepted field
    assert patched.json()["code"] == bu["code"]

    replaced = client.put(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"name": "Replaced BU", "version_no": patched.json()["version_no"]},
    )
    assert replaced.status_code == 200, replaced.text
    assert replaced.json()["name"] == "Replaced BU"


def test_soft_delete_endpoint(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Delete BU")
    deleted = client.delete(f"{BUSINESS_UNITS}/{bu['id']}", headers=tenanta["headers"])
    assert deleted.status_code == 204, deleted.text
    assert (
        client.get(f"{BUSINESS_UNITS}/{bu['id']}", headers=tenanta["headers"]).status_code
        == 404
    )
    # the soft-deleted code is released for reuse (partial unique index)
    again = _create_bu(client, tenanta, name="Delete BU again", code=bu["code"])
    assert again.status_code == 201, again.text


def test_optimistic_locking(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Lock BU")
    first = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"name": "Lock BU 1", "version_no": bu["version_no"]},
    )
    assert first.status_code == 200, first.text
    stale = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"name": "Lock BU 2", "version_no": bu["version_no"]},
    )
    assert stale.status_code == 409, stale.text


# ============================================================ B. Edition gating
def test_community_edition_rejected(
    client: TestClient, tenant_community: dict
) -> None:
    """BR-PF-046 / AC-PF-007-01 — Community cannot create or use business units."""
    created = _create_bu(client, tenant_community, name="Community BU")
    assert created.status_code == 403, created.text
    assert _error_code(created) == "FORBIDDEN"

    listed = client.get(BUSINESS_UNITS, headers=tenant_community["headers"])
    assert listed.status_code == 403, listed.text

    exported = client.get(f"{BUSINESS_UNITS}/export", headers=tenant_community["headers"])
    assert exported.status_code == 403, exported.text


def test_professional_edition_allowed(client: TestClient, tenanta: dict) -> None:
    assert tenanta["edition"] == "PROFESSIONAL"
    created = _create_bu(client, tenanta, name="Professional BU")
    assert created.status_code == 201, created.text


def test_enterprise_edition_allowed(
    client: TestClient, tenant_enterprise: dict
) -> None:
    assert tenant_enterprise["edition"] == "ENTERPRISE"
    created = _create_bu(client, tenant_enterprise, name="Enterprise BU")
    assert created.status_code == 201, created.text


# =========================================================== C. Tenant isolation
def test_tenant_isolation_read_write_delete(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    bu = _new_bu(client, tenanta, name="Isolated BU")
    assert (
        client.get(f"{BUSINESS_UNITS}/{bu['id']}", headers=tenantb["headers"]).status_code
        == 404
    )
    assert (
        client.patch(
            f"{BUSINESS_UNITS}/{bu['id']}",
            headers=tenantb["headers"],
            json={"name": "Hacked", "version_no": bu["version_no"]},
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"{BUSINESS_UNITS}/{bu['id']}",
            headers=tenantb["headers"],
            json={"name": "Hacked", "version_no": bu["version_no"]},
        ).status_code
        == 404
    )
    assert (
        client.delete(f"{BUSINESS_UNITS}/{bu['id']}", headers=tenantb["headers"]).status_code
        == 404
    )
    listing = client.get(
        BUSINESS_UNITS, headers=tenantb["headers"], params={"page_size": 100}
    )
    assert bu["id"] not in [i["id"] for i in listing.json()["items"]]


def test_tenant_isolation_foreign_references(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    foreign_org = client.get(
        f"{ORGANIZATIONS}/root", headers=tenanta["headers"]
    ).json()["id"]
    cross_org = _create_bu(client, tenantb, name="Cross Tenant Org", organization_id=foreign_org)
    assert cross_org.status_code == 404, cross_org.text


# ======================================================== D. Permission matrix
def test_permission_matrix_read_only_roles(
    client: TestClient, tenanta: dict
) -> None:
    """§12 + D3: Sales Manager, Finance User and Project Manager are read-only."""
    bu = _new_bu(client, tenanta, name="Matrix BU")
    for role_code in ("SALES_MANAGER", "PROJECT_MANAGER", "FINANCE_USER"):
        headers = tenanta["users"][role_code]["headers"]
        assert (
            client.get(f"{BUSINESS_UNITS}/{bu['id']}", headers=headers).status_code == 200
        ), role_code
        denied = client.patch(
            f"{BUSINESS_UNITS}/{bu['id']}",
            headers=headers,
            json={"name": "Nope", "version_no": bu["version_no"]},
        )
        assert denied.status_code == 403, (role_code, denied.text)


def test_permission_matrix_denied_roles(
    client: TestClient, tenanta: dict
) -> None:
    """SUPPORT_AGENT is not a BFS-PF-007 §12 actor — read is denied."""
    headers = tenanta["users"]["SUPPORT_AGENT"]["headers"]
    assert client.get(BUSINESS_UNITS, headers=headers).status_code == 403


def test_platform_admin_not_a_pf007_actor(
    client: TestClient, platform_header: dict, tenanta: dict
) -> None:
    """PLATFORM_ADMIN holds no PF-007 grant; the PF-007 gate denies it (PF-009 debt)."""
    assert client.get(BUSINESS_UNITS, headers=platform_header).status_code == 403
    bu = _new_bu(client, tenanta, name="Platform BU")
    assert (
        client.get(f"{BUSINESS_UNITS}/{bu['id']}", headers=platform_header).status_code
        == 403
    )


def test_export_requires_tenant_admin(
    client: TestClient, tenanta: dict, platform_header: dict
) -> None:
    """D2 — export is Tenant Admin only."""
    assert (
        client.get(f"{BUSINESS_UNITS}/export", headers=tenanta["headers"]).status_code == 200
    )
    for role_code in ("SALES_MANAGER", "FINANCE_USER", "PROJECT_MANAGER"):
        headers = tenanta["users"][role_code]["headers"]
        assert (
            client.get(f"{BUSINESS_UNITS}/export", headers=headers).status_code == 403
        ), role_code
    assert (
        client.get(f"{BUSINESS_UNITS}/export", headers=platform_header).status_code == 403
    )
    # JSON only — no formatting artefact endpoint (D8)
    payload = client.get(f"{BUSINESS_UNITS}/export", headers=tenanta["headers"]).json()
    assert isinstance(payload, list)


# ================================================ E. BR-PF-047 code uniqueness
def test_duplicate_code_within_tenant(client: TestClient, tenanta: dict) -> None:
    first = _new_bu(client, tenanta, name="Unique BU")
    duplicate = _create_bu(client, tenanta, name="Duplicate BU", code=first["code"])
    assert duplicate.status_code == 409, duplicate.text
    assert _error_code(duplicate) == "CONFLICT"


def test_same_code_allowed_across_tenants(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    shared_code = _unique("SHARED")
    assert _create_bu(client, tenanta, name="Shared A", code=shared_code).status_code == 201
    assert _create_bu(client, tenantb, name="Shared B", code=shared_code).status_code == 201


# ================================================== F. BR-PF-048 manager rules
def test_active_same_tenant_manager_accepted(
    client: TestClient, tenanta: dict
) -> None:
    manager_id = _provision_user(
        tenanta["tenant_id"],
        "SALES_MANAGER",
        f"mgr-ok-{uuid.uuid4().hex[:6]}@example.com",
        "MgrUser!234",
    )
    created = _create_bu(
        client, tenanta, name="Manager BU", bu_manager_user_id=str(manager_id)
    )
    assert created.status_code == 201, created.text
    assert created.json()["bu_manager_user_id"] == str(manager_id)


def test_inactive_manager_rejected(client: TestClient, tenanta: dict) -> None:
    inactive_id = _provision_user(
        tenanta["tenant_id"],
        "SALES_MANAGER",
        f"mgr-off-{uuid.uuid4().hex[:6]}@example.com",
        "MgrUser!234",
        account_status="INACTIVE",
    )
    rejected = _create_bu(
        client, tenanta, name="Inactive Manager BU", bu_manager_user_id=str(inactive_id)
    )
    assert rejected.status_code == 422, rejected.text
    assert _error_code(rejected) == "VALIDATION_ERROR"

    # a user whose is_active flag is false is likewise not ACTIVE
    flag_off_id = _provision_user(
        tenanta["tenant_id"],
        "SALES_MANAGER",
        f"mgr-flag-{uuid.uuid4().hex[:6]}@example.com",
        "MgrUser!234",
        is_active=False,
    )
    flag_rejected = _create_bu(
        client, tenanta, name="Flag Manager BU", bu_manager_user_id=str(flag_off_id)
    )
    assert flag_rejected.status_code == 422, flag_rejected.text


def test_cross_tenant_manager_rejected(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    foreign_manager = _provision_user(
        tenantb["tenant_id"],
        "SALES_MANAGER",
        f"mgr-x-{uuid.uuid4().hex[:6]}@example.com",
        "MgrUser!234",
    )
    rejected = _create_bu(
        client,
        tenanta,
        name="Cross Manager BU",
        bu_manager_user_id=str(foreign_manager),
    )
    assert rejected.status_code == 404, rejected.text


def test_manager_validated_on_update(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Manager Update BU")
    inactive_id = _provision_user(
        tenanta["tenant_id"],
        "SALES_MANAGER",
        f"mgr-upd-{uuid.uuid4().hex[:6]}@example.com",
        "MgrUser!234",
        account_status="INACTIVE",
    )
    rejected = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={
            "bu_manager_user_id": str(inactive_id),
            "version_no": bu["version_no"],
        },
    )
    assert rejected.status_code == 422, rejected.text


# ===================================================== G. BR-PF-050 edition quota
def test_professional_business_unit_limit(
    client: TestClient, tenant_quota: dict
) -> None:
    """BR-PF-050: Professional = maximum 20 business units."""
    for index in range(20):
        resp = _create_bu(client, tenant_quota, name=f"Quota BU {index}")
        assert resp.status_code == 201, (index, resp.text)
    over = _create_bu(client, tenant_quota, name="Quota BU 21")
    assert over.status_code == 422, over.text
    assert _error_code(over) == "VALIDATION_ERROR"


def test_enterprise_business_unit_unlimited(
    client: TestClient, tenant_enterprise: dict
) -> None:
    """BR-PF-050: Enterprise is unlimited — 21+ business units are accepted."""
    for index in range(21):
        resp = _create_bu(client, tenant_enterprise, name=f"Unlimited BU {index}")
        assert resp.status_code == 201, (index, resp.text)
    listing = client.get(
        BUSINESS_UNITS, headers=tenant_enterprise["headers"], params={"page_size": 100}
    )
    assert listing.json()["total"] >= 21


# ============================================ H. D7 organization_id immutability
def test_organization_id_immutable(client: TestClient, tenanta: dict) -> None:
    other_org = _second_org(client, tenanta)
    bu = _new_bu(client, tenanta, name="Immutable Org BU")

    changed = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"organization_id": other_org, "version_no": bu["version_no"]},
    )
    assert changed.status_code == 422, changed.text
    assert _error_code(changed) == "VALIDATION_ERROR"

    replaced = client.put(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"name": "Immutable Org BU", "organization_id": other_org, "version_no": bu["version_no"]},
    )
    assert replaced.status_code == 422, replaced.text

    # repeating the current organization is accepted (no change requested)
    same = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"organization_id": bu["organization_id"], "version_no": bu["version_no"]},
    )
    assert same.status_code == 200, same.text
    assert same.json()["organization_id"] == bu["organization_id"]


# =============================================================== I. Lifecycle
def test_status_lifecycle(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Lifecycle BU")
    assert bu["status"] == "ACTIVE"

    to_inactive = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": bu["version_no"]},
    )
    assert to_inactive.status_code == 200, to_inactive.text
    assert to_inactive.json()["status"] == "INACTIVE"

    back_active = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "ACTIVE", "version_no": to_inactive.json()["version_no"]},
    )
    assert back_active.status_code == 200, back_active.text
    assert back_active.json()["status"] == "ACTIVE"

    to_inactive_again = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": back_active.json()["version_no"]},
    )
    assert to_inactive_again.status_code == 200, to_inactive_again.text
    archived = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "ARCHIVED", "version_no": to_inactive_again.json()["version_no"]},
    )
    assert archived.status_code == 200, archived.text
    assert archived.json()["status"] == "ARCHIVED"


def test_archived_is_terminal(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Terminal BU")
    first = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": bu["version_no"]},
    )
    assert first.status_code == 200, first.text
    second = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "ARCHIVED", "version_no": first.json()["version_no"]},
    )
    assert second.status_code == 200, second.text

    for target in ("ACTIVE", "INACTIVE"):
        blocked = client.patch(
            f"{BUSINESS_UNITS}/{bu['id']}",
            headers=tenanta["headers"],
            json={"status": target, "version_no": second.json()["version_no"]},
        )
        assert blocked.status_code == 422, (target, blocked.text)


def test_invalid_status_rejected(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="Invalid Status BU")
    bad = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "RETIRED", "version_no": bu["version_no"]},
    )
    assert bad.status_code == 422, bad.text


# ================================================= J. BR-PF-049 assignment guard
def test_inactive_business_unit_not_assignable(
    client: TestClient, tenanta: dict
) -> None:
    """BR-PF-049 domain guard — Batch 1 exposes the rule without project linkage (D6)."""
    from app.core.exceptions import ValidationAppError
    from app.services.pf.business_unit_service import BusinessUnitService

    bu = _new_bu(client, tenanta, name="Assignable BU")
    with platform_session() as db:
        service = BusinessUnitService(db)
        # ACTIVE business unit is assignable
        service.assert_assignable(tenanta["tenant_id"], uuid.UUID(bu["id"]))

    deactivated = client.patch(
        f"{BUSINESS_UNITS}/{bu['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": bu["version_no"]},
    )
    assert deactivated.status_code == 200, deactivated.text
    with platform_session() as db:
        service = BusinessUnitService(db)
        with pytest.raises(ValidationAppError):
            service.assert_assignable(tenanta["tenant_id"], uuid.UUID(bu["id"]))


# ============================================== K. RLS + deferred-scope absence
def test_rls_enforced_on_business_unit(client: TestClient, tenanta: dict) -> None:
    bu = _new_bu(client, tenanta, name="RLS BU")
    assert ("core", "business_unit") in RLS_TABLES

    with platform_session() as db:
        visible = db.execute(
            text("SELECT count(*) FROM core.business_unit WHERE tenant_id = :t"),
            {"t": str(tenanta["tenant_id"])},
        ).scalar()
        assert visible >= 1

    db = SessionLocal()
    try:
        clear_rls_context(db)
        # fail-closed: elu_app + empty GUCs → zero tenant rows (FORCE RLS)
        assert db.execute(text("SELECT count(*) FROM core.business_unit")).scalar() == 0
    finally:
        clear_rls_context(db)
        db.close()


def test_deferred_scope_absent(client: TestClient, tenanta: dict) -> None:
    """No D6/D8/PF-008 surface may leak into Batch 1."""
    bu = _new_bu(client, tenanta, name="Scope BU")

    with platform_session() as db:
        # PF-008 CORE (authorized 2026-09-21): core.users.business_unit_id now exists. The
        # crm.opportunity linkage (D6) remains deferred and is still asserted absent.
        assert (
            db.execute(
                text(
                    "SELECT count(*) FROM information_schema.columns "
                    "WHERE table_schema = :s AND table_name = :t AND column_name = :c"
                ),
                {"s": "core", "t": "users", "c": "business_unit_id"},
            ).scalar()
            == 1
        ), "core.users.business_unit_id (PF-008) must exist"
        assert (
            db.execute(
                text(
                    "SELECT count(*) FROM information_schema.columns "
                    "WHERE table_schema = :s AND table_name = :t AND column_name = :c"
                ),
                {"s": "crm", "t": "opportunity", "c": "business_unit_id"},
            ).scalar()
            == 0
        ), "crm.opportunity.business_unit_id must not exist (D6)"

        # only the tenant and organization FKs exist on core.business_unit
        fks = db.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE conrelid = 'core.business_unit'::regclass AND contype = 'f' "
                "ORDER BY conname"
            )
        ).scalars().all()
        assert sorted(fks) == [
            "fk_business_unit_organization",
            "fk_business_unit_tenant",
        ]

        # the only reference to core.business_unit is the PF-008 user linkage; the deferred
        # opportunity/project/invoice linkage (D6) is still absent
        referencing = db.execute(
            text(
                "SELECT conname FROM pg_constraint "
                "WHERE contype = 'f' AND confrelid = 'core.business_unit'::regclass "
                "ORDER BY conname"
            )
        ).scalars().all()
        assert list(referencing) == ["fk_users_business_unit"]

    # no reporting / formatting surface
    paths = client.get("/openapi.json").json()["paths"]
    assert not any("report" in p for p in paths)
    assert f"{BUSINESS_UNITS}/{{business_unit_id}}/history" not in paths
    assert bu["id"]  # sanity: the created record is addressable
