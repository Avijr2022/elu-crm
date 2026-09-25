"""CRM lookups API tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
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


def test_crm_lookups(client: TestClient, admin_token: str):
    resp = client.get(
        "/api/v1/crm/lookups",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "QUALIFICATION" in body["pipeline_stages"]
    assert "CLOSED_WON" in body["opportunity_statuses"]
    assert "NOTE" in body["activity_types"]


def test_create_activity_with_lookup_type(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={"full_name": "Activity Type Lead", "email": "atl@example.com"},
    )
    assert lead.status_code == 201, lead.text
    lead_id = lead.json()["lead_id"]
    act = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "outcome_code": "INTERESTED",
            "subject": "Follow-up call",
            "entity_type": "LEAD",
            "entity_id": lead_id,
        },
    )
    assert act.status_code == 201, act.text
    assert act.json()["activity_type_code"] == "CALL"


def test_create_planned_activity_with_due_on(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={"full_name": "Due Date Lead", "email": "ddl@example.com"},
    )
    assert lead.status_code == 201, lead.text
    lead_id = lead.json()["lead_id"]
    act = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "TASK",
            "subject": "Follow up",
            "status": "PLANNED",
            "due_on": "2026-12-01T09:00:00Z",
            "entity_type": "LEAD",
            "entity_id": lead_id,
        },
    )
    assert act.status_code == 201, act.text
    body = act.json()
    assert body["status"] == "PLANNED"
    assert body["due_on"] is not None
