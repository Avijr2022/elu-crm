"""PF-008 tenant isolation: the user directory and user records never cross tenant boundaries.

`BR-PF-059` (user must belong to the JWT tenant) and `AC-PF-008-07` (a tenant's user query
returns only its own users) are enforced by the JWT-bound tenant context plus the
`tenant_isolation` RLS policies (ADR-015 / PF-003A). This module proves that a Tenant Admin of
tenant A cannot read, update or deactivate a user that lives in tenant B, even when the UUID
is known, and that the directory never leaks a foreign row.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.security import hash_password
from app.main import app
from app.models.pf import Organization, Role, User
from tests.conftest import platform_session

API = "/api/v1"
PASSWORD = "Pf008Iso@123"


def _unique_code(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _platform_header(client: TestClient) -> dict:
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == "admin@euphoriainfotech.com")
        ).first()
        assert admin is not None
        admin.password_hash = hash_password("Admin@12345")
        db.commit()
    resp = client.post(
        f"{API}/auth/login",
        json={
            "email": "admin@euphoriainfotech.com",
            "password": "Admin@12345",
            "tenant_code": "EIIP001",
        },
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def _provision_tenant(client: TestClient, header: dict, prefix: str) -> dict:
    code = _unique_code(prefix)
    create = client.post(
        f"{API}/platform/tenants",
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
                "name": "Primary",
                "email": f"c-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Isolation Way",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert create.status_code == 201, create.text
    tenant = create.json()
    approve = client.post(
        f"{API}/platform/tenants/{tenant['id']}/approve",
        headers=header,
        json={"version_no": tenant["version_no"]},
    )
    assert approve.status_code == 200, approve.text
    tenant_id = uuid.UUID(tenant["id"])

    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == "TENANT_ADMIN"
            )
        ).first()
        assert org is not None and role is not None
        email = f"admin-{code}@example.com"
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            first_name="Iso",
            last_name="Admin",
            display_name="Iso Admin",
            email=email,
            password_hash=hash_password(PASSWORD),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        admin_id = str(user.user_id)

    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD, "tenant_code": code},
    )
    assert login.status_code == 200, login.text
    return {
        "code": code,
        "id": tenant["id"],
        "admin_email": email,
        "admin_id": admin_id,
        "header": {"Authorization": f"Bearer {login.json()['access_token']}"},
    }


@pytest.fixture(scope="module")
def tenant_a(client: TestClient) -> dict:
    return _provision_tenant(client, _platform_header(client), "isoa")


@pytest.fixture(scope="module")
def tenant_b(client: TestClient) -> dict:
    return _provision_tenant(client, _platform_header(client), "isob")


def test_foreign_user_detail_is_not_readable(
    client: TestClient, tenant_a: dict, tenant_b: dict
) -> None:
    assert tenant_a["id"] != tenant_b["id"]
    resp = client.get(f"{API}/users/{tenant_b['admin_id']}", headers=tenant_a["header"])
    assert resp.status_code == 404, resp.text


def test_foreign_user_is_not_mutable(
    client: TestClient, tenant_a: dict, tenant_b: dict
) -> None:
    put = client.put(
        f"{API}/users/{tenant_b['admin_id']}",
        headers=tenant_a["header"],
        json={"first_name": "Hijacked", "version_no": 1},
    )
    assert put.status_code == 404, put.text
    delete = client.delete(f"{API}/users/{tenant_b['admin_id']}", headers=tenant_a["header"])
    assert delete.status_code == 404, delete.text

    with platform_session() as db:
        victim = db.get(User, uuid.UUID(tenant_b["admin_id"]))
        assert victim.first_name == "Iso"
        assert victim.account_status == "ACTIVE"
        assert victim.is_active is True


def test_directory_never_returns_foreign_rows(
    client: TestClient, tenant_a: dict, tenant_b: dict
) -> None:
    listing = client.get(
        f"{API}/users", headers=tenant_a["header"], params={"page_size": 100}
    )
    assert listing.status_code == 200, listing.text
    body = listing.json()
    tenant_ids = {item["tenant_id"] for item in body["items"]}
    assert tenant_ids <= {tenant_a["id"]}, tenant_ids
    emails = {item["email"] for item in body["items"]}
    assert tenant_b["admin_email"] not in emails
    assert body["total"] == len(body["items"])


def test_foreign_invitation_token_cannot_be_used_cross_tenant(
    client: TestClient, tenant_a: dict, tenant_b: dict
) -> None:
    """An invitation is bound to its tenant: activating it yields that tenant's tokens only."""
    email = f"cross-{uuid.uuid4().hex[:8]}@example.com"
    invited = client.post(
        f"{API}/users",
        headers=tenant_b["header"],
        json={"email": email, "first_name": "Cross", "role_code": "SALES_EXECUTIVE"},
    )
    assert invited.status_code == 201, invited.text
    token = invited.json()["invite_token"]

    activated = client.post(
        f"{API}/auth/register", json={"token": token, "password": "Pf008Cross@1"}
    )
    assert activated.status_code == 200, activated.text
    me = client.get(
        f"{API}/auth/me",
        headers={"Authorization": f"Bearer {activated.json()['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["tenant_id"] == tenant_b["id"]

    # Tenant A can neither see nor read the newly activated user of tenant B.
    assert (
        client.get(f"{API}/users/{invited.json()['user_id']}", headers=tenant_a["header"]).status_code
        == 404
    )
