"""PF-004 Organization Management tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf004 import apply_pf004_ddl
from app.main import app
from app.models.pf import Role, User
from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf004_ddl(db)
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
def tenant_admin_token(client: TestClient, platform_token: str) -> str:
    """BFS §12: mutations require TENANT_ADMIN (Platform Admin is read-only)."""
    email = f"ta-org-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    password = "TenantAdmin!234"
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == "TENANT_ADMIN",
            )
        ).first()
        assert role is not None
        user = User(
            tenant_id=admin.tenant_id,
            organization_id=admin.organization_id,
            role_id=role.role_id,
            employee_code=f"TA{uuid.uuid4().hex[:6].upper()}",
            first_name="Tenant",
            last_name="Admin",
            display_name="Tenant Admin Org",
            email=email,
            password_hash=hash_password(password),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()

    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": "EIIP001"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def platform_header(platform_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {platform_token}"}


@pytest.fixture(scope="module")
def auth_header(tenant_admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {tenant_admin_token}"}


def test_migration_idempotent(client: TestClient) -> None:
    with platform_session() as db:
        apply_pf004_ddl(db)
        apply_pf004_ddl(db)
        row = db.execute(
            text(
                "SELECT 1 FROM pg_indexes WHERE schemaname='core' "
                "AND indexname='uk_organization_one_root'"
            )
        ).first()
        assert row is not None
        soft = db.execute(
            text(
                "SELECT 1 FROM pg_indexes WHERE schemaname='core' "
                "AND indexname='uk_organization_tenant_code_active'"
            )
        ).first()
        assert soft is not None


def test_platform_admin_read_only_write_forbidden(
    client: TestClient, platform_header: dict
) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=platform_header)
    assert root.status_code == 200, root.text
    resp = client.patch(
        f"/api/v1/org/organizations/{root.json()['id']}",
        headers=platform_header,
        json={"name": "Should Fail", "version_no": root.json()["version_no"]},
    )
    assert resp.status_code == 403, resp.text


def test_ac_pf_004_01_one_root(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header)
    assert root.status_code == 200, root.text
    assert root.json()["is_root"] is True
    listing = client.get("/api/v1/org/organizations", headers=auth_header)
    assert listing.status_code == 200
    roots = [i for i in listing.json()["items"] if i["is_root"]]
    assert len(roots) == 1


def test_ac_pf_004_02_invalid_gstin(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    resp = client.patch(
        f"/api/v1/org/organizations/{root['id']}",
        headers=auth_header,
        json={"gstin": "BAD", "version_no": root["version_no"]},
    )
    assert resp.status_code == 422, resp.text


def test_ac_pf_004_03_root_cannot_delete(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    resp = client.delete(
        f"/api/v1/org/organizations/{root['id']}", headers=auth_header
    )
    assert resp.status_code == 422, resp.text
    assert "BR-PF-031" in resp.text or "ROOT" in resp.text.upper()


def test_update_profile_and_hierarchy(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    upd = client.patch(
        f"/api/v1/org/organizations/{root['id']}",
        headers=auth_header,
        json={
            "name": "Euphoria Infotech HO",
            "legal_name": "Euphoria Infotech (I) Limited",
            "gstin": "19AABCE1234F1Z5",
            "pan": "AABCE1234F",
            "fiscal_year_start_month": 4,
            "version_no": root["version_no"],
        },
    )
    assert upd.status_code == 200, upd.text
    body = upd.json()
    assert body["gstin"] == "19AABCE1234F1Z5"
    assert body["pan"] == "AABCE1234F"
    assert body["version_no"] == root["version_no"] + 1

    tree = client.get(
        f"/api/v1/org/organizations/{body['id']}/hierarchy", headers=auth_header
    )
    assert tree.status_code == 200, tree.text
    assert tree.json()["is_root"] is True


def test_create_child_and_reject_second_root(
    client: TestClient, auth_header: dict
) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    bad = client.post(
        "/api/v1/org/organizations",
        headers=auth_header,
        json={"code": f"X{uuid.uuid4().hex[:6].upper()}", "name": "No Root"},
    )
    assert bad.status_code == 422, bad.text

    code = f"BR{uuid.uuid4().hex[:6].upper()}"
    child = client.post(
        "/api/v1/org/organizations",
        headers=auth_header,
        json={
            "code": code,
            "name": "Bengaluru Branch",
            "organization_type": "Branch",
            "parent_organization_id": root["id"],
        },
    )
    assert child.status_code == 201, child.text
    assert child.json()["is_root"] is False
    assert child.json()["parent_organization_id"] == root["id"]

    dele = client.delete(
        f"/api/v1/org/organizations/{child.json()['id']}", headers=auth_header
    )
    assert dele.status_code == 204, dele.text


def test_list_sort_param(client: TestClient, auth_header: dict) -> None:
    resp = client.get(
        "/api/v1/org/organizations",
        headers=auth_header,
        params={"sort": "-code"},
    )
    assert resp.status_code == 200, resp.text


def test_openapi_includes_org_paths(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/org/organizations" in paths
    assert "/api/v1/org/organizations/root" in paths
    assert "/api/v1/org/organizations/{org_id}/history" in paths


def test_address_id_fk_and_validation(client: TestClient, auth_header: dict) -> None:
    with platform_session() as db:
        apply_pf004_ddl(db)
        row = db.execute(
            text(
                "SELECT 1 FROM pg_constraint WHERE conname = 'fk_organization_address'"
            )
        ).first()
        assert row is not None

    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    bad = client.patch(
        f"/api/v1/org/organizations/{root['id']}",
        headers=auth_header,
        json={
            "address_id": str(uuid.uuid4()),
            "version_no": root["version_no"],
        },
    )
    assert bad.status_code == 422, bad.text


def test_organization_history(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    upd = client.patch(
        f"/api/v1/org/organizations/{root['id']}",
        headers=auth_header,
        json={"name": root["name"], "version_no": root["version_no"]},
    )
    assert upd.status_code == 200, upd.text
    hist = client.get(
        f"/api/v1/org/organizations/{root['id']}/history",
        headers=auth_header,
    )
    assert hist.status_code == 200, hist.text
    assert hist.json()["total"] >= 1
    assert any(
        i["event_type"] == "ORGANIZATION_UPDATED" for i in hist.json()["items"]
    )


def test_put_replace_requires_name(client: TestClient, auth_header: dict) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=auth_header).json()
    resp = client.put(
        f"/api/v1/org/organizations/{root['id']}",
        headers=auth_header,
        json={"version_no": root["version_no"]},
    )
    assert resp.status_code == 422, resp.text


def test_rollback_script_exists() -> None:
    from pathlib import Path

    path = (
        Path(__file__).resolve().parents[2]
        / "Database"
        / "03_PlatformFoundation"
        / "013_organization_pf004_rollback.sql"
    )
    assert path.is_file()
    text_sql = path.read_text(encoding="utf-8")
    assert "DROP COLUMN IF EXISTS address_id" in text_sql
    assert "fk_organization_address" in text_sql
