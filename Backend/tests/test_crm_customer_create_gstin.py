"""REQ-CRM-028: customer-create GSTIN validation and duplicate blocking."""

from uuid import UUID, uuid4

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.crm import CustomerTaxRegistration

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.seed_admin_email,
            "password": settings.seed_admin_password,
            "tenant_code": "EIIP001",
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _valid_gstin() -> str:
    # Unique, structurally valid GSTIN-shaped value for this test run.
    suffix = uuid4().hex[:1].upper()
    digits = f"{uuid4().int % 10000:04d}"
    return f"27AAPFU{digits}F1Z{suffix}"


def test_customer_create_accepts_and_persists_gstin(
    client: TestClient, admin_token: str
) -> None:
    gstin = _valid_gstin()
    response = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 GSTIN {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": gstin,
            "state_code": "27",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["legal_name"].startswith("REQ028 GSTIN ")
    with SessionLocal() as db:
        registration = db.scalars(
            select(CustomerTaxRegistration).where(
                CustomerTaxRegistration.customer_id == body["customer_id"],
                CustomerTaxRegistration.tenant_id == body["tenant_id"],
                CustomerTaxRegistration.is_deleted.is_(False),
            )
        ).first()
        assert registration is not None
        assert registration.tax_type == "GSTIN"
        assert registration.tax_number == gstin
        assert registration.state_code == "27"


def test_customer_create_rejects_malformed_gstin(
    client: TestClient, admin_token: str
) -> None:
    response = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 Invalid {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": "NOT-A-GSTIN",
        },
    )
    assert response.status_code == 422, response.text


def test_customer_create_rejects_tax_number_without_tax_type(
    client: TestClient, admin_token: str
) -> None:
    response = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 Missing type {uuid4().hex[:8]}",
            "tax_number": _valid_gstin(),
        },
    )
    assert response.status_code == 422, response.text


def test_customer_create_rejects_unsupported_tax_type(
    client: TestClient, admin_token: str
) -> None:
    response = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 Unsupported type {uuid4().hex[:8]}",
            "tax_type": "PAN",
            "tax_number": _valid_gstin(),
        },
    )
    assert response.status_code == 422, response.text


def test_customer_create_without_tax_fields_remains_supported(
    client: TestClient, admin_token: str
) -> None:
    response = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={"legal_name": f"REQ028 Legacy {uuid4().hex[:8]}"},
    )
    assert response.status_code == 201, response.text


def test_customer_create_duplicate_gstin_returns_conflict(
    client: TestClient, admin_token: str
) -> None:
    gstin = _valid_gstin()
    first = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 First {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": gstin,
        },
    )
    assert first.status_code == 201, first.text

    duplicate = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 Duplicate {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": gstin.lower(),
        },
    )
    assert duplicate.status_code == 409, duplicate.text


def test_customer_create_allows_same_gstin_in_different_tenant(
    client: TestClient, admin_token: str
) -> None:
    """The same GSTIN may be registered in two different tenants."""
    from tests.test_auth_tenant_required import (
        _create_approved_tenant,
        _provision_tenant_admin,
    )

    gstin = _valid_gstin()
    first = client.post(
        "/api/v1/crm/customers",
        headers=_auth(admin_token),
        json={
            "legal_name": f"REQ028 Tenant A {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": gstin,
        },
    )
    assert first.status_code == 201, first.text

    settings = get_settings()
    platform_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.seed_admin_email,
            "password": settings.seed_admin_password,
            "tenant_code": "EIIP001",
        },
    )
    assert platform_login.status_code == 200, platform_login.text
    platform_header = _auth(platform_login.json()["access_token"])

    tenant_code = "gst" + uuid4().hex[:8]
    tenant = _create_approved_tenant(client, platform_header, tenant_code)
    tenant_id = UUID(tenant["id"])
    tenant_email = f"admin-{tenant_code}@example.com"
    tenant_password = f"Req028-{uuid4().hex[:12]}!"

    _provision_tenant_admin(tenant_id, tenant_email, tenant_password)

    tenant_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": tenant_email,
            "password": tenant_password,
            "tenant_code": tenant_code,
        },
    )
    assert tenant_login.status_code == 200, tenant_login.text

    second = client.post(
        "/api/v1/crm/customers",
        headers=_auth(tenant_login.json()["access_token"]),
        json={
            "legal_name": f"REQ028 Tenant B {uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": gstin,
        },
    )
    assert second.status_code == 201, second.text
    assert second.json()["tenant_id"] != first.json()["tenant_id"]


def test_customer_create_rolls_back_customer_if_registration_insert_fails(
    client: TestClient, admin_token: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A registration insert failure must not leave an orphan customer."""
    from app.services.crm.customer_service import CustomerService

    gstin = _valid_gstin()
    legal_name = f"REQ028 Rollback {uuid4().hex[:8]}"

    original_init = CustomerService.__init__

    def patched_init(self, db):
        original_init(self, db)
        original_db_add = db.add

        def fail_registration_add(instance, *args, **kwargs):
            if isinstance(instance, CustomerTaxRegistration):
                from sqlalchemy.exc import IntegrityError
                raise IntegrityError(
                    "injected registration failure", {}, RuntimeError("test")
                )
            return original_db_add(instance, *args, **kwargs)

        monkeypatch.setattr(db, "add", fail_registration_add)

    monkeypatch.setattr(CustomerService, "__init__", patched_init)

    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError, match="injected registration failure"):
        client.post(
            "/api/v1/crm/customers",
            headers=_auth(admin_token),
            json={
                "legal_name": legal_name,
                "tax_type": "GSTIN",
                "tax_number": gstin,
            },
        )

    with platform_session() as db:
        from app.models.crm import Customer
        from sqlalchemy import select

        customer = db.scalars(
            select(Customer).where(
                Customer.legal_name == legal_name,
                Customer.is_deleted.is_(False),
            )
        ).first()
        assert customer is None
