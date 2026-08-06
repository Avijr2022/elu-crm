"""PF-003 Subscription Management tests — repeatable."""

import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf003 import apply_pf003_ddl
from app.db.session import SessionLocal
from app.main import app
from app.models.pf import AuditEvent, Role, User
from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        apply_pf003_ddl(db)
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        assert admin is not None
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


def _unique_code(prefix: str = "s") -> str:
    return f"{prefix}{uuid.uuid4().hex[:10]}"


def _register_tenant(client: TestClient, auth_header: dict) -> dict:
    code = _unique_code("st")
    resp = client.post(
        "/api/v1/platform/tenants",
        headers=auth_header,
        json={
            "code": code,
            "legal_name": f"Legal {code}",
            "trade_name": f"Trade {code}",
            "edition_code": "PROFESSIONAL",
            "email": f"{code}@example.com",
            "mobile": "9876543210",
            "primary_contact": {
                "contact_type": "PRIMARY",
                "name": "Contact",
                "email": f"c-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Street",
                "city": "Kolkata",
                "country": "India",
            },
        },
    )
    assert resp.status_code == 201, resp.text
    return resp.json()


def test_migration_idempotent(client: TestClient) -> None:
    db = SessionLocal()
    try:
        apply_pf003_ddl(db)
        apply_pf003_ddl(db)
        row = db.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='core' AND table_name='subscription_history'"
            )
        ).first()
        assert row is not None
    finally:
        db.close()


def test_list_and_tenant_subscription(client: TestClient, auth_header: dict) -> None:
    listed = client.get("/api/v1/platform/subscriptions", headers=auth_header)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] >= 1
    mine = client.get("/api/v1/tenant/subscription", headers=auth_header)
    assert mine.status_code == 200, mine.text
    assert mine.json()["status"] in {"ACTIVE", "TRIAL"}


def test_trial_activate_renew_upgrade_history(
    client: TestClient, auth_header: dict
) -> None:
    tenant = _register_tenant(client, auth_header)
    # Find TRIAL subscription for new tenant
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    assert listed.status_code == 200
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    sid = trial["id"]
    ver = trial["version_no"]

    activate = client.patch(
        f"/api/v1/platform/subscriptions/{sid}",
        headers=auth_header,
        json={"version_no": ver},
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"
    ver = activate.json()["version_no"]

    end = (date.today() + timedelta(days=365)).isoformat()
    renew = client.post(
        f"/api/v1/platform/subscriptions/{sid}/renew",
        headers=auth_header,
        json={"version_no": ver, "end_date": end, "billing_cycle": "ANNUAL"},
    )
    assert renew.status_code == 200, renew.text
    assert renew.json()["billing_cycle"] == "ANNUAL"
    ver = renew.json()["version_no"]

    upgrade = client.post(
        f"/api/v1/platform/subscriptions/{sid}/upgrade",
        headers=auth_header,
        json={"version_no": ver, "edition_code": "ENTERPRISE", "seat_count": 100},
    )
    assert upgrade.status_code == 200, upgrade.text
    assert upgrade.json()["edition_code"] == "ENTERPRISE"
    ver = upgrade.json()["version_no"]

    hist = client.get(
        f"/api/v1/platform/subscriptions/{sid}/history", headers=auth_header
    )
    assert hist.status_code == 200, hist.text
    types = {h["change_type"] for h in hist.json()}
    assert "ACTIVATED" in types or "CREATED" in types or "RENEWED" in types


def test_br_pf_020_end_before_start(client: TestClient, auth_header: dict) -> None:
    tenant = _register_tenant(client, auth_header)
    # cancel existing trial first via expire path after finding it
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    client.delete(
        f"/api/v1/platform/subscriptions/{trial['id']}",
        headers=auth_header,
        params={
            "version_no": trial["version_no"],
            "reason": "Replace for date test",
        },
    )
    bad = client.post(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        json={
            "tenant_id": tenant["id"],
            "edition_code": "PROFESSIONAL",
            "seat_count": 10,
            "billing_cycle": "MONTHLY",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() - timedelta(days=1)).isoformat(),
            "status": "ACTIVE",
        },
    )
    assert bad.status_code in (400, 422), bad.text


def test_br_pf_021_seat_over_edition(client: TestClient, auth_header: dict) -> None:
    tenant = _register_tenant(client, auth_header)
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    # PROFESSIONAL MAX_USERS=50
    upd = client.put(
        f"/api/v1/platform/subscriptions/{trial['id']}",
        headers=auth_header,
        json={"version_no": trial["version_no"], "seat_count": 500},
    )
    assert upd.status_code in (400, 422), upd.text


def test_br_pf_019_one_current(client: TestClient, auth_header: dict) -> None:
    # Seed EIIP001 already ACTIVE — creating another ACTIVE must conflict
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
        ).first()
        tid = str(admin.tenant_id)
    resp = client.post(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        json={
            "tenant_id": tid,
            "edition_code": "PROFESSIONAL",
            "seat_count": 10,
            "billing_cycle": "MONTHLY",
            "start_date": date.today().isoformat(),
            "end_date": (date.today() + timedelta(days=30)).isoformat(),
            "status": "ACTIVE",
        },
    )
    assert resp.status_code == 409, resp.text


