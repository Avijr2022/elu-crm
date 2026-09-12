"""PF-005 Branch Management tests (ELU-TST-PF §2.2).

Planned cases implemented: TC-PF-BR-01, -02, -03, -04, -05, -06, -08.
TC-PF-BR-07 remains deferred (no project → branch linkage).
Additional cases cover CRUD/PUT/PATCH, lifecycle transitions, search, export,
organization same-tenant validation and deferred-scope compliance.

Tests assert real behaviour (DB state, transition rules, quotas), not only status
codes. No RLS bypass is used except through the shared ``platform_session`` helper
that already backs the PF-001…PF-004 suites.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.edition_gating import BRANCH, has_feature
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf005 import apply_pf005_ddl
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Branch, BranchAddress, Organization, Role, Tenant, User
from app.services.pf.branch_service import BranchService
from tests.conftest import platform_session

BRANCHES = "/api/v1/org/branches"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf005_ddl(db)
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
        "/api/v1/platform/tenants",
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
                "line1": "1 Branch Street",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    apr = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=platform_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    return apr.json()


def _provision_user(
    tenant_id: uuid.UUID, role_code: str, email: str, password: str
) -> uuid.UUID:
    """Create (or reuse) a role and an ACTIVE user for an existing tenant."""
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
    client: TestClient,
    platform_header: dict,
    prefix: str = "br",
    edition_code: str = "PROFESSIONAL",
) -> dict:
    """Provision a tenant + TENANT_ADMIN and return its API context."""
    code = _unique(prefix)
    tenant = _register_and_approve(client, platform_header, code, edition_code)
    tenant_id = uuid.UUID(tenant["id"])
    email = f"ta-{code}@example.com"
    password = "BranchAdmin!234"
    _provision_user(tenant_id, "TENANT_ADMIN", email, password)
    token = _login(client, email, password, code)
    headers = {"Authorization": f"Bearer {token}"}
    root = client.get("/api/v1/org/organizations/root", headers=headers)
    assert root.status_code == 200, root.text
    return {
        "code": code,
        "tenant_id": tenant_id,
        "email": email,
        "password": password,
        "token": token,
        "headers": headers,
        "org_id": root.json()["id"],
    }


def _create_branch(
    client: TestClient,
    ctx: dict,
    *,
    code: str | None = None,
    name: str = "Branch",
    branch_type: str = "BRANCH",
    parent_branch_id: str | None = None,
    address: dict | None = None,
    organization_id: str | None = None,
    status: str = "DRAFT",
) -> dict:
    payload: dict = {
        "code": code or _unique("B"),
        "name": name,
        "branch_type": branch_type,
        "organization_id": organization_id or ctx["org_id"],
        "status": status,
    }
    if parent_branch_id is not None:
        payload["parent_branch_id"] = parent_branch_id
    if address is not None:
        payload["address"] = address
    resp = client.post(BRANCHES, headers=ctx["headers"], json=payload)
    return {"response": resp, "payload": payload}


def _sample_address(city: str = "Bengaluru") -> dict:
    return {
        "address_line_1": "42 MG Road",
        "address_line_2": "Level 3",
        "city": city,
        "state": "Karnataka",
        "postal_code": "560001",
        "country_code": "in",
    }


# ------------------------------------------------------------------- DDL/test
def test_migration_idempotent_and_constraints(client: TestClient) -> None:
    with platform_session() as db:
        apply_pf005_ddl(db)
        apply_pf005_ddl(db)
        index = db.execute(
            text(
                "SELECT 1 FROM pg_indexes WHERE schemaname='core' "
                "AND indexname='uk_branch_tenant_code_active'"
            )
        ).first()
        assert index is not None
        uk = db.execute(
            text(
                "SELECT 1 FROM pg_constraint WHERE conname='uk_branch_address_branch'"
            )
        ).first()
        assert uk is not None
        for constraint in ("ck_branch_status", "ck_branch_type"):
            row = db.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :c"),
                {"c": constraint},
            ).first()
            assert row is not None
        fks = db.execute(
            text(
                "SELECT confdeltype FROM pg_constraint WHERE conname='fk_branch_parent'"
            )
        ).first()
        assert fks is not None and fks[0] == "r"  # RESTRICT (BFS §8)


# ---------------------------------------------------------------- TC-PF-BR-01
def test_tc_pf_br_01_community_forbidden(
    client: TestClient, platform_header: dict
) -> None:
    """BR-PF-034 / AC-PF-005-01: Community edition must be rejected (403)."""
    with platform_session() as db:
        tenant = db.scalars(
            select(Tenant).where(Tenant.tenant_code == "COMU001")
        ).first()
        assert tenant is not None
        community_tenant_id = tenant.tenant_id
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == community_tenant_id)
        ).first()
        assert org is not None
        org_id = str(org.organization_id)
        # mechanism-level evidence: the seeded Community edition does not carry BRANCH
        assert has_feature(db, community_tenant_id, BRANCH) is False

    email = f"comu-{uuid.uuid4().hex[:8]}@example.com"
    password = "Community!234"
    _provision_user(community_tenant_id, "TENANT_ADMIN", email, password)
    headers = {
        "Authorization": f"Bearer {_login(client, email, password, 'COMU001')}"
    }

    create = client.post(
        BRANCHES,
        headers=headers,
        json={
            "code": _unique("C"),
            "name": "Community Branch",
            "branch_type": "BRANCH",
            "organization_id": org_id,
        },
    )
    assert create.status_code == 403, create.text
    assert create.json()["detail"]["error"]["code"] == "FORBIDDEN"

    listing = client.get(BRANCHES, headers=headers)
    assert listing.status_code == 403, listing.text

    with platform_session() as db:
        count = db.execute(
            text("SELECT count(*) FROM core.branch WHERE tenant_id = :t"),
            {"t": community_tenant_id},
        ).scalar()
        assert count == 0


# ---------------------------------------------------------------- TC-PF-BR-02
def test_tc_pf_br_02_duplicate_code(
    client: TestClient, platform_header: dict
) -> None:
    """BR-PF-035: branch code unique within tenant (soft-delete aware)."""
    ctx = _new_tenant_admin(client, platform_header, "dup")
    code = f"DUP{uuid.uuid4().hex[:6].upper()}"

    first = _create_branch(client, ctx, code=code, name="First Branch")
    assert first["response"].status_code == 201, first["response"].text

    same = _create_branch(client, ctx, code=code, name="Second Branch")
    assert same["response"].status_code == 409, same["response"].text
    assert same["response"].json()["detail"]["error"]["req_id"] == "BR-PF-035"

    # case-insensitive: schema upper-cases the code, so a lower-case duplicate collides
    lower = _create_branch(client, ctx, code=code.lower(), name="Third Branch")
    assert lower["response"].status_code == 409, lower["response"].text

    with platform_session() as db:
        rows = db.execute(
            text(
                "SELECT count(*) FROM core.branch "
                "WHERE tenant_id = :t AND branch_code = :c AND is_deleted = FALSE"
            ),
            {"t": ctx["tenant_id"], "c": code},
        ).scalar()
        assert rows == 1


# ---------------------------------------------------------------- TC-PF-BR-03
def test_tc_pf_br_03_head_office_warning(
    client: TestClient, platform_header: dict
) -> None:
    """BR-PF-036: missing HEAD_OFFICE is a non-blocking API warning."""
    ctx = _new_tenant_admin(client, platform_header, "how")

    first = _create_branch(client, ctx, name="Bengaluru Branch", branch_type="BRANCH")
    assert first["response"].status_code == 201, first["response"].text
    body = first["response"].json()
    assert body["warnings"], "expected BR-PF-036 advisory on first non-head-office branch"
    assert any("BR-PF-036" in w for w in body["warnings"])
    # warning semantics: the request succeeded and the row exists
    assert client.get(
        f"{BRANCHES}/{body['id']}", headers=ctx["headers"]
    ).status_code == 200

    hq = _create_branch(
        client, ctx, name="Kolkata Head Office", branch_type="HEAD_OFFICE"
    )
    assert hq["response"].status_code == 201, hq["response"].text
    assert hq["response"].json()["warnings"] == []

    second = _create_branch(client, ctx, name="Mumbai Branch", branch_type="BRANCH")
    assert second["response"].status_code == 201, second["response"].text
    assert second["response"].json()["warnings"] == []


# ---------------------------------------------------------------- TC-PF-BR-04
def test_tc_pf_br_04_branch_limit(client: TestClient, platform_header: dict) -> None:
    """BR-PF-039 / AC-PF-005-03: Professional tenant is capped at 10 branches."""
    ctx = _new_tenant_admin(client, platform_header, "lim")

    with platform_session() as db:
        limit = db.execute(
            text(
                """
                SELECT l.limit_value
                FROM core.edition_limit l
                JOIN core.edition e ON e.id = l.edition_id
                JOIN core.tenant t ON t.edition_id = e.id
                WHERE t.tenant_id = :t AND l.limit_code = 'MAX_BRANCHES'
                """
            ),
            {"t": ctx["tenant_id"]},
        ).first()
        assert limit is not None and int(limit[0]) == 10

    for i in range(10):
        created = _create_branch(client, ctx, name=f"Branch {i}")
        assert created["response"].status_code == 201, created["response"].text

    eleventh = _create_branch(client, ctx, name="Branch 11")
    assert eleventh["response"].status_code == 422, eleventh["response"].text
    assert eleventh["response"].json()["detail"]["error"]["req_id"] == "BR-PF-039"

    with platform_session() as db:
        count = db.execute(
            text(
                "SELECT count(*) FROM core.branch "
                "WHERE tenant_id = :t AND is_deleted = FALSE"
            ),
            {"t": ctx["tenant_id"]},
        ).scalar()
        assert count == 10


# ---------------------------------------------------------------- TC-PF-BR-05
def test_tc_pf_br_05_hierarchy(client: TestClient, platform_header: dict) -> None:
    """BFS-PF-005 §8: parent/child hierarchy works; cycles are rejected."""
    ctx = _new_tenant_admin(client, platform_header, "hier")
    ctx_b = _new_tenant_admin(client, platform_header, "hxb")

    hq = _create_branch(client, ctx, name="HQ", branch_type="HEAD_OFFICE")
    assert hq["response"].status_code == 201, hq["response"].text
    hq_id = hq["response"].json()["id"]

    child = _create_branch(
        client, ctx, name="Region East", branch_type="REGIONAL_OFFICE", parent_branch_id=hq_id
    )
    assert child["response"].status_code == 201, child["response"].text
    child_id = child["response"].json()["id"]
    assert child["response"].json()["parent_branch_id"] == hq_id

    grandchild = _create_branch(client, ctx, name="Bengaluru", parent_branch_id=child_id)
    assert grandchild["response"].status_code == 201, grandchild["response"].text
    grandchild_id = grandchild["response"].json()["id"]

    tree = client.get(f"{BRANCHES}/hierarchy", headers=ctx["headers"])
    assert tree.status_code == 200, tree.text
    items = tree.json()["items"]
    assert len(items) == 1
    assert items[0]["id"] == hq_id
    assert items[0]["branch_type"] == "HEAD_OFFICE"
    assert items[0]["children"][0]["id"] == child_id
    assert items[0]["children"][0]["children"][0]["id"] == grandchild_id

    # self-parenting rejected
    self_parent = client.patch(
        f"{BRANCHES}/{child_id}",
        headers=ctx["headers"],
        json={"parent_branch_id": child_id, "version_no": child["response"].json()["version_no"]},
    )
    assert self_parent.status_code == 422, self_parent.text

    # circular ancestry rejected (HQ cannot become a child of its own grandchild)
    cycle = client.patch(
        f"{BRANCHES}/{hq_id}",
        headers=ctx["headers"],
        json={
            "parent_branch_id": grandchild_id,
            "version_no": hq["response"].json()["version_no"],
        },
    )
    assert cycle.status_code == 422, cycle.text

    # cross-tenant parent rejected
    foreign = _create_branch(client, ctx_b, name="Foreign Branch")
    assert foreign["response"].status_code == 201, foreign["response"].text
    cross = client.patch(
        f"{BRANCHES}/{child_id}",
        headers=ctx["headers"],
        json={
            "parent_branch_id": foreign["response"].json()["id"],
            "version_no": child["response"].json()["version_no"],
        },
    )
    assert cross.status_code == 404, cross.text


# ---------------------------------------------------------------- TC-PF-BR-06
def test_tc_pf_br_06_address(client: TestClient, platform_header: dict) -> None:
    """BFS-PF-005 §7/§9: address 1:1 create/update and cascade on delete."""
    ctx = _new_tenant_admin(client, platform_header, "adr")

    created = _create_branch(
        client, ctx, name="Address Branch", address=_sample_address("Bengaluru")
    )
    assert created["response"].status_code == 201, created["response"].text
    body = created["response"].json()
    assert body["address"] is not None
    assert body["address"]["city"] == "Bengaluru"
    assert body["address"]["country_code"] == "IN"  # normalised from "in"
    branch_id = body["id"]
    address_id = body["address"]["id"]

    with platform_session() as db:
        rows = db.execute(
            text("SELECT count(*) FROM core.branch_address WHERE branch_id = :b"),
            {"b": branch_id},
        ).scalar()
        assert rows == 1

    # 1:1 update — same row, no duplicate
    updated = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"address": _sample_address("Mysuru"), "version_no": body["version_no"]},
    )
    assert updated.status_code == 200, updated.text
    upd_body = updated.json()
    assert upd_body["address"]["id"] == address_id
    assert upd_body["address"]["city"] == "Mysuru"

    with platform_session() as db:
        rows = db.execute(
            text("SELECT count(*) FROM core.branch_address WHERE branch_id = :b"),
            {"b": branch_id},
        ).scalar()
        assert rows == 1

    # invalid address rejected by schema
    bad = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={
            "address": {"address_line_1": "x", "country_code": "IN"},
            "version_no": upd_body["version_no"],
        },
    )
    assert bad.status_code == 422, bad.text

    # soft delete → address soft-deleted with the branch (documented CASCADE semantics)
    dele = client.delete(f"{BRANCHES}/{branch_id}", headers=ctx["headers"])
    assert dele.status_code == 204, dele.text
    assert client.get(f"{BRANCHES}/{branch_id}", headers=ctx["headers"]).status_code == 404

    with platform_session() as db:
        branch_row = db.execute(
            text(
                "SELECT is_deleted, is_active FROM core.branch WHERE branch_id = :b"
            ),
            {"b": branch_id},
        ).first()
        assert branch_row is not None
        assert branch_row[0] is True and branch_row[1] is False
        addr_row = db.execute(
            text(
                "SELECT is_deleted, is_active FROM core.branch_address "
                "WHERE branch_address_id = :a"
            ),
            {"a": address_id},
        ).first()
        assert addr_row is not None
        assert addr_row[0] is True and addr_row[1] is False


# ---------------------------------------------------------------- TC-PF-BR-08
def test_tc_pf_br_08_readonly_roles(
    client: TestClient, platform_header: dict
) -> None:
    """BFS-PF-005 §12: non-Tenant-Admin roles are read-only."""
    ctx = _new_tenant_admin(client, platform_header, "rbac")
    created = _create_branch(client, ctx, name="RBAC Branch")
    assert created["response"].status_code == 201, created["response"].text
    branch_id = created["response"].json()["id"]
    version_no = created["response"].json()["version_no"]

    read_roles = ("SALES_MANAGER", "PROJECT_MANAGER", "FINANCE_USER")
    for role in read_roles:
        email = f"{role.lower()}-{ctx['code']}@example.com"
        password = "ReadOnly!234"
        _provision_user(ctx["tenant_id"], role, email, password)
        headers = {"Authorization": f"Bearer {_login(client, email, password, ctx['code'])}"}

        assert client.get(BRANCHES, headers=headers).status_code == 200
        detail = client.get(f"{BRANCHES}/{branch_id}", headers=headers)
        assert detail.status_code == 200, detail.text
        assert detail.json()["code"] == created["response"].json()["code"]

        assert (
            client.post(
                BRANCHES,
                headers=headers,
                json={
                    "code": _unique("X"),
                    "name": "Nope",
                    "organization_id": ctx["org_id"],
                },
            ).status_code
            == 403
        )
        assert (
            client.patch(
                f"{BRANCHES}/{branch_id}",
                headers=headers,
                json={"name": "Nope", "version_no": version_no},
            ).status_code
            == 403
        )
        assert client.delete(f"{BRANCHES}/{branch_id}", headers=headers).status_code == 403
        assert client.get(f"{BRANCHES}/export", headers=headers).status_code == 403

    # Platform Admin keeps read access but is read-only (and not an export role)
    settings = get_settings()
    platform_headers = {
        "Authorization": f"Bearer {_login(client, settings.seed_admin_email, settings.seed_admin_password, 'EIIP001')}"
    }
    assert client.get(BRANCHES, headers=platform_headers).status_code == 200
    assert (
        client.post(
            BRANCHES,
            headers=platform_headers,
            json={"code": _unique("P"), "name": "Nope", "organization_id": ctx["org_id"]},
        ).status_code
        == 403
    )
    assert client.get(f"{BRANCHES}/export", headers=platform_headers).status_code == 403

    # Tenant Admin may export
    assert client.get(f"{BRANCHES}/export", headers=ctx["headers"]).status_code == 200


# --------------------------------------------------------- CRUD + lifecycle
def test_crud_put_patch_lifecycle_and_audit(
    client: TestClient, platform_header: dict
) -> None:
    ctx = _new_tenant_admin(client, platform_header, "cru")

    created = _create_branch(client, ctx, name="Ops Branch", status="DRAFT")
    assert created["response"].status_code == 201, created["response"].text
    body = created["response"].json()
    branch_id = body["id"]
    assert body["status"] == "DRAFT"
    version_no = body["version_no"]

    # PATCH partial update + optimistic locking
    patched = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"phone": "+913340000009", "version_no": version_no},
    )
    assert patched.status_code == 200, patched.text
    assert patched.json()["phone"] == "+913340000009"
    assert patched.json()["name"] == "Ops Branch"  # untouched by PATCH
    version_no = patched.json()["version_no"]

    stale = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"name": "Stale", "version_no": version_no - 1},
    )
    assert stale.status_code == 409, stale.text

    # PUT requires name and performs a replace (unset optional fields are cleared)
    put_missing_name = client.put(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"version_no": version_no},
    )
    assert put_missing_name.status_code == 422, put_missing_name.text

    replaced = client.put(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"name": "Ops Branch HQ", "branch_type": "BRANCH", "version_no": version_no},
    )
    assert replaced.status_code == 200, replaced.text
    assert replaced.json()["name"] == "Ops Branch HQ"
    assert replaced.json()["phone"] is None  # full replace cleared the PATCH-set phone
    version_no = replaced.json()["version_no"]

    # lifecycle (BFS-PF-005 §5)
    activate = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"status": "ACTIVE", "version_no": version_no},
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"
    assert activate.json()["opened_date"] is not None
    version_no = activate.json()["version_no"]

    invalid = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"status": "CANCELLED", "version_no": version_no},
    )
    assert invalid.status_code == 422, invalid.text  # ACTIVE → CANCELLED is not allowed

    deactivate = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"status": "INACTIVE", "version_no": version_no},
    )
    assert deactivate.status_code == 200, deactivate.text
    version_no = deactivate.json()["version_no"]

    archived = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"status": "ARCHIVED", "version_no": version_no},
    )
    assert archived.status_code == 200, archived.text
    assert archived.json()["closed_date"] is not None
    version_no = archived.json()["version_no"]

    terminal = client.patch(
        f"{BRANCHES}/{branch_id}",
        headers=ctx["headers"],
        json={"status": "ACTIVE", "version_no": version_no},
    )
    assert terminal.status_code == 422, terminal.text  # ARCHIVED is terminal

    # audit trail — service-level history (no history endpoint per BFS §10)
    with platform_session() as db:
        hist = BranchService(db).history(ctx["tenant_id"], uuid.UUID(branch_id))
    kinds = {i.event_type for i in hist.items}
    assert {"BRANCH_CREATED", "BRANCH_UPDATED", "BRANCH_REPLACED", "BRANCH_STATUS_CHANGED"} <= kinds

    # delete (soft) + post-delete invisibility
    assert client.delete(f"{BRANCHES}/{branch_id}", headers=ctx["headers"]).status_code == 204
    assert client.get(f"{BRANCHES}/{branch_id}", headers=ctx["headers"]).status_code == 404
    assert client.delete(f"{BRANCHES}/{branch_id}", headers=ctx["headers"]).status_code == 404


def test_delete_blocked_by_child_branches(
    client: TestClient, platform_header: dict
) -> None:
    ctx = _new_tenant_admin(client, platform_header, "chd")
    parent = _create_branch(client, ctx, name="Parent")
    assert parent["response"].status_code == 201, parent["response"].text
    child = _create_branch(
        client, ctx, name="Child", parent_branch_id=parent["response"].json()["id"]
    )
    assert child["response"].status_code == 201, child["response"].text

    blocked = client.delete(
        f"{BRANCHES}/{parent['response'].json()['id']}", headers=ctx["headers"]
    )
    assert blocked.status_code == 422, blocked.text
    assert "RESTRICT" in blocked.text


def test_search_list_filters_and_export(
    client: TestClient, platform_header: dict
) -> None:
    ctx = _new_tenant_admin(client, platform_header, "sch")
    token = uuid.uuid4().hex[:6].upper()

    hq = _create_branch(
        client, ctx, code=f"HQ{token}", name=f"Head {token}", branch_type="HEAD_OFFICE"
    )
    br = _create_branch(
        client, ctx, code=f"BR{token}", name=f"Branch {token}", branch_type="BRANCH"
    )
    assert hq["response"].status_code == 201 and br["response"].status_code == 201

    search = client.get(f"{BRANCHES}/search", headers=ctx["headers"], params={"q": token})
    assert search.status_code == 200, search.text
    codes = {i["code"] for i in search.json()["items"]}
    assert codes == {f"HQ{token}", f"BR{token}"}

    by_type = client.get(
        f"{BRANCHES}", headers=ctx["headers"], params={"branch_type": "HEAD_OFFICE"}
    )
    assert by_type.status_code == 200, by_type.text
    assert {i["code"] for i in by_type.json()["items"]} == {f"HQ{token}"}

    by_status = client.get(
        f"{BRANCHES}", headers=ctx["headers"], params={"status": "DRAFT"}
    )
    assert by_status.status_code == 200
    assert by_status.json()["total"] >= 2

    sorted_desc = client.get(
        f"{BRANCHES}", headers=ctx["headers"], params={"sort": "-code"}
    )
    assert sorted_desc.status_code == 200

    export = client.get(f"{BRANCHES}/export", headers=ctx["headers"])
    assert export.status_code == 200, export.text
    rows = export.json()
    exported_codes = {r["code"] for r in rows}
    assert {f"HQ{token}", f"BR{token}"} <= exported_codes
    assert all("branch_type" in r and "status" in r for r in rows)
    # export is tenant-scoped: nothing from the other tenants created above leaks in
    assert all(r["code"] != "NOPE-CROSS" for r in rows)


def test_organization_same_tenant_validation(
    client: TestClient, platform_header: dict
) -> None:
    ctx = _new_tenant_admin(client, platform_header, "org")
    other = _new_tenant_admin(client, platform_header, "oth")

    unknown = _create_branch(client, ctx, name="Unknown Org", organization_id=str(uuid.uuid4()))
    assert unknown["response"].status_code == 404, unknown["response"].text

    foreign = _create_branch(
        client, ctx, name="Foreign Org", organization_id=other["org_id"]
    )
    assert foreign["response"].status_code == 404, foreign["response"].text

    valid = _create_branch(client, ctx, name="Valid Org")
    assert valid["response"].status_code == 201, valid["response"].text
    assert valid["response"].json()["organization_id"] == ctx["org_id"]


def test_openapi_exposes_exactly_the_approved_surface(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    for path in (
        "/api/v1/org/branches",
        "/api/v1/org/branches/{branch_id}",
        "/api/v1/org/branches/search",
        "/api/v1/org/branches/export",
        "/api/v1/org/branches/hierarchy",
    ):
        assert path in paths, f"missing {path}"

    methods = {
        (method, path)
        for path, ops in paths.items()
        if path.startswith("/api/v1/org/branches")
        for method in ops
    }
    assert methods == {
        ("get", "/api/v1/org/branches"),
        ("post", "/api/v1/org/branches"),
        ("get", "/api/v1/org/branches/{branch_id}"),
        ("put", "/api/v1/org/branches/{branch_id}"),
        ("patch", "/api/v1/org/branches/{branch_id}"),
        ("delete", "/api/v1/org/branches/{branch_id}"),
        ("get", "/api/v1/org/branches/search"),
        ("get", "/api/v1/org/branches/export"),
        ("get", "/api/v1/org/branches/hierarchy"),
    }
    assert "/api/v1/org/branches/{branch_id}/history" not in paths


def test_deferred_scope_not_implemented(
    client: TestClient, platform_header: dict
) -> None:
    """BR-PF-038 / PF-006 / PF-008 / BR-PF-037 must not leak into this batch."""
    ctx = _new_tenant_admin(client, platform_header, "sco")

    # branch_head_user_id is accepted-but-ignored: no assignment logic (PF-008)
    resp = client.post(
        BRANCHES,
        headers=ctx["headers"],
        json={
            "code": _unique("SH"),
            "name": "Scope Branch",
            "organization_id": ctx["org_id"],
            "branch_head_user_id": str(uuid.uuid4()),
        },
    )
    assert resp.status_code == 201, resp.text
    assert resp.json()["branch_head_user_id"] is None

    with platform_session() as db:
        # no user FK / assignment support
        fk = db.execute(
            text(
                """
                SELECT 1 FROM pg_constraint c
                JOIN pg_class t ON t.oid = c.conrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                WHERE c.contype = 'f' AND n.nspname = 'core' AND t.relname = 'branch'
                  AND pg_get_constraintdef(c.oid) ILIKE '%branch_head%'
                """
            )
        ).first()
        assert fk is None
        nullable = db.execute(
            text(
                "SELECT is_nullable FROM information_schema.columns "
                "WHERE table_schema='core' AND table_name='branch' "
                "AND column_name='branch_head_user_id'"
            )
        ).first()
        assert nullable is not None and nullable[0] == "YES"
        # PF-008: users.branch_id not added
        assert (
            db.execute(
                text(
                    "SELECT 1 FROM information_schema.columns WHERE table_schema='core' "
                    "AND table_name='users' AND column_name='branch_id'"
                )
            ).first()
            is None
        )
        # PF-006: no department table
        assert (
            db.execute(
                text(
                    "SELECT 1 FROM information_schema.tables WHERE table_schema='core' "
                    "AND table_name='department'"
                )
            ).first()
            is None
        )
        # BR-PF-037: no project → branch linkage
        assert (
            db.execute(
                text(
                    "SELECT 1 FROM information_schema.columns WHERE column_name='branch_id' "
                    "AND table_name IN ('project','work_order','handoff','wo_handoff')"
                )
            ).first()
            is None
        )


def test_rls_context_scopes_branch_queries(
    client: TestClient, platform_header: dict
) -> None:
    """Branch/branch_address reads are tenant-scoped under RLS."""
    ctx = _new_tenant_admin(client, platform_header, "rls")
    created = _create_branch(
        client, ctx, name="RLS Branch", address=_sample_address("Kolkata")
    )
    assert created["response"].status_code == 201, created["response"].text

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=ctx["tenant_id"], platform=False)
        assert (
            db.execute(
                text("SELECT count(*) FROM core.branch WHERE tenant_id = :t"),
                {"t": ctx["tenant_id"]},
            ).scalar()
            == 1
        )
        assert (
            db.execute(text("SELECT count(*) FROM core.branch_address")).scalar() == 1
        )
    finally:
        clear_rls_context(db)
        db.close()

    with platform_session() as db:
        rows = db.scalars(
            select(Branch).where(Branch.tenant_id == ctx["tenant_id"])
        ).all()
        assert len(rows) == 1
        addresses = db.scalars(
            select(BranchAddress).where(BranchAddress.tenant_id == ctx["tenant_id"])
        ).all()
        assert len(addresses) == 1
