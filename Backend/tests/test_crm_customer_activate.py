"""BR-CRM-043/044 customer activation validation tests."""

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


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_activate_without_contact_or_address_fails(client: TestClient, admin_token: str):
    create = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"Activate Test {uuid.uuid4().hex[:6]}"},
    )
    assert create.status_code == 201, create.text
    cid = create.json()["customer_id"]

    patch = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "ACTIVE"},
    )
    assert patch.status_code == 422, patch.text
    assert "BR-CRM-043" in patch.text or "primary" in patch.text.lower()


def test_activate_with_contact_only_fails(client: TestClient, admin_token: str):
    create = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"Partial {uuid.uuid4().hex[:6]}"},
    )
    cid = create.json()["customer_id"]
    client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=_auth(admin_token),
        json={"first_name": "Ravi", "is_primary": True},
    )
    patch = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "ACTIVE"},
    )
    assert patch.status_code == 422, patch.text
    assert "BR-CRM-044" in patch.text or "address" in patch.text.lower()


def test_activate_with_contact_and_address_succeeds(client: TestClient, admin_token: str):
    create = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"Full {uuid.uuid4().hex[:6]}"},
    )
    cid = create.json()["customer_id"]
    client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=_auth(admin_token),
        json={"first_name": "Priya", "is_primary": True},
    )
    client.post(
        f"/api/v1/crm/customers/{cid}/addresses",
        headers=_auth(admin_token),
        json={"address_type": "REGISTERED", "address_line1": "12 MG Road"},
    )
    patch = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "ACTIVE"},
    )
    assert patch.status_code == 200, patch.text
    assert patch.json()["status"] == "ACTIVE"


def test_list_customers_by_status(client: TestClient, admin_token: str):
    suffix = uuid.uuid4().hex[:6]
    prospect = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"Prospect {suffix}"},
    )
    assert prospect.status_code == 201, prospect.text

    active = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"Active {suffix}"},
    )
    assert active.status_code == 201, active.text
    cid = active.json()["customer_id"]
    client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=_auth(admin_token),
        json={"first_name": "A", "is_primary": True},
    )
    client.post(
        f"/api/v1/crm/customers/{cid}/addresses",
        headers=_auth(admin_token),
        json={"address_type": "REGISTERED", "address_line1": "1 Main St"},
    )
    client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "ACTIVE"},
    )

    listed = client.get(
        "/api/v1/crm/customers?status=ACTIVE&page_size=1",
        headers=_auth(admin_token),
    )
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] >= 1
    assert all(i["status"] == "ACTIVE" for i in listed.json()["items"])
