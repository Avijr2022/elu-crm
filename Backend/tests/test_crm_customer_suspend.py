"""REQ-CRM-028 Customer Suspension.

Covers BR-CRM-047 (Finance-only), BR-CRM-049 (block new SAL transactions) and
BR-CRM-055 (reason code + comment), plus tenant isolation, status history, the
``customer.suspended`` audit event, transactional rollback and generic-PATCH
bypass prevention.

REQ-CRM-029 (release suspension / reactivate) is deliberately NOT implemented.
"""

import uuid
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.crm import Customer, CustomerStatusHistory
from app.models.pf import AuditEvent, Role, User
from tests.conftest import platform_admin_select, platform_session

USER_PASSWORD = "Req028Smoke!234"

SUSPEND_REASON = "CREDIT_RISK"
SUSPEND_COMMENT = "Outstanding overdue beyond 90 days - credit hold"


@pytest.fixture(scope="module")
def client():
    # raise_server_exceptions=False so the forced-failure rollback test can observe
    # the 500 instead of the client re-raising the RuntimeError.
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
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


def _role_token(client: TestClient, role_code: str) -> tuple[str, str]:
    """Create an ACTIVE user holding ``role_code`` in the seed tenant and log in.

    Returns ``(token, user_id)``.
    """
    settings = get_settings()
    _ = settings
    email = f"req028-{role_code.lower()}-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        assert role is not None, f"role {role_code} not seeded for the tenant"
        user = User(
            tenant_id=admin.tenant_id,
            organization_id=admin.organization_id,
            role_id=role.role_id,
            employee_code=f"R28{uuid.uuid4().hex[:6].upper()}",
            first_name="REQ028",
            last_name=role_code.title(),
            display_name=f"REQ028 {role_code}",
            email=email,
            password_hash=hash_password(USER_PASSWORD),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        user_id = str(user.user_id)
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": "EIIP001"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"], user_id


@pytest.fixture(scope="module")
def finance(client: TestClient, admin_token: str) -> tuple[str, str]:
    return _role_token(client, "FINANCE_USER")


@pytest.fixture(scope="module")
def sales_manager(client: TestClient, admin_token: str) -> tuple[str, str]:
    return _role_token(client, "SALES_MANAGER")


@pytest.fixture(scope="module")
def sales_executive(client: TestClient, admin_token: str) -> tuple[str, str]:
    return _role_token(client, "SALES_EXECUTIVE")


@pytest.fixture(scope="module")
def tenant_admin(client: TestClient, admin_token: str) -> tuple[str, str]:
    return _role_token(client, "TENANT_ADMIN")


@pytest.fixture(scope="module")
def community_token(client: TestClient, admin_token: str) -> str:
    with platform_session() as db:
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        if user:
            user.password_hash = hash_password("Community@12345")
            db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "community@euphoriainfotech.com",
            "password": "Community@12345",
            "tenant_code": "COMU001",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_active_customer(client: TestClient, token: str) -> str:
    """Create a customer and drive it PROSPECT -> ACTIVE (BR-CRM-043/044)."""
    headers = _auth(token)
    create = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"Suspend Cust {uuid.uuid4().hex[:8]}"},
    )
    assert create.status_code == 201, create.text
    cid = create.json()["customer_id"]

    contact = client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=headers,
        json={"first_name": "Primary", "is_primary": True},
    )
    assert contact.status_code == 201, contact.text
    address = client.post(
        f"/api/v1/crm/customers/{cid}/addresses",
        headers=headers,
        json={"address_type": "REGISTERED", "address_line1": "1 Test Road"},
    )
    assert address.status_code == 201, address.text
    activate = client.patch(
        f"/api/v1/crm/customers/{cid}", headers=headers, json={"status": "ACTIVE"}
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"
    return cid


def _suspend(client: TestClient, token: str, cid: str):
    return client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        headers=_auth(token),
        json={"reason_code": SUSPEND_REASON, "comment": SUSPEND_COMMENT},
    )


