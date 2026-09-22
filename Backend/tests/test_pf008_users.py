"""PF-008 CORE focused tests — user CRUD, invitation/activation, lifecycle, seats, passwords.

Evidence mapping to `ELU-BFS-PF-008`:
  AC-PF-008-01 activation with a 72 h invitation token; AC-PF-008-02 seat-limit rejection;
  AC-PF-008-03 JWT claims carry tenant_id/role; AC-PF-008-04 five failures -> LOCKED;
  AC-PF-008-05 deactivated user cannot log in; AC-PF-008-07 tenant-scoped user list.
  BR-PF-051 email unique per tenant; BR-PF-052 seats; BR-PF-054 72 h expiry;
  BR-PF-055 lockout; BR-PF-057 refresh revocation; BR-PF-060 last Tenant Admin guard.

Implementation decisions under test are recorded in
``Documentation/PF008_CORE_IMPLEMENTATION_MAP.md`` (D4/D6/D7/D8/D11).

Each module run provisions its own tenant through the platform API (unique code) so the
tests neither depend on nor disturb the seeded EIIP001 tenant. Setup/assertions that must
cross the tenant boundary use ``platform_session`` (the RLS-aware helper from tests/conftest).
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.main import app
from app.models.pf import Organization, Role, Subscription, User, UserInvite
from app.core.security import hash_password
from tests.conftest import platform_session

API = "/api/v1"
PASSWORD = "Pf008Admin@1"
USER_PASSWORD = "Pf008User@12"


def _unique_code(prefix: str) -> str:
    return f"{prefix}{uuid.uuid4().hex[:8]}"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_header(client: TestClient) -> dict:
    """Seed admin of EIIP001 (PLATFORM_ADMIN) used to provision throwaway tenants."""
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == "admin@euphoriainfotech.com")
        ).first()
        assert admin is not None, "seed admin missing"
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


def _create_approved_tenant(client: TestClient, header: dict, code: str) -> dict:
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
                "name": "Primary Contact",
                "email": f"contact-{code}@example.com",
                "is_primary": True,
            },
            "registered_address": {
                "address_type": "REGISTERED",
                "line1": "1 Identity Road",
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
    return approve.json()


def _provision_tenant_admin(tenant_id: uuid.UUID, email: str, password: str) -> uuid.UUID:
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(Organization.tenant_id == tenant_id)
        ).first()
        assert org is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id, Role.role_code == "TENANT_ADMIN"
            )
        ).first()
        assert role is not None, "TENANT_ADMIN role missing after provisioning"
        user = User(
            tenant_id=tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            first_name="Tenant",
            last_name="Admin",
            display_name="Tenant Admin",
            email=email.lower(),
            password_hash=hash_password(password),
            account_status="ACTIVE",
        )
        db.add(user)
        db.commit()
        return user.user_id


def _set_seats(tenant_id: str, seats: int) -> None:
    """Test setup: give the throwaway tenant headroom under BR-PF-052.

    The Professional edition caps MAX_USERS at 50, so 45 keeps the module's fixtures inside
    both the subscription seat_count and the edition limit without touching product rules.
    """
    with platform_session() as db:
        subscription = db.scalars(
            select(Subscription).where(Subscription.tenant_id == uuid.UUID(tenant_id))
        ).first()
        assert subscription is not None
        subscription.seat_count = seats
        db.commit()


@pytest.fixture(scope="module")
def tenant_a(client: TestClient, platform_header: dict) -> dict:
    code = _unique_code("p8a")
    tenant = _create_approved_tenant(client, platform_header, code)
    email = f"admin-{code}@example.com"
    user_id = _provision_tenant_admin(uuid.UUID(tenant["id"]), email, PASSWORD)
    _set_seats(tenant["id"], 45)
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD, "tenant_code": code},
    )
    assert login.status_code == 200, login.text
    return {
        "code": code,
        "id": tenant["id"],
        "admin_email": email,
        "admin_id": str(user_id),
        "header": {"Authorization": f"Bearer {login.json()['access_token']}"},
    }


@pytest.fixture(scope="module")
def tenant_b(client: TestClient, platform_header: dict) -> dict:
    code = _unique_code("p8b")
    tenant = _create_approved_tenant(client, platform_header, code)
    email = f"admin-{code}@example.com"
    user_id = _provision_tenant_admin(uuid.UUID(tenant["id"]), email, PASSWORD)
    _set_seats(tenant["id"], 45)
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": PASSWORD, "tenant_code": code},
    )
    assert login.status_code == 200, login.text
    return {
        "code": code,
        "id": tenant["id"],
        "admin_email": email,
        "admin_id": str(user_id),
        "header": {"Authorization": f"Bearer {login.json()['access_token']}"},
    }


def _invite(client: TestClient, tenant: dict, *, email: str, role_code: str = "SALES_EXECUTIVE",
            password: str | None = None, **extra) -> tuple[int, dict]:
    payload = {
        "email": email,
        "first_name": "New",
        "last_name": "User",
        "role_code": role_code,
    }
    if password:
        payload["password"] = password
    payload.update(extra)
    resp = client.post(f"{API}/users", headers=tenant["header"], json=payload)
    return resp.status_code, (resp.json() if resp.content else {})


# ---------------------------------------------------------------- authorization
def test_users_endpoints_require_authentication(client: TestClient) -> None:
    assert client.get(f"{API}/users").status_code == 401
    assert client.post(f"{API}/users", json={}).status_code == 401
    assert client.get(f"{API}/users/export").status_code == 401


def test_non_admin_role_is_forbidden_but_self_profile_works(
    client: TestClient, tenant_a: dict
) -> None:
    email = f"exec-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    assert login.status_code == 200, login.text
    header = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.get(f"{API}/users", headers=header).status_code == 403
    assert client.get(f"{API}/users/export", headers=header).status_code == 403
    me = client.get(f"{API}/users/me", headers=header)
    assert me.status_code == 200, me.text
    assert me.json()["email"] == email


# --------------------------------------------------------- invitation lifecycle
def test_invite_creates_invited_user_with_token(client: TestClient, tenant_a: dict) -> None:
    email = f"invited-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body
    assert body["account_status"] == "INVITED"
    assert body["invite_token"], "invitation token must be returned once"
    assert body["invited_at"] is not None
    expires = datetime.fromisoformat(body["invite_expires_on"])
    delta = expires - datetime.now(timezone.utc)
    assert timedelta(hours=71) < delta <= timedelta(hours=72, minutes=1)  # BR-PF-054


def test_activation_with_invite_token_issues_tokens_and_marks_invite_used(
    client: TestClient, tenant_a: dict
) -> None:
    email = f"activate-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body
    token = body["invite_token"]

    activate = client.post(f"{API}/auth/register", json={"token": token, "password": USER_PASSWORD})
    assert activate.status_code == 200, activate.text
    assert activate.json()["access_token"]

    me = client.get(
        f"{API}/auth/me",
        headers={"Authorization": f"Bearer {activate.json()['access_token']}"},
    )
    assert me.status_code == 200, me.text
    assert me.json()["tenant_code"] == tenant_a["code"]  # AC-PF-008-03
    assert me.json()["role_code"] == "SALES_EXECUTIVE"

    detail = client.get(f"{API}/users/{body['user_id']}", headers=tenant_a["header"]).json()
    assert detail["account_status"] == "ACTIVE"
    assert detail["activated_at"] is not None

    replay = client.post(f"{API}/auth/register", json={"token": token, "password": USER_PASSWORD})
    assert replay.status_code == 401, "an invitation token is single-use"


def test_expired_invitation_is_rejected_and_marked_expired(
    client: TestClient, tenant_a: dict
) -> None:
    email = f"expire-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body
    with platform_session() as db:
        invite = db.scalars(
            select(UserInvite).where(UserInvite.user_id == uuid.UUID(body["user_id"]))
        ).first()
        assert invite is not None
        invite.expires_on = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()

    resp = client.post(
        f"{API}/auth/register", json={"token": body["invite_token"], "password": USER_PASSWORD}
    )
    assert resp.status_code == 401, resp.text
    detail = client.get(f"{API}/users/{body['user_id']}", headers=tenant_a["header"]).json()
    assert detail["account_status"] == "EXPIRED"  # D6 lazy expiry


def test_reinvite_issues_a_fresh_token(client: TestClient, tenant_a: dict) -> None:
    email = f"reinvite-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body
    first_token = body["invite_token"]

    again = client.post(
        f"{API}/users/{body['user_id']}/reinvite", headers=tenant_a["header"]
    )
    assert again.status_code == 200, again.text
    assert again.json()["invite_token"] and again.json()["invite_token"] != first_token

    stale = client.post(
        f"{API}/auth/register", json={"token": first_token, "password": USER_PASSWORD}
    )
    assert stale.status_code == 401, "the superseded invitation must be cancelled"
    fresh = client.post(
        f"{API}/auth/register",
        json={"token": again.json()["invite_token"], "password": USER_PASSWORD},
    )
    assert fresh.status_code == 200, fresh.text


def test_email_is_unique_within_the_tenant(client: TestClient, tenant_a: dict) -> None:
    email = f"dupe-{uuid.uuid4().hex[:8]}@example.com"
    assert _invite(client, tenant_a, email=email)[0] == 201
    status, body = _invite(client, tenant_a, email=email)
    assert status == 409, body


# ----------------------------------------------------------------------- seats
def test_seat_limit_blocks_invitation(client: TestClient, tenant_a: dict) -> None:
    with platform_session() as db:
        subscription = db.scalars(
            select(Subscription).where(Subscription.tenant_id == uuid.UUID(tenant_a["id"]))
        ).first()
        assert subscription is not None
        original = subscription.seat_count
        subscription.seat_count = 1  # only the Tenant Admin fits
        db.commit()
    try:
        status, body = _invite(client, tenant_a, email=f"seat-{uuid.uuid4().hex[:8]}@example.com")
        assert status == 422, body
        assert "BR-PF-052" in str(body) or "seat" in str(body).lower()
    finally:
        with platform_session() as db:
            subscription = db.scalars(
                select(Subscription).where(Subscription.tenant_id == uuid.UUID(tenant_a["id"]))
            ).first()
            subscription.seat_count = original
            db.commit()


# ------------------------------------------------------------------- lifecycle
def test_five_failed_logins_lock_the_account(client: TestClient, tenant_a: dict) -> None:
    email = f"lock-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    for _ in range(5):
        bad = client.post(
            f"{API}/auth/login",
            json={"email": email, "password": "WrongPassword@1", "tenant_code": tenant_a["code"]},
        )
        assert bad.status_code == 401, bad.text

    sixth = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    assert sixth.status_code == 403, sixth.text  # AC-PF-008-04

    detail = client.get(f"{API}/users/{body['user_id']}", headers=tenant_a["header"]).json()
    assert detail["account_status"] == "LOCKED"
    with platform_session() as db:
        user = db.get(User, uuid.UUID(body["user_id"]))
        assert user.failed_login_count >= 5  # BR-PF-055
        assert user.locked_until is not None
        assert user.locked_until > datetime.now(timezone.utc)


def test_lock_is_released_after_the_30_minute_window(client: TestClient, tenant_a: dict) -> None:
    email = f"unlock-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    for _ in range(5):
        client.post(
            f"{API}/auth/login",
            json={"email": email, "password": "WrongPassword@1", "tenant_code": tenant_a["code"]},
        )
    with platform_session() as db:
        user = db.get(User, uuid.UUID(body["user_id"]))
        user.locked_until = datetime.now(timezone.utc) - timedelta(minutes=1)
        db.commit()

    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    assert login.status_code == 200, login.text  # D7 lazy auto-unlock
    detail = client.get(f"{API}/users/{body['user_id']}", headers=tenant_a["header"]).json()
    assert detail["account_status"] == "ACTIVE"


def test_deactivate_blocks_login_and_rejects_refresh(client: TestClient, tenant_a: dict) -> None:
    email = f"deact-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    refresh_token = login.json()["refresh_token"]

    deleted = client.delete(f"{API}/users/{body['user_id']}", headers=tenant_a["header"])
    assert deleted.status_code == 200, deleted.text
    assert deleted.json()["account_status"] == "INACTIVE"
    assert deleted.json()["deactivated_at"] is not None

    blocked = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    assert blocked.status_code == 403, blocked.text  # AC-PF-008-05

    revoked = client.post(f"{API}/auth/refresh", json={"refresh_token": refresh_token})
    assert revoked.status_code == 401, revoked.text  # BR-PF-057 (D4)


def test_last_active_tenant_admin_cannot_be_deactivated(client: TestClient, tenant_b: dict) -> None:
    resp = client.delete(f"{API}/users/{tenant_b['admin_id']}", headers=tenant_b["header"])
    assert resp.status_code == 422, resp.text  # BR-PF-060


def test_illegal_status_transition_is_rejected(client: TestClient, tenant_a: dict) -> None:
    email = f"trans-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body
    resp = client.patch(
        f"{API}/users/{body['user_id']}",
        headers=tenant_a["header"],
        json={"account_status": "LOCKED", "version_no": body["version_no"]},
    )
    assert resp.status_code == 422, resp.text  # INVITED -> LOCKED is illegal


# -------------------------------------------------------------------- passwords
def test_change_password_flow(client: TestClient, tenant_a: dict) -> None:
    email = f"chpw-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    header = {"Authorization": f"Bearer {login.json()['access_token']}"}
    new_password = "Pf008Changed@9"

    changed = client.post(
        f"{API}/auth/change-password",
        headers=header,
        json={"current_password": USER_PASSWORD, "new_password": new_password},
    )
    assert changed.status_code == 200, changed.text

    wrong_current = client.post(
        f"{API}/auth/change-password",
        headers=header,
        json={"current_password": "NotThePassword@1", "new_password": "Another@12345"},
    )
    assert wrong_current.status_code == 401, wrong_current.text

    old = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    assert old.status_code == 401, old.text
    new = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": new_password, "tenant_code": tenant_a["code"]},
    )
    assert new.status_code == 200, new.text


def test_admin_reset_password_issues_token_and_reset_works(
    client: TestClient, tenant_a: dict
) -> None:
    email = f"reset-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body

    issued = client.post(
        f"{API}/users/{body['user_id']}/reset-password", headers=tenant_a["header"]
    )
    assert issued.status_code == 200, issued.text
    reset_token = issued.json()["reset_token"]
    assert reset_token, "D11 — the admin path returns the token while NTF-PF-008-03 is deferred"

    reset_password = "Pf008Reset@77"
    applied = client.post(
        f"{API}/auth/reset-password", json={"token": reset_token, "password": reset_password}
    )
    assert applied.status_code == 200, applied.text

    replay = client.post(
        f"{API}/auth/reset-password", json={"token": reset_token, "password": "Other@123456"}
    )
    assert replay.status_code == 422, replay.text

    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": reset_password, "tenant_code": tenant_a["code"]},
    )
    assert login.status_code == 200, login.text


def test_forgot_password_is_non_enumerable(client: TestClient, tenant_a: dict) -> None:
    known = client.post(
        f"{API}/auth/forgot-password",
        json={"tenant_code": tenant_a["code"], "email": tenant_a["admin_email"]},
    )
    unknown = client.post(
        f"{API}/auth/forgot-password",
        json={"tenant_code": tenant_a["code"], "email": "nobody@example.com"},
    )
    assert known.status_code == 200 and unknown.status_code == 200, (known.text, unknown.text)
    assert known.json()["message"] == unknown.json()["message"]
    assert "reset_token" not in known.json()  # D11 — never returned on the public path


def test_logout_revokes_refresh_token(client: TestClient, tenant_a: dict) -> None:
    email = f"logout-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    header = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert client.post(f"{API}/auth/logout", headers=header).status_code == 200
    revoked = client.post(
        f"{API}/auth/refresh", json={"refresh_token": login.json()["refresh_token"]}
    )
    assert revoked.status_code == 401, revoked.text


# ---------------------------------------------------------- directory & profile
def test_list_is_tenant_scoped(client: TestClient, tenant_a: dict, tenant_b: dict) -> None:
    status, body = _invite(client, tenant_b, email=f"b-{uuid.uuid4().hex[:8]}@example.com")
    assert status == 201, body
    listing = client.get(f"{API}/users", headers=tenant_a["header"], params={"page_size": 100})
    assert listing.status_code == 200, listing.text
    emails = {item["email"] for item in listing.json()["items"]}
    assert body["email"] not in emails  # AC-PF-008-07
    assert all(item["tenant_id"] == tenant_a["id"] for item in listing.json()["items"])


def test_cross_tenant_user_id_is_not_found(client: TestClient, tenant_a: dict, tenant_b: dict) -> None:
    resp = client.get(f"{API}/users/{tenant_b['admin_id']}", headers=tenant_a["header"])
    assert resp.status_code == 404, resp.text  # BR-PF-059


def test_search_export_and_status_filter(client: TestClient, tenant_a: dict) -> None:
    marker = uuid.uuid4().hex[:8]
    email = f"find-{marker}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body

    found = client.get(f"{API}/users/search", headers=tenant_a["header"], params={"q": marker})
    assert found.status_code == 200, found.text
    assert [item["email"] for item in found.json()["items"]] == [email]

    invited = client.get(
        f"{API}/users", headers=tenant_a["header"], params={"status": "INVITED", "page_size": 100}
    )
    assert invited.status_code == 200, invited.text
    assert all(item["account_status"] == "INVITED" for item in invited.json()["items"])

    exported = client.get(f"{API}/users/export", headers=tenant_a["header"])
    assert exported.status_code == 200, exported.text
    assert any(row["email"] == email for row in exported.json())


def test_self_profile_update_does_not_change_role_or_status(
    client: TestClient, tenant_a: dict
) -> None:
    email = f"self-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(
        client, tenant_a, email=email, role_code="SALES_EXECUTIVE", password=USER_PASSWORD
    )
    assert status == 201, body
    login = client.post(
        f"{API}/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": tenant_a["code"]},
    )
    header = {"Authorization": f"Bearer {login.json()['access_token']}"}
    updated = client.put(
        f"{API}/users/me",
        headers=header,
        json={"first_name": "Renamed", "designation": "Sales Rep"},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["first_name"] == "Renamed"
    assert updated.json()["designation"] == "Sales Rep"
    assert updated.json()["role_code"] == "SALES_EXECUTIVE"
    assert updated.json()["account_status"] == "ACTIVE"


# ----------------------------------------------------- update + linkage (PF-005/6/7)
def test_update_user_and_optimistic_locking(client: TestClient, tenant_a: dict) -> None:
    email = f"upd-{uuid.uuid4().hex[:8]}@example.com"
    status, body = _invite(client, tenant_a, email=email)
    assert status == 201, body

    stale = client.put(
        f"{API}/users/{body['user_id']}",
        headers=tenant_a["header"],
        json={"first_name": "Stale", "version_no": body["version_no"] + 5},
    )
    assert stale.status_code == 409, stale.text

    updated = client.put(
        f"{API}/users/{body['user_id']}",
        headers=tenant_a["header"],
        json={
            "first_name": "Renamed",
            "last_name": "Invitee",
            "designation": "Analyst",
            "version_no": body["version_no"],
        },
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["display_name"] == "Renamed Invitee"
    assert updated.json()["version_no"] == body["version_no"] + 1


def test_linkage_accepts_same_tenant_active_branch_and_rejects_foreign(
    client: TestClient, tenant_a: dict, tenant_b: dict
) -> None:
    create_branch = client.post(
        f"{API}/org/branches",
        headers=tenant_a["header"],
        json={
            "code": f"BR{uuid.uuid4().hex[:6].upper()}",
            "name": "Identity Branch",
            "branch_type": "BRANCH",
            "organization_id": _root_org_id(tenant_a["id"]),
            "status": "ACTIVE",
        },
    )
    assert create_branch.status_code == 201, create_branch.text
    branch = create_branch.json()

    ok_status, ok_body = _invite(
        client, tenant_a, email=f"linked-{uuid.uuid4().hex[:8]}@example.com",
        branch_id=branch["id"],
    )
    assert ok_status == 201, ok_body
    assert ok_body["branch_id"] == branch["id"]

    foreign = client.post(
        f"{API}/org/branches",
        headers=tenant_b["header"],
        json={
            "code": f"BX{uuid.uuid4().hex[:6].upper()}",
            "name": "Foreign Branch",
            "branch_type": "BRANCH",
            "organization_id": _root_org_id(tenant_b["id"]),
            "status": "ACTIVE",
        },
    )
    assert foreign.status_code == 201, foreign.text

    bad_status, bad_body = _invite(
        client, tenant_a, email=f"foreign-{uuid.uuid4().hex[:8]}@example.com",
        branch_id=foreign.json()["id"],
    )
    assert bad_status == 422, bad_body  # BR-PF-059


def test_linkage_rejects_inactive_branch(client: TestClient, tenant_a: dict) -> None:
    create_branch = client.post(
        f"{API}/org/branches",
        headers=tenant_a["header"],
        json={
            "code": f"BI{uuid.uuid4().hex[:6].upper()}",
            "name": "Dormant Branch",
            "branch_type": "BRANCH",
            "organization_id": _root_org_id(tenant_a["id"]),
            "status": "ACTIVE",
        },
    )
    assert create_branch.status_code == 201, create_branch.text
    branch_id = create_branch.json()["id"]
    with platform_session() as db:
        from app.models.pf import Branch

        branch = db.get(Branch, uuid.UUID(branch_id))
        branch.status = "INACTIVE"
        db.commit()

    status, body = _invite(
        client, tenant_a, email=f"inactive-{uuid.uuid4().hex[:8]}@example.com",
        branch_id=branch_id,
    )
    assert status == 422, body


def _root_org_id(tenant_id: str) -> str:
    with platform_session() as db:
        org = db.scalars(
            select(Organization).where(
                Organization.tenant_id == uuid.UUID(tenant_id),
                Organization.is_root.is_(True),
            )
        ).first()
        assert org is not None
        return str(org.organization_id)
