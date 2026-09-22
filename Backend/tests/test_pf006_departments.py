"""PF-006 Department Management tests (Batch 5 — API + service).

Coverage follows the approved PF-006 scope: API smoke (list/get/create/PATCH/PUT/move/
hierarchy/export/history/soft delete), tenant isolation, the authoritative §12 permission
matrix, hierarchy rules (C-N7/C-N9/C-N11, BR-PF-041/BR-PF-042), the adopted
organization-change policy (Batch 3-C), branch rules (C-N10), lifecycle (C-N3, §5),
optimistic locking, soft delete (BR-PF-044) and export (C-N4, JSON only).

Conventions mirror the PF-004/PF-005 suites: ``TestClient`` against ``app.main.app``,
module-scoped tenants provisioned through the platform API, and the shared
``platform_session`` helper for DB-level assertions.

Deliberately NOT covered (out of PF-006 scope): ``users.department_id``, user↔department
assignment, BR-PF-043 department-head validation (PF-008), notifications, reports,
workflow (CPS-001), CSV/XLSX and Flutter.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf006 import apply_pf006_ddl
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Department, Organization, Role, Tenant, User
from tests.conftest import platform_session

DEPARTMENTS = "/api/v1/org/departments"
ORGANIZATIONS = "/api/v1/org/organizations"
BRANCHES = "/api/v1/org/branches"
TENANTS = "/api/v1/platform/tenants"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf006_ddl(db)
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
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
    client: TestClient, platform_header: dict, code: str, edition_code: str = "PROFESSIONAL"
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
                "line1": "1 Department Street",
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
    tenant_id: uuid.UUID, role_code: str, email: str, password: str
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
            account_status="ACTIVE",
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
    client: TestClient, platform_header: dict, prefix: str = "dep"
) -> dict:
    """Provision a tenant + TENANT_ADMIN (+ read-only/denied actors) and return context."""
    code = _unique(prefix)
    tenant = _register_and_approve(client, platform_header, code)
    tenant_id = uuid.UUID(tenant["id"])
    email = f"ta-{code}@example.com"
    password = "DeptAdmin!234"
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
        "users": {},
    }
    for role_code in (
        "SALES_MANAGER",
        "PROJECT_MANAGER",
        "FINANCE_USER",
        "SUPPORT_AGENT",
    ):
        actor_email = f"{role_code.lower()}-{code}@example.com"
        actor_password = "DeptUser!234"
        _provision_user(tenant_id, role_code, actor_email, actor_password)
        ctx["users"][role_code] = {
            "headers": {
                "Authorization": f"Bearer {_login(client, actor_email, actor_password, code)}"
            }
        }
    return ctx


def _second_org(client: TestClient, ctx: dict) -> str:
    """Create a second organization in the same tenant (C-N11 / organization-change tests).

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