def _accepted_quotation(client: TestClient, token: str, cid: str) -> str:
    """Drive a quotation DRAFT -> SUBMITTED -> APPROVED -> SENT -> ACCEPTED."""
    headers = _auth(token)
    create = client.post(
        "/api/v1/sal/quotations", headers=headers, json={"customer_id": cid}
    )
    assert create.status_code == 201, create.text
    qid = create.json()["quotation_id"]
    line = client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Item", "qty": "1", "unit_price": "100"},
    )
    assert line.status_code == 201, line.text
    for target in ("SUBMITTED", "APPROVED", "SENT", "ACCEPTED"):
        step = client.patch(
            f"/api/v1/sal/quotations/{qid}/status",
            headers=headers,
            json={"status": target},
        )
        assert step.status_code == 200, f"{target}: {step.text}"
    return qid


def _history(cid: str):
    with platform_session() as db:
        return list(
            db.scalars(
                select(CustomerStatusHistory).where(
                    CustomerStatusHistory.customer_id == UUID(cid)
                )
            ).all()
        )


def _audit_events(cid: str, event_type: str = "customer.suspended"):
    with platform_session() as db:
        return list(
            db.scalars(
                select(AuditEvent).where(
                    AuditEvent.entity_id == UUID(cid),
                    AuditEvent.event_type == event_type,
                )
            ).all()
        )


def _status_of(cid: str) -> str:
    with platform_session() as db:
        return db.scalars(
            select(Customer.status).where(Customer.customer_id == UUID(cid))
        ).first()


# --------------------------------------------------------------------- authz


def test_suspend_requires_authentication(client: TestClient, admin_token: str):
    cid = _create_active_customer(client, admin_token)
    resp = client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        json={"reason_code": SUSPEND_REASON, "comment": SUSPEND_COMMENT},
    )
    assert resp.status_code in (401, 403), resp.text
    assert _status_of(cid) == "ACTIVE"


@pytest.mark.parametrize(
    "fixture_name",
    ["sales_manager", "sales_executive", "tenant_admin"],
)
def test_suspend_denied_for_non_finance_roles(
    client: TestClient, admin_token: str, request, fixture_name: str
):
    """BR-CRM-047: suspension is Finance User only, even for Tenant Admin."""
    token, _ = request.getfixturevalue(fixture_name)
    cid = _create_active_customer(client, admin_token)
    resp = _suspend(client, token, cid)
    assert resp.status_code == 403, resp.text
    assert _status_of(cid) == "ACTIVE"
    assert _history(cid) == []


