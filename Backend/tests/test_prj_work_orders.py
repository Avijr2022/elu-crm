"""PRJ work-order list/detail API tests."""

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


def _handoff_work_order(client: TestClient, headers: dict) -> dict:
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"PRJ WO {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
    )
    assert opp.status_code == 201, opp.text
    opp_id = opp.json()["opportunity_id"]
    won = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=headers,
        json={"status": "CLOSED_WON"},
    )
    assert won.status_code == 200, won.text
    handoff = client.post(
        f"/api/v1/prj/handoffs/from-opportunity/{opp_id}",
        headers=headers,
    )
    assert handoff.status_code == 201, handoff.text
    return handoff.json()


def test_list_and_get_work_orders(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    created = _handoff_work_order(client, headers)
    wo_id = created["work_order_id"]

    listed = client.get("/api/v1/prj/work-orders", headers=headers)
    assert listed.status_code == 200, listed.text
    body = listed.json()
    assert body["total"] >= 1
    assert any(i["work_order_id"] == wo_id for i in body["items"])

    detail = client.get(f"/api/v1/prj/work-orders/{wo_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    row = detail.json()
    assert row["wo_number"] == created["wo_number"]
    assert row["status"] == "QUEUED"
    assert row["opportunity_id"] == created["opportunity_id"]

    filtered = client.get(
        "/api/v1/prj/work-orders",
        headers=headers,
        params={"status": "QUEUED"},
    )
    assert filtered.status_code == 200, filtered.text
    assert all(i["status"] == "QUEUED" for i in filtered.json()["items"])

    missing = client.get(
        f"/api/v1/prj/work-orders/{uuid.uuid4()}",
        headers=headers,
    )
    assert missing.status_code == 404, missing.text