def _create_branch(client: TestClient, ctx: dict, org_id: str | None = None) -> str:
    resp = client.post(
        BRANCHES,
        headers=ctx["headers"],
        json={
            "code": _unique("B"),
            "name": "Branch",
            "branch_type": "BRANCH",
            "organization_id": org_id or ctx["org_id"],
            "status": "ACTIVE",
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def _create_dept(
    client: TestClient,
    ctx: dict,
    *,
    headers: dict | None = None,
    name: str = "Department",
    organization_id: str | None = None,
    parent_department_id: str | None = None,
    branch_id: str | None = None,
    department_type: str = "FUNCTIONAL",
    code: str | None = None,
):
    payload: dict = {
        "code": code or _unique("D"),
        "name": name,
        "department_type": department_type,
        "organization_id": organization_id or ctx["org_id"],
    }
    if parent_department_id is not None:
        payload["parent_department_id"] = parent_department_id
    if branch_id is not None:
        payload["branch_id"] = branch_id
    return client.post(DEPARTMENTS, headers=headers or ctx["headers"], json=payload)


def _new_dept(client: TestClient, ctx: dict, **kwargs) -> dict:
    resp = _create_dept(client, ctx, **kwargs)
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
    return _new_tenant_admin(client, platform_header, "depa")


@pytest.fixture(scope="module")
def tenantb(client: TestClient, platform_header: dict) -> dict:
    return _new_tenant_admin(client, platform_header, "depb")


# ================================================== A. API smoke (CRUD surface)
def test_create_get_and_list(client: TestClient, tenanta: dict) -> None:
    created = _new_dept(client, tenanta, name="Smoke Dept")
    assert created["code"].isupper()
    assert created["status"] == "ACTIVE"
    assert created["version_no"] == 1
    assert created["tenant_id"] == str(tenanta["tenant_id"])

    got = client.get(f"{DEPARTMENTS}/{created['id']}", headers=tenanta["headers"])
    assert got.status_code == 200, got.text
    assert got.json()["name"] == "Smoke Dept"

    listing = client.get(DEPARTMENTS, headers=tenanta["headers"])
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert {"items", "page", "page_size", "total", "warnings"} <= set(body)
    assert created["id"] in [i["id"] for i in body["items"]]

    # filters / search / sort
    one = client.get(
        DEPARTMENTS,
        headers=tenanta["headers"],
        params={"organization_id": tenanta["org_id"], "status": "ACTIVE", "page_size": 5},
    )
    assert one.status_code == 200, one.text
    searched = client.get(
        DEPARTMENTS, headers=tenanta["headers"], params={"search": created["code"][:6]}
    )
    assert searched.status_code == 200, searched.text
    sorted_resp = client.get(
        DEPARTMENTS, headers=tenanta["headers"], params={"sort": "-code"}
    )
    assert sorted_resp.status_code == 200, sorted_resp.text


def test_search_endpoint(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Searchable Dept")
    resp = client.get(
        f"{DEPARTMENTS}/search", headers=tenanta["headers"], params={"q": dept["code"]}
    )
    assert resp.status_code == 200, resp.text
    assert dept["id"] in [i["id"] for i in resp.json()["items"]]
    missing = client.get(f"{DEPARTMENTS}/search", headers=tenanta["headers"])
    assert missing.status_code == 422


def test_patch_and_put(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Patch Dept")

    patched = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"name": "Patched Dept", "version_no": dept["version_no"]},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["name"] == "Patched Dept"
    assert patched.json()["version_no"] == dept["version_no"] + 1
    # PATCH with only supplied fields: description untouched
    assert patched.json()["description"] is None

    replaced = client.put(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={
            "name": "Replaced Dept",
            "department_type": "FUNCTIONAL",
            "version_no": patched.json()["version_no"],
        },
    )
    assert replaced.status_code == 200, replaced.text
    assert replaced.json()["name"] == "Replaced Dept"
    # PUT replaces optional fields -> explicit null
    assert replaced.json()["description"] is None

    no_name = client.put(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"version_no": replaced.json()["version_no"]},
    )
    assert no_name.status_code == 422


def test_hierarchy_export_and_history(client: TestClient, tenanta: dict) -> None:
    parent = _new_dept(client, tenanta, name="Tree Parent")
    child = _new_dept(
        client, tenanta, name="Tree Child", parent_department_id=parent["id"]
    )

    tree = client.get(f"{DEPARTMENTS}/hierarchy", headers=tenanta["headers"])
    assert tree.status_code == 200, tree.text
    roots = {n["id"]: n for n in tree.json()["items"]}
    node = roots.get(parent["id"]) or next(
        (n for n in roots.values() if any(c["id"] == parent["id"] for c in n["children"])),
        None,
    )
    assert node is not None, "parent must appear as a root"
    assert [c["id"] for c in node["children"]] == [child["id"]]

    exported = client.get(f"{DEPARTMENTS}/export", headers=tenanta["headers"])
    assert exported.status_code == 200, exported.text
    assert exported.headers["content-type"].startswith("application/json")
    rows = exported.json()
    assert isinstance(rows, list) and rows
    assert all(isinstance(r["id"], str) for r in rows)
    assert parent["id"] in [r["id"] for r in rows]

    history = client.get(
        f"{DEPARTMENTS}/{parent['id']}/history", headers=tenanta["headers"]
    )
    assert history.status_code == 200, history.text
    body = history.json()
    assert body["total"] >= 1
    assert "DEPARTMENT_CREATED" in [i["event_type"] for i in body["items"]]
    assert body["items"][0]["created_on"]


def test_soft_delete_endpoint(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Delete Dept")
    deleted = client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"])
    assert deleted.status_code == 204, deleted.text
    assert client.get(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"]).status_code == 404
    listing = client.get(DEPARTMENTS, headers=tenanta["headers"], params={"page_size": 100})
    assert dept["id"] not in [i["id"] for i in listing.json()["items"]]


def test_approved_endpoint_set(client: TestClient) -> None:
    paths = set(client.get("/openapi.json").json()["paths"].keys())
    expected = {
        DEPARTMENTS,
        f"{DEPARTMENTS}/search",
        f"{DEPARTMENTS}/export",
        f"{DEPARTMENTS}/hierarchy",
        f"{DEPARTMENTS}/{{department_id}}",
        f"{DEPARTMENTS}/{{department_id}}/move",
        f"{DEPARTMENTS}/{{department_id}}/history",
    }
    assert expected <= paths
    # no PF-008 / workflow / notification / report / csv surface leaked in
    assert not any(
        token in p
        for p in paths
        if p.startswith(DEPARTMENTS)
        for token in ("assign", "user", "workflow", "notification", "report", "csv", "excel")
    )


# =========================================================== B. Tenant isolation
def test_tenant_isolation_read_write_delete(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    dept = _new_dept(client, tenanta, name="Isolated Dept")
    assert client.get(f"{DEPARTMENTS}/{dept['id']}", headers=tenantb["headers"]).status_code == 404
    assert (
        client.patch(
            f"{DEPARTMENTS}/{dept['id']}",
            headers=tenantb["headers"],
            json={"name": "Hacked", "version_no": dept["version_no"]},
        ).status_code
        == 404
    )
    assert (
        client.put(
            f"{DEPARTMENTS}/{dept['id']}",
            headers=tenantb["headers"],
            json={"name": "Hacked", "version_no": dept["version_no"]},
        ).status_code
        == 404
    )
    assert client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=tenantb["headers"]).status_code == 404
    assert (
        client.patch(
            f"{DEPARTMENTS}/{dept['id']}/move",
            headers=tenantb["headers"],
            json={"parent_department_id": None, "version_no": dept["version_no"]},
        ).status_code
        == 404
    )
    assert client.get(
        f"{DEPARTMENTS}/{dept['id']}/history", headers=tenantb["headers"]
    ).status_code == 404
    # tenant B list cannot see tenant A rows
    listing = client.get(DEPARTMENTS, headers=tenantb["headers"], params={"page_size": 100})
    assert dept["id"] not in [i["id"] for i in listing.json()["items"]]


def test_tenant_isolation_foreign_references(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    foreign_org = client.get(f"{ORGANIZATIONS}/root", headers=tenanta["headers"]).json()["id"]
    foreign_branch = _create_branch(client, tenanta)
    foreign_parent = _new_dept(client, tenanta, name="Foreign Parent")

    for override in (
        {"organization_id": foreign_org},
        {"branch_id": foreign_branch},
        {"parent_department_id": foreign_parent["id"]},
    ):
        resp = _create_dept(client, tenantb, name="Cross Tenant", **override)
        assert resp.status_code == 404, resp.text

    # tenant B cannot move one of its own departments under a tenant A parent
    own = _new_dept(client, tenantb, name="Own Dept")
    moved = client.patch(
        f"{DEPARTMENTS}/{own['id']}/move",
        headers=tenantb["headers"],
        json={"parent_department_id": foreign_parent["id"], "version_no": own["version_no"]},
    )
    assert moved.status_code == 404, moved.text


# ========================================================= C. Permission matrix
def test_permission_matrix_read_only_roles(
    client: TestClient, tenanta: dict
) -> None:
    dept = _new_dept(client, tenanta, name="Perm Dept")
    for role_code in ("SALES_MANAGER", "PROJECT_MANAGER"):
        headers = tenanta["users"][role_code]["headers"]
        assert client.get(DEPARTMENTS, headers=headers).status_code == 200
        assert client.get(f"{DEPARTMENTS}/{dept['id']}", headers=headers).status_code == 200
        assert client.get(f"{DEPARTMENTS}/hierarchy", headers=headers).status_code == 200
        assert client.get(f"{DEPARTMENTS}/search", headers=headers, params={"q": "a"}).status_code == 200
        assert client.get(f"{DEPARTMENTS}/{dept['id']}/history", headers=headers).status_code == 200
        # write + export denied
        assert _create_dept(client, tenanta, headers=headers).status_code == 403
        assert (
            client.patch(
                f"{DEPARTMENTS}/{dept['id']}",
                headers=headers,
                json={"name": "Denied", "version_no": dept["version_no"]},
            ).status_code
            == 403
        )
        assert (
            client.put(
                f"{DEPARTMENTS}/{dept['id']}",
                headers=headers,
                json={"name": "Denied", "version_no": dept["version_no"]},
            ).status_code
            == 403
        )
        assert (
            client.patch(
                f"{DEPARTMENTS}/{dept['id']}/move",
                headers=headers,
                json={"parent_department_id": None, "version_no": dept["version_no"]},
            ).status_code
            == 403
        )
        assert client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=headers).status_code == 403
        assert client.get(f"{DEPARTMENTS}/export", headers=headers).status_code == 403


def test_permission_matrix_denied_roles(client: TestClient, tenanta: dict) -> None:
    """FINANCE_USER and SUPPORT_AGENT have no PF-006 grant (§12 is authoritative)."""
    for role_code in ("FINANCE_USER", "SUPPORT_AGENT"):
        headers = tenanta["users"][role_code]["headers"]
        assert client.get(DEPARTMENTS, headers=headers).status_code == 403
        assert _create_dept(client, tenanta, headers=headers).status_code == 403
    # FINANCE_USER also denied export (C-N4: Tenant Admin only)
    finance = tenanta["users"]["FINANCE_USER"]["headers"]
    assert client.get(f"{DEPARTMENTS}/export", headers=finance).status_code == 403


def test_platform_admin_not_a_pf006_actor(
    client: TestClient, platform_header: dict
) -> None:
    """PLATFORM_ADMIN is not a PF-006 actor (approved matrix + role-gate decision)."""
    resp = client.get(DEPARTMENTS, headers=platform_header)
    assert resp.status_code == 403, resp.text
    assert _error_code(resp) == "FORBIDDEN"


def test_export_requires_tenant_admin(client: TestClient, tenanta: dict) -> None:
    assert client.get(f"{DEPARTMENTS}/export", headers=tenanta["headers"]).status_code == 200


# ================================================================= D. Hierarchy
def test_root_depth_and_sixth_level_rejected(client: TestClient, tenanta: dict) -> None:
    parent = None
    for level in range(1, 6):
        created = _new_dept(
            client,
            tenanta,
            name=f"Level {level}",
            parent_department_id=parent["id"] if parent else None,
        )
        parent = created

    sixth = _create_dept(client, tenanta, name="Level 6", parent_department_id=parent["id"])
    assert sixth.status_code == 422, sixth.text


def test_self_parent_rejected(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Self Parent")
    resp = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"parent_department_id": dept["id"], "version_no": dept["version_no"]},
    )
    assert resp.status_code == 422, resp.text


def test_circular_parent_rejected(client: TestClient, tenanta: dict) -> None:
    root = _new_dept(client, tenanta, name="Cycle Root")
    child = _new_dept(client, tenanta, name="Cycle Child", parent_department_id=root["id"])
    resp = client.patch(
        f"{DEPARTMENTS}/{root['id']}/move",
        headers=tenanta["headers"],
        json={"parent_department_id": child["id"], "version_no": root["version_no"]},
    )
    assert resp.status_code == 422, resp.text


def test_deleted_parent_rejected(client: TestClient, tenanta: dict) -> None:
    parent = _new_dept(client, tenanta, name="Deleted Parent")
    assert client.delete(f"{DEPARTMENTS}/{parent['id']}", headers=tenanta["headers"]).status_code == 204
    resp = _create_dept(client, tenanta, name="Orphan", parent_department_id=parent["id"])
    assert resp.status_code == 404, resp.text


def test_active_inactive_archived_parent_allowed(
    client: TestClient, tenanta: dict
) -> None:
    parent = _new_dept(client, tenanta, name="Status Parent")

    inactive = client.patch(
        f"{DEPARTMENTS}/{parent['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": parent["version_no"]},
    )
    assert inactive.status_code == 200, inactive.text
    assert _create_dept(client, tenanta, name="Child Of Inactive", parent_department_id=parent["id"]).status_code == 201

    archived = client.patch(
        f"{DEPARTMENTS}/{parent['id']}",
        headers=tenanta["headers"],
        json={"status": "ARCHIVED", "version_no": inactive.json()["version_no"]},
    )
    assert archived.status_code == 200, archived.text
    assert _create_dept(client, tenanta, name="Child Of Archived", parent_department_id=parent["id"]).status_code == 201


def test_same_organization_parent_enforced(client: TestClient, tenanta: dict) -> None:
    org2 = _second_org(client, tenanta)
    parent_org1 = _new_dept(client, tenanta, name="Parent Org1")

    cross = _create_dept(
        client, tenanta, name="Cross Org Child", organization_id=org2,
        parent_department_id=parent_org1["id"],
    )
    assert cross.status_code == 422, cross.text

    parent_org2 = _new_dept(client, tenanta, name="Parent Org2", organization_id=org2)
    same = _create_dept(
        client, tenanta, name="Same Org Child", organization_id=org2,
        parent_department_id=parent_org2["id"],
    )
    assert same.status_code == 201, same.text


# ================================================= E. Organization-change policy
def test_organization_unchanged_still_works(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Org Unchanged")
    resp = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={
            "name": "Org Unchanged 2",
            "organization_id": tenanta["org_id"],
            "version_no": dept["version_no"],
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["organization_id"] == tenanta["org_id"]


def test_root_without_children_can_change_organization(
    client: TestClient, tenanta: dict
) -> None:
    org2 = _second_org(client, tenanta)
    dept = _new_dept(client, tenanta, name="Movable Root")
    resp = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"organization_id": org2, "version_no": dept["version_no"]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["organization_id"] == org2
    assert resp.json()["parent_department_id"] is None


def test_organization_change_with_retained_parent_rejected(
    client: TestClient, tenanta: dict
) -> None:
    org2 = _second_org(client, tenanta)
    parent = _new_dept(client, tenanta, name="Retain Parent")
    child = _new_dept(client, tenanta, name="Retain Child", parent_department_id=parent["id"])

    resp = client.patch(
        f"{DEPARTMENTS}/{child['id']}",
        headers=tenanta["headers"],
        json={"organization_id": org2, "version_no": child["version_no"]},
    )
    assert resp.status_code == 422, resp.text
    assert _error_code(resp) == "VALIDATION_ERROR"


def test_organization_change_with_children_rejected_and_no_cascade(
    client: TestClient, tenanta: dict
) -> None:
    org2 = _second_org(client, tenanta)
    parent = _new_dept(client, tenanta, name="Cascade Parent")
    child = _new_dept(client, tenanta, name="Cascade Child", parent_department_id=parent["id"])

    resp = client.patch(
        f"{DEPARTMENTS}/{parent['id']}",
        headers=tenanta["headers"],
        json={"organization_id": org2, "version_no": parent["version_no"]},
    )
    assert resp.status_code == 422, resp.text

    with platform_session() as db:
        row_parent = db.scalars(
            select(Department).where(Department.department_id == uuid.UUID(parent["id"]))
        ).first()
        row_child = db.scalars(
            select(Department).where(Department.department_id == uuid.UUID(child["id"]))
        ).first()
        assert row_parent is not None and row_child is not None
        # no cascade: both keep the original organization and the child keeps its parent
        assert str(row_parent.organization_id) == tenanta["org_id"]
        assert str(row_child.organization_id) == tenanta["org_id"]
        assert str(row_child.parent_department_id) == parent["id"]


def test_patch_detach_plus_organization_change_allowed(
    client: TestClient, tenanta: dict
) -> None:
    """Batch 3-C: effective parent NULL + no children ⇒ the combined request is allowed."""
    org2 = _second_org(client, tenanta)
    parent = _new_dept(client, tenanta, name="Detach Parent")
    child = _new_dept(client, tenanta, name="Detach Child", parent_department_id=parent["id"])

    resp = client.patch(
        f"{DEPARTMENTS}/{child['id']}",
        headers=tenanta["headers"],
        json={
            "parent_department_id": None,
            "organization_id": org2,
            "version_no": child["version_no"],
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["parent_department_id"] is None
    assert resp.json()["organization_id"] == org2


def test_put_replacement_detach_plus_organization_change_allowed(
    client: TestClient, tenanta: dict
) -> None:
    org2 = _second_org(client, tenanta)
    parent = _new_dept(client, tenanta, name="Put Parent")
    child = _new_dept(client, tenanta, name="Put Child", parent_department_id=parent["id"])

    resp = client.put(
        f"{DEPARTMENTS}/{child['id']}",
        headers=tenanta["headers"],
        json={
            "name": "Put Child Replaced",
            "department_type": "FUNCTIONAL",
            "parent_department_id": None,
            "organization_id": org2,
            "version_no": child["version_no"],
        },
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["parent_department_id"] is None
    assert resp.json()["organization_id"] == org2


def test_organization_change_invalid_org_returns_404(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    dept = _new_dept(client, tenanta, name="Bad Org")
    foreign_org = client.get(f"{ORGANIZATIONS}/root", headers=tenantb["headers"]).json()["id"]

    unknown = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"organization_id": str(uuid.uuid4()), "version_no": dept["version_no"]},
    )
    assert unknown.status_code == 404, unknown.text

    foreign = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"organization_id": foreign_org, "version_no": dept["version_no"]},
    )
    assert foreign.status_code == 404, foreign.text

    # soft-deleted organization
    org3 = _second_org(client, tenanta)
    shown = client.get(f"{ORGANIZATIONS}/{org3}", headers=tenanta["headers"])
    assert shown.status_code == 200, shown.text
    removed = client.delete(f"{ORGANIZATIONS}/{org3}", headers=tenanta["headers"])
    assert removed.status_code == 204, removed.text
    deleted_org = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"organization_id": org3, "version_no": dept["version_no"]},
    )
    assert deleted_org.status_code == 404, deleted_org.text


def test_no_silent_reparenting_on_move_and_update(
    client: TestClient, tenanta: dict
) -> None:
    root = _new_dept(client, tenanta, name="Silent Root")
    child = _new_dept(client, tenanta, name="Silent Child", parent_department_id=root["id"])
    other = _new_dept(client, tenanta, name="Silent Other")

    # updating unrelated fields never changes the parent
    patched = client.patch(
        f"{DEPARTMENTS}/{child['id']}",
        headers=tenanta["headers"],
        json={"name": "Silent Child 2", "version_no": child["version_no"]},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["parent_department_id"] == root["id"]

    # moving 'other' does not touch 'child'
    moved = client.patch(
        f"{DEPARTMENTS}/{other['id']}/move",
        headers=tenanta["headers"],
        json={"parent_department_id": root["id"], "version_no": other["version_no"]},
    )
    assert moved.status_code == 200, moved.text
    unchanged = client.get(f"{DEPARTMENTS}/{child['id']}", headers=tenanta["headers"])
    assert unchanged.json()["parent_department_id"] == root["id"]


# ==================================================================== F. Branch
def test_branch_nullable_and_same_tenant(client: TestClient, tenanta: dict) -> None:
    no_branch = _new_dept(client, tenanta, name="No Branch")
    assert no_branch["branch_id"] is None

    branch_id = _create_branch(client, tenanta)
    with_branch = _new_dept(client, tenanta, name="With Branch", branch_id=branch_id)
    assert with_branch["branch_id"] == branch_id


def test_branch_deleted_or_foreign_rejected(
    client: TestClient, tenanta: dict, tenantb: dict
) -> None:
    branch_id = _create_branch(client, tenanta)
    assert client.delete(f"{BRANCHES}/{branch_id}", headers=tenanta["headers"]).status_code == 204
    assert _create_dept(client, tenanta, name="Deleted Branch", branch_id=branch_id).status_code == 404

    foreign_branch = _create_branch(client, tenantb)
    assert _create_dept(client, tenanta, name="Foreign Branch", branch_id=foreign_branch).status_code == 404


def test_branch_organization_mismatch_allowed(client: TestClient, tenanta: dict) -> None:
    """C-N10: the branch does not have to belong to the department's organization."""
    org2 = _second_org(client, tenanta)
    branch_org1 = _create_branch(client, tenanta, org_id=tenanta["org_id"])
    resp = _create_dept(
        client, tenanta, name="Mismatch Dept", organization_id=org2, branch_id=branch_org1
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["branch_id"] == branch_org1


# =================================================================== G. Status
def test_status_lifecycle(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Lifecycle")

    inactive = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": dept["version_no"]},
    )
    assert inactive.status_code == 200, inactive.text

    active = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "ACTIVE", "version_no": inactive.json()["version_no"]},
    )
    assert active.status_code == 200, active.text

    # same-state is a no-op
    same = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "ACTIVE", "version_no": active.json()["version_no"]},
    )
    assert same.status_code == 200, same.text

    # ACTIVE -> ARCHIVED is not an approved transition (§5)
    illegal = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "ARCHIVED", "version_no": same.json()["version_no"]},
    )
    assert illegal.status_code == 422, illegal.text

    back = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "INACTIVE", "version_no": same.json()["version_no"]},
    )
    assert back.status_code == 200, back.text
    archived = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "ARCHIVED", "version_no": back.json()["version_no"]},
    )
    assert archived.status_code == 200, archived.text

    # ARCHIVED is terminal
    terminal = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "ACTIVE", "version_no": archived.json()["version_no"]},
    )
    assert terminal.status_code == 422, terminal.text

    unknown_value = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"status": "PENDING", "version_no": archived.json()["version_no"]},
    )
    assert unknown_value.status_code == 422


