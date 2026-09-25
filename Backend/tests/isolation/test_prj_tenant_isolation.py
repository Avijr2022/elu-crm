"""PRJ work-order tenant isolation (ADR-015)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf003a import rls_enabled
from app.main import app
from app.models.pf import User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient, email: str, password: str, tenant_code: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": tenant_code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def pro_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    return _login(
        client,
        settings.seed_admin_email,
        settings.seed_admin_password,
        "EIIP001",
    )


@pytest.fixture(scope="module")
def community_token(client: TestClient) -> str:
    return _login(
        client,
        "community@euphoriainfotech.com",
        "Community@12345",
        "COMU001",
    )


def _create_work_order(client: TestClient, headers: dict) -> str:
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"PRJ ISO {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
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
    return handoff.json()["work_order_id"]


def test_prj_work_order_rls_enabled():
    with platform_session() as db:
        assert rls_enabled(db, "projects", "work_order")


def test_prj_work_order_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    community_headers = {"Authorization": f"Bearer {community_token}"}
    wo_id = _create_work_order(client, pro_headers)

    blocked = client.get(
        f"/api/v1/prj/work-orders/{wo_id}",
        headers=community_headers,
    )
    assert blocked.status_code in (403, 404), blocked.text
