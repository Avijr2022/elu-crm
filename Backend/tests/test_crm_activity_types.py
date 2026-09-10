"""CRM DB-backed lookups and activity type admin tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
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


def test_crm_lookups_db_backed(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    resp = client.get("/api/v1/crm/lookups", headers=headers)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "QUALIFICATION" in body["pipeline_stages"]
    assert "NOTE" in body["activity_types"]
    assert len(body["activity_type_details"]) >= 6
    assert len(body["pipeline_stage_details"]) >= 6


def test_create_custom_activity_type(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    code = f"VISIT{uuid.uuid4().hex[:4].upper()}"
    create = client.post(
        "/api/v1/crm/activity-types",
        headers=headers,
        json={"code": code, "name": "Demo Visit"},
    )
    assert create.status_code == 201, create.text
    assert create.json()["code"] == code

    lookups = client.get("/api/v1/crm/lookups", headers=headers)
    assert lookups.status_code == 200, lookups.text
    assert code in lookups.json()["activity_types"]


def test_deactivate_activity_type(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    code = f"VISIT{uuid.uuid4().hex[:4].upper()}"
    create = client.post(
        "/api/v1/crm/activity-types",
        headers=headers,
        json={"code": code, "name": "Temp Visit"},
    )
    assert create.status_code == 201, create.text
    type_id = create.json()["activity_type_id"]

    deactivate = client.patch(
        f"/api/v1/crm/activity-types/{type_id}",
        headers=headers,
        json={"is_active": False},
    )
    assert deactivate.status_code == 200, deactivate.text
    assert deactivate.json()["is_active"] is False

    active_only = client.get("/api/v1/crm/activity-types", headers=headers)
    assert active_only.status_code == 200, active_only.text
    assert code not in {t["code"] for t in active_only.json()["items"]}

    with_inactive = client.get(
        "/api/v1/crm/activity-types?include_inactive=true",
        headers=headers,
    )
    assert with_inactive.status_code == 200, with_inactive.text
    assert code in {t["code"] for t in with_inactive.json()["items"]}

    lookups = client.get("/api/v1/crm/lookups", headers=headers)
    assert lookups.status_code == 200, lookups.text
    assert code not in lookups.json()["activity_types"]
