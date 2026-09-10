"""Community edition feature matrix and demo tenant smoke tests."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.seed import EDITION_SPECS
from app.main import app
from app.models.pf import Edition, EditionFeature, Tenant, User
from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_community_edition_feature_matrix():
    spec = EDITION_SPECS["COMMUNITY"]
    assert "CRM_LEAD" in spec["features"]
    assert "CRM_CUSTOMER" in spec["features"]
    assert "CRM_ACTIVITY" in spec["features"]
    assert "CRM_OPPORTUNITY" not in spec["features"]


def test_community_edition_in_database():
    with platform_session() as db:
        edition = db.scalars(select(Edition).where(Edition.code == "COMMUNITY")).first()
        assert edition is not None
        codes = {f.feature_code for f in edition.features if f.is_enabled}
        assert "CRM_CUSTOMER" in codes
        assert "CRM_ACTIVITY" in codes
        assert "CRM_OPPORTUNITY" not in codes


def test_community_demo_tenant_exists():
    with platform_session() as db:
        tenant = db.scalars(select(Tenant).where(Tenant.tenant_code == "COMU001")).first()
        assert tenant is not None
        assert tenant.edition.code == "COMMUNITY"


def test_community_login_and_edition_features(client: TestClient):
    with platform_session() as db:
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        assert user is not None
        user.password_hash = hash_password("Community@12345")
        db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "community@euphoriainfotech.com",
            "password": "Community@12345",
            "tenant_code": "COMU001",
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    edition = client.get("/api/v1/tenant/edition", headers=headers)
    assert edition.status_code == 200, edition.text
    codes = {
        f["feature_code"]
        for f in edition.json().get("features", [])
        if f.get("is_enabled")
    }
    assert "CRM_CUSTOMER" in codes
    assert "CRM_ACTIVITY" in codes
    assert "CRM_OPPORTUNITY" not in codes

    customers = client.get("/api/v1/crm/customers", headers=headers)
    assert customers.status_code == 200, customers.text

    opps = client.get("/api/v1/crm/opportunities", headers=headers)
    assert opps.status_code == 403, opps.text
    assert "CRM_OPPORTUNITY" in opps.text or "REQ-EDM" in opps.text


def test_community_lead_converts_to_customer(client: TestClient):
    with platform_session() as db:
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        assert user is not None
        user.password_hash = hash_password("Community@12345")
        db.commit()

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": "community@euphoriainfotech.com",
            "password": "Community@12345",
            "tenant_code": "COMU001",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = client.post(
        "/api/v1/crm/leads",
        headers=headers,
        json={"full_name": "Community Lead", "email": "cl@example.com"},
    )
    assert create.status_code == 201, create.text
    lead_id = create.json()["lead_id"]

    convert = client.post(f"/api/v1/crm/leads/{lead_id}/convert", headers=headers)
    assert convert.status_code == 201, convert.text
    body = convert.json()
    assert body["convert_type"] == "CUSTOMER"
    assert body["customer"]["legal_name"] == "Community Lead"
