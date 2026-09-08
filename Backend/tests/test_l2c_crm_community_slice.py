"""Community edition CRM portion of Lead-to-Cash (TC-L2C-CRM-01 variant).

Traces: Lead → Qualify → Convert to Customer → Activity → Activate Customer.
No opportunity pipeline (COMU001 / Community edition).
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.conftest import platform_session

COMMUNITY_EMAIL = "community@euphoriainfotech.com"
COMMUNITY_PASSWORD = "Community@12345"
COMMUNITY_TENANT = "COMU001"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def community_token(client: TestClient) -> str:
    with platform_session() as db:
        user = db.scalars(select(User).where(User.email == COMMUNITY_EMAIL)).first()
        assert user is not None
        user.password_hash = hash_password(COMMUNITY_PASSWORD)
        db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": COMMUNITY_EMAIL,
            "password": COMMUNITY_PASSWORD,
            "tenant_code": COMMUNITY_TENANT,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_l2c_crm_community_happy_path(client: TestClient, community_token: str):
    headers = {"Authorization": f"Bearer {community_token}"}
    suffix = uuid.uuid4().hex[:6]

    opps = client.get("/api/v1/crm/opportunities", headers=headers)
    assert opps.status_code == 403, opps.text

    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={
            "full_name": f"Community L2C {suffix}",
            "company_name": f"Community Corp {suffix}",
            "email": f"comm-l2c-{suffix}@example.com",
            "estimated_value": 120000,
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
    assert body["convert_type"] == "CUSTOMER"
    customer_id = body["customer"]["customer_id"]
    assert body["customer"]["status"] == "PROSPECT"

    activity = client.post(
        "/api/v1/crm/activities",
        headers=headers,
        json={
            "activity_type_code": "CALL",
            "outcome_code": "INTERESTED",
            "subject": "Community discovery call",
            "entity_type": "CUSTOMER",
            "entity_id": customer_id,
        },
    )
    assert activity.status_code == 201, activity.text
    assert activity.json()["outcome_code"] == "INTERESTED"

    address = client.post(
        f"/api/v1/crm/customers/{customer_id}/addresses",
        headers=headers,
        json={"address_type": "REGISTERED", "address_line1": "45 Community Lane"},
    )
    assert address.status_code == 201, address.text

    activate = client.patch(
        f"/api/v1/crm/customers/{customer_id}",
        headers=headers,
        json={"status": "ACTIVE"},
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"

    timeline = client.get(
        f"/api/v1/crm/activities/timeline?entity_type=CUSTOMER&entity_id={customer_id}",
        headers=headers,
    )
    assert timeline.status_code == 200, timeline.text
    assert timeline.json()["total"] >= 1
