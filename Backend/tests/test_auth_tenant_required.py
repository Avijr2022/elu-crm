"""Focused authentication contract tests - tenant_code is required and always scoped.

Enforces the login contract:
- ``tenant_code`` is mandatory (omitted -> 422, empty -> 422)
- an unknown ``tenant_code`` is rejected (401)
- the user lookup is scoped to the named tenant, so an email that exists in two
  tenants cannot be authenticated against the wrong one, and no unscoped
  (tenant-less) login path remains.

The scoping case relies on ``uk_users_tenant_email`` (UNIQUE(tenant_id, email)),
which permits the same email in two tenants by design.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import Organization, Role, User
from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def seed_admin(client: TestClient) -> dict:
    """Pin the seeded EIIP001 admin to the known seed password."""
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None, "seed admin user missing"
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    return {
        "email": settings.seed_admin_email,
        "password": settings.seed_admin_password,
        "tenant_code": "EIIP001",
    }


@pytest.fixture(scope="module")
def platform_header(client: TestClient, seed_admin: dict) -> dict:
    resp = client.post("/api/v1/auth/login", json=seed_admin)
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _create_approved_tenant(client: TestClient, header: dict, code: str) -> dict:
    create = client.post(
        "/api/v1/platform/tenants",
        headers=header,
        json={
            "code": code,
            "legal_name": f"Legal {code}",
            "trade_name": f"Trade {code}",
            "edition_code": "PROFESSIONAL",
            "email": f"{code}@example.com",
            "mobile": "9876543210",
            "primary_contact": {
                "contact_type": "PRIMARY",
                "name": "Primary Contact",
                "email": f"contact-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Tenant Scope Street",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    approve = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=header,
        json={"version_no": tenant["version_no"]},
    )
    assert approve.status_code == 200, approve.text
    return approve.json()


def _provision_tenant_admin(tenant_id: uuid.UUID, email: str, password: str) -> uuid.UUID:
    """Create an ACTIVE TENANT_ADMIN for the tenant (platform session)."""
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        assert org is not None, "tenant organization missing"
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == "TENANT_ADMIN"
            )
        ).first()
        if role is None:
            role = Role(
                tenant_id=tenant_id,
                role_code="TENANT_ADMIN",
                role_name="Tenant Admin",
                is_system=True,
            )
            db.add(role)
            db.flush()
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            employee_code=f"TSC{uuid.uuid4().hex[:6].upper()}",
            first_name="Tenant",
            last_name="Scope",
            display_name="Tenant Scope",
            email=email.lower(),
            password_hash=hash_password(password),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        return user.user_id


def test_login_without_tenant_code_is_rejected(client: TestClient, seed_admin: dict) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": seed_admin["email"], "password": seed_admin["password"]},
    )
    assert resp.status_code == 422, resp.text


def test_login_with_empty_tenant_code_is_rejected(client: TestClient, seed_admin: dict) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": seed_admin["email"],
            "password": seed_admin["password"],
            "tenant_code": "",
        },
    )
    assert resp.status_code == 422, resp.text


def test_login_with_unknown_tenant_code_is_rejected(client: TestClient, seed_admin: dict) -> None:
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": seed_admin["email"],
            "password": seed_admin["password"],
            "tenant_code": "NOPE001",
        },
    )
    assert resp.status_code == 401, resp.text


def test_login_is_scoped_to_the_named_tenant(
    client: TestClient, seed_admin: dict, platform_header: dict
) -> None:
    code = "tsc" + uuid.uuid4().hex[:8]
    tenant = _create_approved_tenant(client, platform_header, code)
    other_password = "OtherTenant@123"
    _provision_tenant_admin(uuid.UUID(tenant["id"]), seed_admin["email"], other_password)

    # correct tenant + its own password -> 200
    ok = client.post("/api/v1/auth/login", json=seed_admin)
    assert ok.status_code == 200, ok.text

    # same email, OTHER tenant, tenant A's password -> 401 (scoping enforced)
    wrong = client.post(
        "/api/v1/auth/login",
        json={
            "email": seed_admin["email"],
            "password": seed_admin["password"],
            "tenant_code": code,
        },
    )
    assert wrong.status_code == 401, wrong.text

    # other tenant + its own password -> 200 and resolves to that tenant only
    other = client.post(
        "/api/v1/auth/login",
        json={
            "email": seed_admin["email"],
            "password": other_password,
            "tenant_code": code,
        },
    )
    assert other.status_code == 200, other.text
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {other.json()['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["tenant_code"].lower() == code.lower()

    # no unscoped path remains: omitting the tenant cannot authenticate either user
    unscoped = client.post(
        "/api/v1/auth/login",
        json={"email": seed_admin["email"], "password": other_password},
    )
    assert unscoped.status_code == 422, unscoped.text