def test_suspend_allowed_for_finance_user(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    resp = _suspend(client, token, cid)
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "SUSPENDED"


# ---------------------------------------------------------------- validation


@pytest.mark.parametrize(
    "payload",
    [
        {"reason_code": "", "comment": SUSPEND_COMMENT},
        {"reason_code": "   ", "comment": SUSPEND_COMMENT},
        {"reason_code": SUSPEND_REASON, "comment": ""},
        {"reason_code": SUSPEND_REASON, "comment": "  "},
        {"comment": SUSPEND_COMMENT},
        {"reason_code": SUSPEND_REASON},
        {},
    ],
)
def test_suspend_rejects_blank_or_missing_reason(
    client: TestClient,
    admin_token: str,
    finance: tuple[str, str],
    payload: dict,
):
    """BR-CRM-055: reason_code and comment are both mandatory and non-blank."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    resp = client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        headers=_auth(token),
        json=payload,
    )
    assert resp.status_code == 422, resp.text
    assert _status_of(cid) == "ACTIVE"
    assert _history(cid) == []


# ------------------------------------------------------------ state machine


def test_suspend_only_from_active(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    token, _ = finance
    headers = _auth(admin_token)
    create = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"Prospect Only {uuid.uuid4().hex[:8]}"},
    )
    assert create.status_code == 201, create.text
    cid = create.json()["customer_id"]  # PROSPECT, not ACTIVE

    resp = _suspend(client, token, cid)
    assert resp.status_code == 422, resp.text
    assert "ACTIVE" in resp.text
    assert _status_of(cid) == "PROSPECT"


def test_suspend_twice_is_conflict(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200
    second = _suspend(client, token, cid)
    assert second.status_code == 409, second.text
    assert len(_history(cid)) == 1


# ------------------------------------------------- history / audit / rollback


def test_suspend_records_status_history(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    token, finance_user_id = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200

    rows = _history(cid)
    assert len(rows) == 1, rows
    row = rows[0]
    assert row.from_status == "ACTIVE"
    assert row.to_status == "SUSPENDED"
    assert row.reason == f"[{SUSPEND_REASON}] {SUSPEND_COMMENT}"
    assert str(row.actor_id) == finance_user_id


def test_suspend_writes_customer_suspended_audit_event(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    token, finance_user_id = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200

    events = _audit_events(cid)
    assert len(events) == 1, events
    event = events[0]
    assert event.event_category == "CRM"
    assert event.entity_type == "customer"
    assert str(event.actor_id) == finance_user_id
    assert event.tenant_id is not None
    payload = event.payload_json
    assert SUSPEND_REASON in payload
    assert "SUSPENDED" in payload


def test_suspend_rolls_back_status_history_and_audit_on_failure(
    client: TestClient,
    admin_token: str,
    finance: tuple[str, str],
    monkeypatch: pytest.MonkeyPatch,
):
    """Requirement 5: a mid-transaction failure must leave NO partial state."""
    from app.services.crm import customer_service as customer_service_module

    token, _ = finance
    cid = _create_active_customer(client, admin_token)

    def _boom(*args, **kwargs):
        raise RuntimeError("forced audit failure (REQ-CRM-028 rollback test)")

    monkeypatch.setattr(customer_service_module, "write_audit_event", _boom)
    resp = _suspend(client, token, cid)
    assert resp.status_code == 500, resp.text

    # The status must NOT have been persisted, and neither history nor audit.
    assert _status_of(cid) == "ACTIVE"
    assert _history(cid) == []
    assert _audit_events(cid) == []


# ------------------------------------------------- PATCH bypass prevention


def test_patch_cannot_set_suspended(
    client: TestClient,
    admin_token: str,
    sales_manager: tuple[str, str],
    tenant_admin: tuple[str, str],
):
    """Requirement 6: generic PATCH must not bypass Finance-only suspension."""
    cid = _create_active_customer(client, admin_token)
    for token, _ in (sales_manager, tenant_admin):
        resp = client.patch(
            f"/api/v1/crm/customers/{cid}",
            headers=_auth(token),
            json={"status": "SUSPENDED"},
        )
        assert resp.status_code == 403, resp.text
    assert _status_of(cid) == "ACTIVE"
    assert _history(cid) == []
    # The admin token also must not be able to PATCH into SUSPENDED.
    resp = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "SUSPENDED"},
    )
    assert resp.status_code == 403, resp.text
    assert _status_of(cid) == "ACTIVE"


def test_patch_cannot_release_suspended_customer(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """REQ-CRM-029 is out of scope: SUSPENDED must not be releasable via PATCH."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200

    resp = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"status": "ACTIVE"},
    )
    assert resp.status_code == 403, resp.text
    assert _status_of(cid) == "SUSPENDED"


def test_patch_still_updates_unrelated_fields_for_suspended_customer(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """Bypass prevention must not break ordinary edits (Requirement 8)."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200

    resp = client.patch(
        f"/api/v1/crm/customers/{cid}",
        headers=_auth(admin_token),
        json={"notes": "credit hold under review"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "SUSPENDED"
    assert resp.json()["notes"] == "credit hold under review"


# ------------------------------------------------------ tenant isolation


def test_suspend_is_tenant_scoped(
    client: TestClient,
    admin_token: str,
    finance: tuple[str, str],
    community_token: str,
):
    """Requirement 4 / BR-CRM-054: another tenant's customer is a 404, untouched."""
    token, _ = finance
    headers = _auth(community_token)
    create = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"Community Cust {uuid.uuid4().hex[:8]}"},
    )
    assert create.status_code == 201, create.text
    foreign_cid = create.json()["customer_id"]

    resp = _suspend(client, token, foreign_cid)
    assert resp.status_code == 404, resp.text
    assert _status_of(foreign_cid) == "PROSPECT"


