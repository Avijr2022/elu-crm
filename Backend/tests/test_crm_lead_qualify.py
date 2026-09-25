"""CRM lead qualify/disqualify API tests."""

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from sqlalchemy import select

from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient) -> str:
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


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    return _login(client)


def _create_lead(client: TestClient, token: str, name: str = "Qualify Test") -> str:
    resp = client.post(
        "/api/v1/crm/leads",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": name, "email": f"{name.replace(' ', '').lower()}@example.com"},
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["lead_id"]


def test_qualify_lead(client: TestClient, admin_token: str):
    lead_id = _create_lead(client, admin_token)
    resp = client.post(
        f"/api/v1/crm/leads/{lead_id}/qualify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "QUALIFIED"


def test_disqualify_lead_requires_reason(client: TestClient, admin_token: str):
    lead_id = _create_lead(client, admin_token)
    resp = client.post(
        f"/api/v1/crm/leads/{lead_id}/disqualify",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"reason": "Not a fit"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "DISQUALIFIED"
    assert "Not a fit" in (body.get("notes") or "")


def test_cannot_qualify_converted_lead(client: TestClient, admin_token: str):
    lead_id = _create_lead(client, admin_token, "Convert First")
    convert = client.post(
        f"/api/v1/crm/leads/{lead_id}/convert",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert convert.status_code == 201, convert.text
    resp = client.post(
        f"/api/v1/crm/leads/{lead_id}/qualify",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 422


def test_customer_opportunities_after_close_won(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": "360 Opp", "stage": "NEGOTIATION", "status": "OPEN", "opportunity_value": 50000},
    )
    assert opp.status_code == 201, opp.text
    opp_id = opp.json()["opportunity_id"]

    close = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=headers,
        json={"status": "CLOSED_WON"},
    )
    assert close.status_code == 200, close.text
    customer_id = close.json()["customer_id"]
    assert customer_id is not None

    linked = client.get(
        f"/api/v1/crm/customers/{customer_id}/opportunities",
        headers=headers,
    )
    assert linked.status_code == 200, linked.text
    items = linked.json()["items"]
    assert any(i["opportunity_id"] == opp_id for i in items)