# ====================================================== H. Optimistic locking
def test_optimistic_locking(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Locking")
    stale = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"name": "Stale", "version_no": dept["version_no"] + 5},
    )
    assert stale.status_code == 409, stale.text

    updated = client.patch(
        f"{DEPARTMENTS}/{dept['id']}",
        headers=tenanta["headers"],
        json={"name": "Locking 2", "version_no": dept["version_no"]},
    )
    assert updated.json()["version_no"] == dept["version_no"] + 1

    stale_move = client.patch(
        f"{DEPARTMENTS}/{dept['id']}/move",
        headers=tenanta["headers"],
        json={"parent_department_id": None, "version_no": dept["version_no"]},
    )
    assert stale_move.status_code == 409, stale_move.text

    moved = client.patch(
        f"{DEPARTMENTS}/{dept['id']}/move",
        headers=tenanta["headers"],
        json={"parent_department_id": None, "version_no": updated.json()["version_no"]},
    )
    assert moved.status_code == 200, moved.text
    assert moved.json()["version_no"] == updated.json()["version_no"] + 1

    # reads never increment
    for _ in range(2):
        read = client.get(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"])
        assert read.json()["version_no"] == moved.json()["version_no"]


# ============================================================= I. Soft delete
def test_child_delete_guard_and_no_hard_delete(
    client: TestClient, tenanta: dict
) -> None:
    parent = _new_dept(client, tenanta, name="Guard Parent")
    _new_dept(client, tenanta, name="Guard Child", parent_department_id=parent["id"])

    blocked = client.delete(f"{DEPARTMENTS}/{parent['id']}", headers=tenanta["headers"])
    assert blocked.status_code == 422, blocked.text

    with platform_session() as db:
        row = db.scalars(
            select(Department).where(Department.department_id == uuid.UUID(parent["id"]))
        ).first()
        assert row is not None and row.is_deleted is False

    assert client.delete(f"{DEPARTMENTS}/{parent['id']}", headers=tenanta["headers"]).status_code == 422
    # still visible/updatable after the rejected delete
    assert client.get(f"{DEPARTMENTS}/{parent['id']}", headers=tenanta["headers"]).status_code == 200


def test_deleted_department_becomes_untouchable(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Untouchable")
    assert client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"]).status_code == 204

    assert (
        client.patch(
            f"{DEPARTMENTS}/{dept['id']}",
            headers=tenanta["headers"],
            json={"name": "Nope", "version_no": dept["version_no"]},
        ).status_code
        == 404
    )
    assert (
        client.patch(
            f"{DEPARTMENTS}/{dept['id']}/move",
            headers=tenanta["headers"],
            json={"parent_department_id": None, "version_no": dept["version_no"]},
        ).status_code
        == 404
    )
    assert client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"]).status_code == 404

    with platform_session() as db:
        row = db.scalars(
            select(Department).where(Department.department_id == uuid.UUID(dept["id"]))
        ).first()
        assert row is not None, "hard delete must never be performed"
        assert row.is_deleted is True


# ==================================================================== J. Export
def test_export_excludes_deleted_and_is_json(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Export Dept")
    assert client.delete(f"{DEPARTMENTS}/{dept['id']}", headers=tenanta["headers"]).status_code == 204

    resp = client.get(f"{DEPARTMENTS}/export", headers=tenanta["headers"])
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("application/json")
    ids = [row["id"] for row in resp.json()]
    assert dept["id"] not in ids
    assert all(isinstance(row["id"], str) for row in resp.json())


def test_recommended_department_warning_advisory(
    client: TestClient, platform_header: dict
) -> None:
    """BR-PF-045: advisory only — surfaced while the tenant still has no departments."""
    fresh = _new_tenant_admin(client, platform_header, "depw")

    empty = client.get(DEPARTMENTS, headers=fresh["headers"])
    assert empty.status_code == 200, empty.text
    assert empty.json()["items"] == []
    assert empty.json()["warnings"], "BR-PF-045 advisory expected on an empty tenant"
    # an empty tenant has no hierarchy to return (C-N8)
    assert client.get(f"{DEPARTMENTS}/hierarchy", headers=fresh["headers"]).status_code == 404

    created = _create_dept(client, fresh, name="First Dept")
    assert created.status_code == 201, created.text
    after = client.get(DEPARTMENTS, headers=fresh["headers"])
    assert after.json()["warnings"] == []


# ========================================================= K. Deferred scope
def test_deferred_scope_absent(client: TestClient, tenanta: dict) -> None:
    dept = _new_dept(client, tenanta, name="Scope Dept")

    # department_head_user_id is never accepted from the client (C-N12)
    with_head = _create_dept(client, tenanta, name="Head Attempt")
    assert with_head.status_code == 201, with_head.text
    assert with_head.json()["department_head_user_id"] is None

    with platform_session() as db:
        # no FK/relationship to users, and no users.department_id (PF-008)
        fk = db.execute(
            text(
                """
                SELECT 1 FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE c.contype = 'f' AND n.nspname = 'core' AND t.relname = 'department'
                  AND pg_get_constraintdef(c.oid) ILIKE '%users%'
                """
            )
        ).first()
        assert fk is None
        # PF-008 CORE (authorized 2026-09-21): users.department_id now exists — the previous
        # absence guard is superseded by the delivered PF-008 schema and is therefore asserted
        # in the positive direction only. BR-PF-043 department-head validation and the
        # department -> users FK remain PF-008-deferred (department_head_user_id has no FK).
        assert (
            db.execute(
                text(
                    "SELECT 1 FROM information_schema.columns WHERE table_schema='core' "
                    "AND table_name='users' AND column_name='department_id'"
                )
            ).first()
            is not None
        )
        # no persisted hierarchy level/path (C-N2)
        for column in ("level", "path"):
            assert (
                db.execute(
                    text(
                        "SELECT 1 FROM information_schema.columns WHERE table_schema='core' "
                        "AND table_name='department' AND column_name = :c"
                    ),
                    {"c": column},
                ).first()
                is None
            )

    # export is JSON only — no CSV/XLSX artefact endpoint is registered
    openapi_paths = set(client.get("/openapi.json").json()["paths"].keys())
    assert f"{DEPARTMENTS}/export.csv" not in openapi_paths
    csv_attempt = client.get(f"{DEPARTMENTS}/export.csv", headers=tenanta["headers"])
    assert csv_attempt.status_code in {404, 422}  # unknown path / not a UUID path param
    assert "csv" not in csv_attempt.headers.get("content-type", "")
    assert dept["id"]
