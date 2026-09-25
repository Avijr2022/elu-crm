"""PF-001 Edition Management tests — repeatable (unique codes per run)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import AuditEvent, Role, User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
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


def _unique_code(prefix: str = "T") -> str:
    return f"{prefix}{uuid.uuid4().hex[:10].upper()}"


def _baseline_limits() -> list[dict]:
    return [
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
    ]


def test_list_editions(client: TestClient, auth_header: dict) -> None:
    codes: set[str] = set()
    page = 1
    total = 1
    while (page - 1) * 100 < total:
        resp = client.get(
            "/api/v1/platform/editions",
            headers=auth_header,
            params={"page": page, "page_size": 100},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        total = int(body["total"])
        codes |= {i["code"] for i in body["items"]}
        page += 1
    assert total >= 3
    assert {"COMMUNITY", "PROFESSIONAL", "ENTERPRISE"} <= codes


def test_get_tenant_edition(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/tenant/edition", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["code"] == "PROFESSIONAL"
    assert resp.json()["status"] == "ACTIVE"


def test_create_publish_deprecate_flow(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("PUB")
    create = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": code,
            "name": "PF001 Test Edition",
            "description": "Automated test draft",
            "display_order": 99,
            "features": [
                {"feature_code": "CRM_LEAD", "is_enabled": True, "is_visible": True}
            ],
            "limits": _baseline_limits(),
        },
    )
    assert create.status_code == 201, create.text
    edition = create.json()
    assert edition["status"] == "DRAFT"
    assert edition["code"] == code
    edition_id = edition["id"]
    version = edition["version_no"]

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

    # Audit events persisted
    with platform_session() as db:
        events = list(
            db.scalars(
                select(AuditEvent).where(AuditEvent.entity_id == uuid.UUID(edition_id))
            ).all()
        )
        types = {e.event_type for e in events}
        assert "EDITION_CREATED" in types
        assert "EDITION_PUBLISHED" in types
        assert "EDITION_DEACTIVATED" in types


def test_publish_requires_feature_and_limit(
    client: TestClient, auth_header: dict
) -> None:
    create = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": _unique_code("EMP"),
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
            "code": _unique_code("LOW"),
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


def test_search_and_history(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("SRCH")
    create = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": code,
            "name": "Searchable Edition",
            "features": [
                {"feature_code": "CRM_LEAD", "is_enabled": True, "is_visible": True}
            ],
            "limits": _baseline_limits(),
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
    assert pub.status_code == 200, pub.text

    search = client.get(
        "/api/v1/platform/editions/search",
        headers=auth_header,
        params={"q": code[:6]},
    )
    assert search.status_code == 200, search.text
    assert any(i["code"] == code for i in search.json()["items"])

    hist = client.get(
        f"/api/v1/platform/editions/{edition_id}/history",
        headers=auth_header,
    )
    assert hist.status_code == 200, hist.text
    assert len(hist.json()) >= 1


def test_schema_ddd_columns() -> None:
    from sqlalchemy import inspect

    from app.db.session import engine

    insp = inspect(engine)
    cols = {c["name"] for c in insp.get_columns("edition", schema="core")}
    assert {"id", "code", "name", "status", "version_no", "created_on"} <= cols
    assert "edition_id" not in cols
    assert "edition_code" not in cols
    assert "max_users" not in cols
    checks = insp.get_check_constraints("edition", schema="core")
    assert any(c["name"] == "ck_edition_status" for c in checks)
    indexes = {i["name"] for i in insp.get_indexes("edition", schema="core")}
    assert "idx_edition_status" in indexes