def test_expire_cascades_tenant_suspend(
    client: TestClient, auth_header: dict
) -> None:
    tenant = _register_tenant(client, auth_header)
    # approve tenant first so status ACTIVE
    apr = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=auth_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    # activate then expire
    act = client.patch(
        f"/api/v1/platform/subscriptions/{trial['id']}",
        headers=auth_header,
        json={"version_no": trial["version_no"]},
    )
    assert act.status_code == 200, act.text
    ver = act.json()["version_no"]
    exp = client.post(
        f"/api/v1/platform/subscriptions/{trial['id']}/expire",
        headers=auth_header,
        json={"version_no": ver},
    )
    assert exp.status_code == 200, exp.text
    assert exp.json()["status"] == "EXPIRED"
    tget = client.get(
        f"/api/v1/platform/tenants/{tenant['id']}", headers=auth_header
    )
    assert tget.status_code == 200
    assert tget.json()["status"] == "SUSPENDED"


def test_usage_and_export(client: TestClient, auth_header: dict) -> None:
    usage = client.get("/api/v1/tenant/subscription/usage", headers=auth_header)
    assert usage.status_code == 200, usage.text
    assert "seat_count" in usage.json()
    export = client.get(
        "/api/v1/platform/subscriptions/export", headers=auth_header
    )
    assert export.status_code == 200
    assert isinstance(export.json(), list)


def test_audit_on_activate(client: TestClient, auth_header: dict) -> None:
    tenant = _register_tenant(client, auth_header)
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    act = client.patch(
        f"/api/v1/platform/subscriptions/{trial['id']}",
        headers=auth_header,
        json={"version_no": trial["version_no"]},
    )
    assert act.status_code == 200
    sid = uuid.UUID(trial["id"])
    with platform_session() as db:
        events = list(
            db.scalars(
                select(AuditEvent).where(
                    AuditEvent.entity_id == sid,
                    AuditEvent.event_type == "SUBSCRIPTION_ACTIVATED",
                )
            ).all()
        )
        assert len(events) >= 1


def test_schema_constraints_and_uk(client: TestClient) -> None:
    db = SessionLocal()
    try:
        apply_pf003_ddl(db)
        apply_pf003_ddl(db)
        uk = db.execute(
            text(
                "SELECT 1 FROM pg_indexes WHERE schemaname='core' "
                "AND indexname='uk_subscription_one_current'"
            )
        ).first()
        assert uk is not None
        fk = db.execute(
            text(
                "SELECT 1 FROM pg_constraint WHERE conname='fk_tenant_current_subscription'"
            )
        ).first()
        assert fk is not None
        seat_ck = db.execute(
            text(
                "SELECT 1 FROM pg_constraint WHERE conname='ck_subscription_seat_count'"
            )
        ).first()
        assert seat_ck is not None
        nn = db.execute(
            text(
                "SELECT is_nullable FROM information_schema.columns "
                "WHERE table_schema='core' AND table_name='subscription' "
                "AND column_name='seat_count'"
            )
        ).first()
        assert nn is not None and nn[0] == "NO"
    finally:
        db.close()


def test_openapi_includes_subscriptions(client: TestClient) -> None:
    spec = client.get("/openapi.json")
    assert spec.status_code == 200
    paths = spec.json()["paths"]
    required = [
        "/api/v1/platform/subscriptions",
        "/api/v1/platform/subscriptions/search",
        "/api/v1/platform/subscriptions/export",
        "/api/v1/platform/subscriptions/{subscription_id}",
        "/api/v1/platform/subscriptions/{subscription_id}/renew",
        "/api/v1/platform/subscriptions/{subscription_id}/upgrade",
        "/api/v1/platform/subscriptions/{subscription_id}/reactivate",
        "/api/v1/platform/subscriptions/{subscription_id}/history",
        "/api/v1/tenant/subscription",
        "/api/v1/tenant/subscription/usage",
    ]
    for p in required:
        assert p in paths, f"missing OpenAPI path {p}"


def test_cancel_cascades_offboarding(client: TestClient, auth_header: dict) -> None:
    tenant = _register_tenant(client, auth_header)
    apr = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=auth_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant["id"]),
        None,
    )
    assert trial is not None
    cancel = client.delete(
        f"/api/v1/platform/subscriptions/{trial['id']}",
        headers=auth_header,
        params={"version_no": trial["version_no"], "reason": "QA cancel cascade"},
    )
    assert cancel.status_code == 204, cancel.text
    tget = client.get(
        f"/api/v1/platform/tenants/{tenant['id']}", headers=auth_header
    )
    assert tget.status_code == 200
    assert tget.json()["status"] == "OFFBOARDING"
