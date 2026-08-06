"""PF-002 Tenant Management tests — repeatable (unique codes per run)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf002 import apply_pf002_ddl
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import AuditEvent, Role, Tenant, User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    db = SessionLocal()
    try:
        apply_pf002_ddl(db)
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None, "Seed admin missing — start API once to seed"
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == "PLATFORM_ADMIN",
            )
        ).first()
        if role is None:
            role = Role(
                tenant_id=admin.tenant_id,
                role_code="PLATFORM_ADMIN",
                role_name="Platform Admin",
                is_system=True,
            )
            db.add(role)
            db.flush()
        admin.role_id = role.role_id
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    finally:
        db.close()

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


@pytest.fixture(scope="module")
def auth_header(platform_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {platform_token}"}


def _unique_code(prefix: str = "t") -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def _register_payload(code: str, legal: str | None = None) -> dict:
    return {
        "code": code,
        "legal_name": legal or f"Legal {code}",
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
            "line1": "1 Test Street",
            "city": "Kolkata",
            "country": "India",
        },
    }


def test_migration_idempotent(client: TestClient) -> None:
    db = SessionLocal()
    try:
        apply_pf002_ddl(db)
        apply_pf002_ddl(db)
        row = db.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='core' AND table_name='tenant_contact'"
            )
        ).first()
        assert row is not None
    finally:
        db.close()


def test_list_tenants(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/platform/tenants", headers=auth_header)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["total"] >= 1
    codes = {i["code"] for i in body["items"]}
    assert "EIIP001" in codes


def test_tenant_profile_own(client: TestClient, auth_header: dict) -> None:
    resp = client.get("/api/v1/tenant/profile", headers=auth_header)
    assert resp.status_code == 200, resp.text
    assert resp.json()["code"] == "EIIP001"


def test_register_approve_suspend_reactivate(
    client: TestClient, auth_header: dict
) -> None:
    code = _unique_code("reg")
    create = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code),
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["code"] == code
    assert body["status"] == "PENDING_ACTIVATION"
    assert body["organization_code"] == "HO001"
    assert body["subscription_status"] == "TRIAL"
    assert len(body["contacts"]) == 1
    assert len(body["addresses"]) == 1
    tid = body["id"]
    ver = body["version_no"]

    approve = client.post(
        f"/api/v1/platform/tenants/{tid}/approve",
        headers=auth_header,
        json={"version_no": ver},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["status"] == "ACTIVE"
    ver = approve.json()["version_no"]

    suspend = client.post(
        f"/api/v1/platform/tenants/{tid}/suspend",
        headers=auth_header,
        json={"version_no": ver, "reason": "Payment overdue QA"},
    )
    assert suspend.status_code == 200, suspend.text
    assert suspend.json()["status"] == "SUSPENDED"
    ver = suspend.json()["version_no"]

    reactivate = client.post(
        f"/api/v1/platform/tenants/{tid}/reactivate",
        headers=auth_header,
        json={"version_no": ver},
    )
    assert reactivate.status_code == 200, reactivate.text
    assert reactivate.json()["status"] == "ACTIVE"


def test_br_pf_009_code_validation(client: TestClient, auth_header: dict) -> None:
    resp = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload("BAD_CODE"),
    )
    assert resp.status_code == 422


def test_br_pf_010_legal_name_unique(client: TestClient, auth_header: dict) -> None:
    code1 = _unique_code("ln")
    legal = f"Unique Legal {code1}"
    first = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code1, legal),
    )
    assert first.status_code == 201, first.text
    code2 = _unique_code("ln")
    second = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code2, legal),
    )
    assert second.status_code == 409, second.text


def test_br_pf_013_deprecated_edition_blocked(
    client: TestClient, auth_header: dict
) -> None:
    ed_code = f"DEP{uuid.uuid4().hex[:8].upper()}"
    create_ed = client.post(
        "/api/v1/platform/editions",
        headers=auth_header,
        json={
            "code": ed_code,
            "name": "Deprecate Me",
            "description": "PF-002 BR-PF-013",
            "features": [
                {"feature_code": "CRM_LEAD", "is_enabled": True},
            ],
            "limits": [
                {
                    "limit_code": "MAX_USERS",
                    "limit_name": "Maximum users",
                    "limit_value": "5",
                    "limit_unit": "users",
                },
                {
                    "limit_code": "MAX_STORAGE_GB",
                    "limit_name": "Storage",
                    "limit_value": "5",
                    "limit_unit": "GB",
                },
                {
                    "limit_code": "MAX_ROLES",
                    "limit_name": "Roles",
                    "limit_value": "5",
                    "limit_unit": "roles",
                },
            ],
        },
    )
    assert create_ed.status_code == 201, create_ed.text
    eid = create_ed.json()["id"]
    ver = create_ed.json()["version_no"]
    pub = client.post(
        f"/api/v1/platform/editions/{eid}/publish",
        headers=auth_header,
        json={"version_no": ver},
    )
    assert pub.status_code == 200, pub.text
    ver = pub.json()["version_no"]
    dep = client.post(
        f"/api/v1/platform/editions/{eid}/deprecate",
        headers=auth_header,
        json={"version_no": ver, "reason": "QA BR-PF-013"},
    )
    assert dep.status_code == 200, dep.text

    payload = _register_payload(_unique_code("de"))
    payload["edition_code"] = ed_code
    blocked = client.post(
        "/api/v1/platform/tenants", headers=auth_header, json=payload
    )
    assert blocked.status_code in (400, 422), blocked.text


def test_idempotency_key(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("id")
    key = f"idem-{uuid.uuid4().hex}"
    headers = {**auth_header, "Idempotency-Key": key}
    first = client.post(
        "/api/v1/platform/tenants",
        headers=headers,
        json=_register_payload(code),
    )
    assert first.status_code == 201, first.text
    second = client.post(
        "/api/v1/platform/tenants",
        headers=headers,
        json=_register_payload(code),
    )
    assert second.status_code == 201, second.text
    assert second.json()["id"] == first.json()["id"]


def test_soft_delete_closed(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("cl")
    create = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code),
    )
    assert create.status_code == 201, create.text
    tid = create.json()["id"]
    delete = client.delete(
        f"/api/v1/platform/tenants/{tid}", headers=auth_header
    )
    assert delete.status_code == 204, delete.text
    get = client.get(f"/api/v1/platform/tenants/{tid}", headers=auth_header)
    assert get.status_code == 404


def test_audit_on_create(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("au")
    create = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code),
    )
    assert create.status_code == 201, create.text
    tid = uuid.UUID(create.json()["id"])
    db = SessionLocal()
    try:
        events = list(
            db.scalars(
                select(AuditEvent).where(
                    AuditEvent.entity_id == tid,
                    AuditEvent.event_type == "TENANT_CREATED",
                )
            ).all()
        )
        assert len(events) >= 1
    finally:
        db.close()


def test_search_and_export(client: TestClient, auth_header: dict) -> None:
    code = _unique_code("sr")
    create = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json=_register_payload(code),
    )
    assert create.status_code == 201, create.text
    search = client.get(
        "/api/v1/platform/tenants/search",
        headers=auth_header,
        params={"q": code},
    )
    assert search.status_code == 200, search.text
    assert any(i["code"] == code for i in search.json()["items"])
    export = client.get("/api/v1/platform/tenants/export", headers=auth_header)
    assert export.status_code == 200, export.text
    assert isinstance(export.json(), list)
