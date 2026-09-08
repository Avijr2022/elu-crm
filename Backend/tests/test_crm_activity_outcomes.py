"""CRM activity outcome lookup tests."""

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


def test_activity_outcomes_seeded_and_filtered(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    lookups = client.get("/api/v1/crm/lookups", headers=headers)
    assert lookups.status_code == 200, lookups.text
    body = lookups.json()
    assert "INTERESTED" in body["activity_outcomes"]
    assert len(body["activity_outcome_details"]) >= 9

    call_outcomes = client.get(
        "/api/v1/crm/activity-outcomes?activity_type_code=CALL",
        headers=headers,
    )
    assert call_outcomes.status_code == 200, call_outcomes.text
    codes = {i["code"] for i in call_outcomes.json()["items"]}
    assert codes == {"INTERESTED", "NOT_INTERESTED", "CALLBACK", "NO_ANSWER"}


def test_call_requires_outcome_when_completed(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={"full_name": "Outcome Lead", "email": "outcome@example.com"},
    )
    assert lead.status_code == 201, lead.text
    lead_id = lead.json()["lead_id"]

    missing = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "subject": "No outcome",
            "entity_type": "LEAD",
            "entity_id": lead_id,
        },
    )
    assert missing.status_code == 422, missing.text

    ok = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "outcome_code": "INTERESTED",
            "subject": "Discovery call",
            "entity_type": "LEAD",
            "entity_id": lead_id,
        },
    )
    assert ok.status_code == 201, ok.text
    assert ok.json()["outcome_code"] == "INTERESTED"


def test_create_and_deactivate_activity_outcome(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Use a unique code per run so this test is idempotent even though the test
    # DB is shared/persistent (a previous leftover would otherwise 422 on create).
    code = f"WARM_LEAD_{uuid.uuid4().hex[:6]}".upper()
    create = client.post(
        "/api/v1/crm/activity-outcomes",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "code": code,
            "name": "Warm Lead",
            "is_positive": True,
        },
    )
    assert create.status_code == 201, create.text
    outcome_id = create.json()["activity_outcome_id"]
    try:
        listed = client.get(
            "/api/v1/crm/activity-outcomes?activity_type_code=CALL",
            headers=headers,
        )
        assert code in {i["code"] for i in listed.json()["items"]}

        patch = client.patch(
            f"/api/v1/crm/activity-outcomes/{outcome_id}",
            headers=headers,
            json={"is_active": False},
        )
        assert patch.status_code == 200, patch.text
        assert patch.json()["is_active"] is False

        active = client.get(
            "/api/v1/crm/activity-outcomes?activity_type_code=CALL",
            headers=headers,
        )
        assert code not in {i["code"] for i in active.json()["items"]}
    finally:
        # Cleanup: always leave the created outcome inactive so it never pollutes
        # the exact-set "seeded CALL outcomes" assertion in later runs.
        client.patch(
            f"/api/v1/crm/activity-outcomes/{outcome_id}",
            headers=headers,
            json={"is_active": False},
        )
