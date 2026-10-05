"""TD-PF-003-01 — hourly due TRIAL subscription expiry job."""

import uuid
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf003 import apply_pf003_ddl
from app.jobs.expire_due_trial_subscriptions import (
    due_trial_subscription_rows,
    run_expire_due_trial_subscriptions,
    utc_today,
)
from app.main import app
from app.models.pf import AuditEvent, Role, Subscription, SubscriptionHistory, Tenant, User
from tests.conftest import platform_admin_select, platform_session
from tests.test_pf003_subscriptions import _register_tenant


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def auth_header(client: TestClient) -> dict[str, str]:
    settings = get_settings()
    with platform_session() as db:
        apply_pf003_ddl(db)
        admin = db.scalars(platform_admin_select()).first()
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
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def _approve_tenant(client: TestClient, auth_header: dict, tenant: dict) -> dict:
    apr = client.post(
        f"/api/v1/platform/tenants/{tenant['id']}/approve",
        headers=auth_header,
        json={"version_no": tenant["version_no"]},
    )
    assert apr.status_code == 200, apr.text
    return apr.json()


def _trial_for_tenant(client: TestClient, auth_header: dict, tenant_id: str) -> dict:
    listed = client.get(
        "/api/v1/platform/subscriptions",
        headers=auth_header,
        params={"status": "TRIAL"},
    )
    assert listed.status_code == 200, listed.text
    trial = next(
        (i for i in listed.json()["items"] if i["tenant_id"] == tenant_id),
        None,
    )
    assert trial is not None
    return trial


def _set_trial_end(subscription_id: str, trial_end: date) -> None:
    with platform_session() as db:
        sub = db.get(Subscription, uuid.UUID(subscription_id))
        assert sub is not None
        sub.trial_end_date = trial_end
        if sub.end_date is None or sub.end_date < trial_end:
            sub.end_date = trial_end
        db.commit()


def test_trial_expiry_job_expires_due_and_skips_future(
    client: TestClient, auth_header: dict
) -> None:
    due_tenant = _approve_tenant(client, auth_header, _register_tenant(client, auth_header))
    future_tenant = _approve_tenant(
        client, auth_header, _register_tenant(client, auth_header)
    )
    due_trial = _trial_for_tenant(client, auth_header, due_tenant["id"])
    future_trial = _trial_for_tenant(client, auth_header, future_tenant["id"])

    today = utc_today()
    _set_trial_end(due_trial["id"], today - timedelta(days=1))
    _set_trial_end(future_trial["id"], today + timedelta(days=10))

    with platform_session() as db:
        due_rows = due_trial_subscription_rows(db, today)
        due_ids = {row[0] for row in due_rows}
        assert uuid.UUID(due_trial["id"]) in due_ids
        assert uuid.UUID(future_trial["id"]) not in due_ids

    result = run_expire_due_trial_subscriptions(as_of_utc_date=today)
    assert result.processed == 1
    assert result.failed == 0

    with platform_session() as db:
        due_sub = db.get(Subscription, uuid.UUID(due_trial["id"]))
        assert due_sub is not None
        assert due_sub.subscription_status == "EXPIRED"

        future_sub = db.get(Subscription, uuid.UUID(future_trial["id"]))
        assert future_sub is not None
        assert future_sub.subscription_status == "TRIAL"

        due_tenant_row = db.get(Tenant, uuid.UUID(due_tenant["id"]))
        assert due_tenant_row is not None
        assert due_tenant_row.status == "SUSPENDED"
        assert due_tenant_row.current_subscription_id is None

        hist = db.scalars(
            select(SubscriptionHistory).where(
                SubscriptionHistory.subscription_id == due_sub.subscription_id,
                SubscriptionHistory.change_type == "EXPIRED",
            )
        ).all()
        assert len(hist) == 1
        assert hist[0].actor_id is None

        audit = db.scalars(
            select(AuditEvent).where(
                AuditEvent.entity_id == due_sub.subscription_id,
                AuditEvent.event_type == "SUBSCRIPTION_EXPIRED",
            )
        ).all()
        assert len(audit) >= 1
        assert audit[-1].actor_id is None


def test_trial_expiry_job_idempotent_second_run(
    client: TestClient, auth_header: dict
) -> None:
    tenant = _approve_tenant(client, auth_header, _register_tenant(client, auth_header))
    trial = _trial_for_tenant(client, auth_header, tenant["id"])
    today = utc_today()
    _set_trial_end(trial["id"], today)

    first = run_expire_due_trial_subscriptions(as_of_utc_date=today)
    assert first.processed == 1
    assert first.failed == 0

    second = run_expire_due_trial_subscriptions(as_of_utc_date=today)
    assert second.processed == 0
    assert second.failed == 0

    with platform_session() as db:
        due_rows = due_trial_subscription_rows(db, today)
        assert due_rows == []
