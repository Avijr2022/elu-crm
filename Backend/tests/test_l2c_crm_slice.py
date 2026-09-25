"""CRM portion of Lead-to-Cash happy path (TC-L2C-CRM-01).

Traces: Lead → Qualify → Convert → Activity → Close Won → Activate Customer.
SAL/PRJ/FIN modules are not yet implemented; this test bounds the CRM slice.
"""

import uuid

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
def manager_token(client: TestClient) -> str:
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


def test_l2c_crm_happy_path(client: TestClient, manager_token: str):
    headers = {"Authorization": f"Bearer {manager_token}"}
    suffix = uuid.uuid4().hex[:6]

    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={
            "full_name": f"L2C Prospect {suffix}",
            "company_name": f"L2C Corp {suffix}",
            "email": f"l2c-{suffix}@example.com",
            "estimated_value": 250000,
        },
    )
    assert lead.status_code == 201, lead.text
    lead_id = lead.json()["lead_id"]

    qualify = client.post(f"/api/v1/crm/leads/{lead_id}/qualify", headers=headers)
    assert qualify.status_code == 200, qualify.text
    assert qualify.json()["status"] == "QUALIFIED"

    convert = client.post(f"/api/v1/crm/leads/{lead_id}/convert", headers=headers)
    assert convert.status_code == 201, convert.text
    body = convert.json()
    assert body["convert_type"] == "OPPORTUNITY"
    opp_id = body["opportunity"]["opportunity_id"]

    activity = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "outcome_code": "INTERESTED",
            "subject": "Discovery call",
            "entity_type": "OPPORTUNITY",
            "entity_id": opp_id,
        },
    )
    assert activity.status_code == 201, activity.text
    assert activity.json()["outcome_code"] == "INTERESTED"

    close = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=headers,
        json={"status": "CLOSED_WON"},
    )
    assert close.status_code == 200, close.text
    customer_id = close.json()["customer_id"]
    assert customer_id is not None

    client.post(
        f"/api/v1/crm/customers/{customer_id}/contacts",
        headers=headers,
        json={"first_name": "Priya", "is_primary": True},
    )
    client.post(
        f"/api/v1/crm/customers/{customer_id}/addresses",
        headers=headers,
        json={"address_type": "REGISTERED", "address_line1": "12 MG Road"},
    )
    activate = client.patch(
        f"/api/v1/crm/customers/{customer_id}",
        headers=headers,
        json={"status": "ACTIVE"},
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"

    timeline = client.get(
        f"/api/v1/crm/activities/timeline?entity_type=OPPORTUNITY&entity_id={opp_id}",
        headers=headers,
    )
    assert timeline.status_code == 200, timeline.text
    assert timeline.json()["total"] >= 1
