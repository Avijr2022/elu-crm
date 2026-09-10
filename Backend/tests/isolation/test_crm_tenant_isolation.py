"""CRM tenant isolation (ELU-TST-CRM / ADR-015)."""

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
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        if user:
            user.password_hash = hash_password("Community@12345")
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


def test_crm_lead_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    """TC-CRM-ISO-01: tenant B cannot read tenant A lead by ID."""
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    create = client.post(
        "/api/v1/crm/leads",
        headers=pro_headers,
        json={
            "full_name": f"Isolated Lead {uuid.uuid4().hex[:6]}",
            "email": f"iso-{uuid.uuid4().hex[:8]}@example.com",
        },
    )
    assert create.status_code == 201, create.text
    lead_id = create.json()["lead_id"]

    comm_headers = {"Authorization": f"Bearer {community_token}"}
    cross = client.get(f"/api/v1/crm/leads/{lead_id}", headers=comm_headers)
    assert cross.status_code == 404, cross.text

    own = client.get(f"/api/v1/crm/leads/{lead_id}", headers=pro_headers)
    assert own.status_code == 200, own.text


def test_crm_opportunity_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    """TC-CRM-ISO-02: tenant B cannot read tenant A opportunity by ID."""
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    create = client.post(
        "/api/v1/crm/opportunities",
        headers=pro_headers,
        json={"name": f"Iso Opp {uuid.uuid4().hex[:6]}", "stage": "QUALIFICATION", "status": "OPEN"},
    )
    assert create.status_code == 201, create.text
    opp_id = create.json()["opportunity_id"]

    comm_headers = {"Authorization": f"Bearer {community_token}"}
    cross = client.get(f"/api/v1/crm/opportunities/{opp_id}", headers=comm_headers)
    assert cross.status_code in (403, 404), cross.text


def test_crm_customer_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    """TC-CRM-ISO-03: tenant B cannot read tenant A customer by ID."""
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    create = client.post(
        "/api/v1/crm/customers",
        headers=pro_headers,
        json={"legal_name": f"Iso Customer {uuid.uuid4().hex[:6]}"},
    )
    assert create.status_code == 201, create.text
    customer_id = create.json()["customer_id"]

    comm_headers = {"Authorization": f"Bearer {community_token}"}
    cross = client.get(f"/api/v1/crm/customers/{customer_id}", headers=comm_headers)
    assert cross.status_code == 404, cross.text
