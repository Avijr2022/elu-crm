"""PRJ handoff stub tests."""

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


def test_prj_handoff_from_close_won_opportunity(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"PRJ HO {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
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
    body = handoff.json()
    assert body["status"] == "QUEUED"
    assert body["wo_number"].startswith("WO-")
    assert body["opportunity_id"] == opp_id

    again = client.post(
        f"/api/v1/prj/handoffs/from-opportunity/{opp_id}",
        headers=headers,
    )
    assert again.status_code == 201, again.text
    assert again.json()["work_order_id"] == body["work_order_id"]
