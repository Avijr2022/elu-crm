"""PF-001 Edition Management tests (ELU-BFS-PF-001 / ELU-TST-PF related)."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import Role, User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    # Ensure admin is PLATFORM_ADMIN (re-seed path may have upgraded)
    db = SessionLocal()
    try:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None, "Seed admin missing — start API once to seed"
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == "PLATFORM_ADMIN",
            )
        ).first()
        if role is None:
            role = Role(
                tenant_id=admin.tenant_id,
                role_code="PLATFORM_ADMIN",
                role_name="Platform Admin",
                is_system=True,
            )
            db.add(role)
            db.flush()
        admin.role_id = role.role_id
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    finally:
        db.close()

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


def test_list_editions(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/platform/editions", headers=auth_header)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] >= 3
    codes = {i["code"] for i in body["items"]}
    assert {"COMMUNITY", "PROFESSIONAL", "ENTERPRISE"} <= codes


def test_get_tenant_edition(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/tenant/edition", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["code"] == "PROFESSIONAL"
    assert resp.json()["status"] == "ACTIVE"


def test_create_publish_deprecate_flow(client: TestClient, auth_header: dict) -> None:
    create = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": "PF001_TEST",
            "name": "PF001 Test Edition",
            "description": "Automated test draft",
            "display_order": 99,
            "features": [
                {"feature_code": "CRM_LEAD", "is_enabled": True, "is_visible": True}
            ],
            "limits": [
                {
                    "limit_code": "MAX_USERS",
                    "limit_name": "Maximum users",
                    "limit_value": "5",
                    "limit_unit": "users",
                },
                {
                    "limit_code": "MAX_STORAGE_GB",
                    "limit_name": "Storage",
                    "limit_value": "5",
                    "limit_unit": "GB",
                },
                {
                    "limit_code": "MAX_ROLES",
                    "limit_name": "Roles",
                    "limit_value": "5",
                    "limit_unit": "roles",
                },
            ],
        },
    )
    assert create.status_code == 201, create.text
    edition = create.json()
    assert edition["status"] == "DRAFT"
    edition_id = edition["id"]
    version = edition["version_no"]

    # Publish without bump conflict
    pub = client.post(
        f"/api/v1/platform/editions/{edition_id}/publish",
        headers=auth_header,
        json={"version_no": version},
    )
    assert pub.status_code == 200, pub.text
    assert pub.json()["status"] == "ACTIVE"
    version = pub.json()["version_no"]

    dep = client.post(
        f"/api/v1/platform/editions/{edition_id}/deprecate",
        headers=auth_header,
        json={"reason": "End of test sale", "version_no": version},
    )
    assert dep.status_code == 200, dep.text
    assert dep.json()["status"] == "DEPRECATED"


def test_publish_requires_feature_and_limit(
    client: TestClient, auth_header: dict
) -> None:
    create = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": "PF001_EMPTY",
            "name": "Empty Draft",
            "features": [],
            "limits": [],
        },
    )
    assert create.status_code == 201, create.text
    edition_id = create.json()["id"]
    version = create.json()["version_no"]
    pub = client.post(
        f"/api/v1/platform/editions/{edition_id}/publish",
        headers=auth_header,
        json={"version_no": version},
    )
    assert pub.status_code == 422, pub.text
    assert "feature" in pub.json()["detail"]["error"]["message"].lower()


def test_limit_below_community_baseline(
    client: TestClient, auth_header: dict
) -> None:
    resp = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": "PF001_LOW",
            "name": "Too Low",
            "features": [
                {"feature_code": "CRM_LEAD", "is_enabled": True, "is_visible": True}
            ],
            "limits": [
                {
                    "limit_code": "MAX_USERS",
                    "limit_name": "Users",
                    "limit_value": "1",
                    "limit_unit": "users",
                }
            ],
        },
    )
    assert resp.status_code == 422, resp.text


def test_export_matrix(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/platform/editions/export", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)
    assert any(row["code"] == "ENTERPRISE" for row in resp.json())


def test_openapi_includes_editions(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    paths = spec["paths"]
    assert "/api/v1/platform/editions" in paths
    assert "/api/v1/tenant/edition" in paths
