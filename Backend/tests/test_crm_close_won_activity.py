"""CRM close-won and activity API tests."""

import uuid
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import Role, User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient, email: str, password: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": "EIIP001"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


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
    return _login(client, settings.seed_admin_email, settings.seed_admin_password)


def _create_sales_user(role_code: str) -> tuple[str, str]:
    email = f"{role_code.lower()}-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    password = "SalesUser!234"
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        assert role is not None
        user = User(
            tenant_id=admin.tenant_id,
            organization_id=admin.organization_id,
            role_id=role.role_id,
            employee_code=f"SE{uuid.uuid4().hex[:6].upper()}",
            first_name="Sales",
            last_name=role_code,
            display_name=f"Test {role_code}",
            email=email,
            password_hash=hash_password(password),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
    return email, password


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_close_won_creates_customer_and_activity(client: TestClient, admin_token: str):
    create = client.post(
        "/api/v1/crm/opportunities",
        headers=_auth(admin_token),
        json={
            "name": f"Close Won Test {uuid.uuid4().hex[:6]}",
            "company_name": "Acme Test Co",
            "opportunity_value": "50000",
            "currency_code": "INR",
        },
    )
    assert create.status_code == 201, create.text
    opp_id = create.json()["opportunity_id"]

    close = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=_auth(admin_token),
        json={"status": "CLOSED_WON"},
    )
    assert close.status_code == 200, close.text
    body = close.json()
    assert body["status"] == "CLOSED_WON"
    assert body["customer_id"] is not None

    customer = client.get(
        f"/api/v1/crm/customers/{body['customer_id']}",
        headers=_auth(admin_token),
    )
    assert customer.status_code == 200, customer.text
    assert customer.json()["legal_name"] == "Acme Test Co"

    timeline = client.get(
        "/api/v1/crm/activities/timeline",
        headers=_auth(admin_token),
        params={"entity_type": "OPPORTUNITY", "entity_id": opp_id},
    )
    assert timeline.status_code == 200, timeline.text
    subjects = [a["subject"] for a in timeline.json()["items"]]
    assert "Closed Won" in subjects


def test_sales_exec_cannot_close_won(client: TestClient, admin_token: str):
    email, password = _create_sales_user("SALES_EXECUTIVE")
    exec_token = _login(client, email, password)

    create = client.post(
        "/api/v1/crm/opportunities",
        headers=_auth(exec_token),
        json={
            "name": f"Exec Block {uuid.uuid4().hex[:6]}",
            "opportunity_value": str(Decimal("10000")),
        },
    )
    assert create.status_code == 201, create.text
    opp_id = create.json()["opportunity_id"]

    close = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=_auth(exec_token),
        json={"status": "CLOSED_WON"},
    )
    assert close.status_code == 403, close.text


def test_create_activity(client: TestClient, admin_token: str):
    create = client.post(
        "/api/v1/crm/leads",
        headers=_auth(admin_token),
        json={
            "full_name": "Activity Lead",
            "email": f"lead-{uuid.uuid4().hex[:6]}@example.com",
            "estimated_value": "0",
        },
    )
    assert create.status_code == 201, create.text
    lead_id = create.json()["lead_id"]

    act = client.post(
        "/api/v1/crm/activities",
        headers=_auth(admin_token),
        json={
            "activity_type_code": "NOTE",
            "subject": "Follow-up call",
            "description": "Discussed requirements",
            "entity_type": "LEAD",
            "entity_id": lead_id,
        },
    )
    assert act.status_code == 201, act.text
    assert act.json()["subject"] == "Follow-up call"

    timeline = client.get(
        "/api/v1/crm/activities/timeline",
        headers=_auth(admin_token),
        params={"entity_type": "LEAD", "entity_id": lead_id},
    )
    assert timeline.status_code == 200
    assert any(i["subject"] == "Follow-up call" for i in timeline.json()["items"])


def test_me_includes_permissions(client: TestClient, admin_token: str):
    me = client.get("/api/v1/auth/me", headers=_auth(admin_token))
    assert me.status_code == 200, me.text
    perms = me.json().get("permissions") or []
    assert "opportunity.approve" in perms
    assert "lead.create" in perms