def test_suspend_unknown_customer_is_404(
    client: TestClient, finance: tuple[str, str]
):
    token, _ = finance
    resp = _suspend(client, token, str(uuid.uuid4()))
    assert resp.status_code == 404, resp.text


# --------------------------------------------------------- SAL enforcement


def test_new_quotation_blocked_for_suspended_customer(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """BR-CRM-049: suspended customers cannot have new quotations."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    assert _suspend(client, token, cid).status_code == 200

    resp = client.post(
        "/api/v1/sal/quotations",
        headers=_auth(admin_token),
        json={"customer_id": cid},
    )
    assert resp.status_code == 422, resp.text
    assert "BR-CRM-049" in resp.text


def test_sales_order_conversion_blocked_for_suspended_customer(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """BR-CRM-049: a NEW sales order cannot be created after suspension."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    qid = _accepted_quotation(client, admin_token, cid)
    assert _suspend(client, token, cid).status_code == 200

    resp = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=_auth(admin_token)
    )
    assert resp.status_code == 422, resp.text
    assert "BR-CRM-049" in resp.text


def test_draft_sales_order_confirm_blocked_for_suspended_customer(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """BR-CRM-049: an existing DRAFT order cannot be confirmed once suspended."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    qid = _accepted_quotation(client, admin_token, cid)
    converted = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=_auth(admin_token)
    )
    assert converted.status_code == 201, converted.text
    so_id = converted.json()["sales_order_id"]

    assert _suspend(client, token, cid).status_code == 200

    resp = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/confirm", headers=_auth(admin_token)
    )
    assert resp.status_code == 422, resp.text
    assert "BR-CRM-049" in resp.text


def test_idempotent_conversion_is_preserved_after_suspension(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """Requirement 7: re-converting an already-converted quotation still returns
    the existing sales order rather than being blocked by the suspension."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    qid = _accepted_quotation(client, admin_token, cid)

    first = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=_auth(admin_token)
    )
    assert first.status_code == 201, first.text
    so_id = first.json()["sales_order_id"]

    assert _suspend(client, token, cid).status_code == 200

    again = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=_auth(admin_token)
    )
    assert again.status_code == 201, again.text
    assert again.json()["sales_order_id"] == so_id
    assert "already exists" in again.json()["message"]


def test_ongoing_sales_order_and_payments_are_not_blocked(
    client: TestClient, admin_token: str, finance: tuple[str, str]
):
    """Requirement 7: suspension must not break existing orders or their payments."""
    token, _ = finance
    cid = _create_active_customer(client, admin_token)
    qid = _accepted_quotation(client, admin_token, cid)
    converted = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=_auth(admin_token)
    )
    assert converted.status_code == 201, converted.text
    so_id = converted.json()["sales_order_id"]
    confirmed = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/confirm", headers=_auth(admin_token)
    )
    assert confirmed.status_code == 200, confirmed.text

    assert _suspend(client, token, cid).status_code == 200

    # Read paths and downstream payment recording must be unaffected by suspension.
    assert (
        client.get(f"/api/v1/sal/sales-orders/{so_id}", headers=_auth(admin_token)).status_code
        == 200
    )
    assert (
        client.get(f"/api/v1/sal/quotations/{qid}", headers=_auth(admin_token)).status_code
        == 200
    )
    stub = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/record-payment-stub",
        headers=_auth(admin_token),
        json={"payment_status": "RECEIVED", "amount": "100"},
    )
    # Whatever the endpoint's own preconditions, suspension must not be the blocker.
    assert "BR-CRM-049" not in stub.text, stub.text
