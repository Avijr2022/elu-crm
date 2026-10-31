"""REQ-CRM-028 / BR-CRM-047 — ``customer.suspend`` must be GRANT-level Finance-only.

Proves that:
  * the new-tenant provisioning path grants it to FINANCE_USER only;
  * re-seeding an existing tenant heals erroneous TENANT_ADMIN / PLATFORM_ADMIN grants;
  * Sales roles never receive it;
  * the revoke is scoped to one permission and one tenant, preserving every other grant;
  * Finance suspension still works end to end with the runtime role gate intact.

All direct database work runs inside ``platform_session()``, which closes WITHOUT
committing, so every mutation here rolls back and nothing is persisted.
"""

import uuid
from datetime import date
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db import seed as seed_module
from app.main import app
from app.models.pf import Edition, Permission, Role, RolePermission, Tenant, User
from tests.conftest import platform_admin_select, platform_session

USER_PASSWORD = "Req028Grant!234"
PLATFORM_TENANT_CODE = "EIIP001"
SUSPEND_PERMISSION = "customer.suspend"
FINANCE_ROLE = "FINANCE_USER"
NON_FINANCE_ROLES = (
    "TENANT_ADMIN",
    "PLATFORM_ADMIN",
    "SALES_EXECUTIVE",
    "SALES_MANAGER",
)


# --------------------------------------------------------------------- helpers


def _tenant(db, tenant_code: str) -> Tenant | None:
    return db.scalars(select(Tenant).where(Tenant.tenant_code == tenant_code)).first()


def _role(db, tenant_id, role_code: str) -> Role | None:
    return db.scalars(
        select(Role).where(Role.tenant_id == tenant_id, Role.role_code == role_code)
    ).first()


def _suspend_permission(db) -> Permission | None:
    return db.scalars(
        select(Permission).where(Permission.permission_code == SUSPEND_PERMISSION)
    ).first()


def _hold_suspend(db, tenant_id) -> set[str]:
    """Return the set of role codes in ``tenant_id`` that hold customer.suspend."""
    rows = db.execute(
        select(Role.role_code)
        .join(RolePermission, RolePermission.role_id == Role.role_id)
        .join(Permission, Permission.permission_id == RolePermission.permission_id)
        .where(
            Role.tenant_id == tenant_id,
            Permission.permission_code == SUSPEND_PERMISSION,
        )
    ).all()
    return {row[0] for row in rows}


def _all_grants(db, tenant_id) -> set[tuple[str, str]]:
    """Return every (role_code, permission_code) pair held in ``tenant_id``."""
    rows = db.execute(
        select(Role.role_code, Permission.permission_code)
        .join(RolePermission, RolePermission.role_id == Role.role_id)
        .join(Permission, Permission.permission_id == RolePermission.permission_id)
        .where(Role.tenant_id == tenant_id)
    ).all()
    return {(row[0], row[1]) for row in rows}


def _force_grant(db, tenant_id, role_code: str, permission_code: str = SUSPEND_PERMISSION) -> None:
    """Create the RolePermission row if missing (simulates an erroneous legacy grant)."""
    role = _role(db, tenant_id, role_code)
    perm = db.scalars(
        select(Permission).where(Permission.permission_code == permission_code)
    ).first()
    assert role is not None, f"role {role_code} missing"
    assert perm is not None, f"permission {permission_code} missing"
    exists = db.scalars(
        select(RolePermission).where(
            RolePermission.role_id == role.role_id,
            RolePermission.permission_id == perm.permission_id,
        )
    ).first()
    if exists is None:
        db.add(
            RolePermission(role_id=role.role_id, permission_id=perm.permission_id)
        )
        db.flush()


# ------------------------------------------------- catalogue / helper contract


def test_customer_suspend_is_registered_as_finance_only():
    codes = {code for code, _, _ in seed_module.PERMISSIONS}
    assert SUSPEND_PERMISSION in codes
    assert SUSPEND_PERMISSION in seed_module.FINANCE_ONLY_PERMISSIONS
    # The exclusion helper must actually drop it and leave everything else intact.
    sample = ("customer.read", SUSPEND_PERMISSION, "customer.update")
    assert seed_module._exclude_finance_only(sample) == (
        "customer.read",
        "customer.update",
    )


# --------------------------------------------------- (a) new-tenant provisioning


def test_provision_tenant_roles_grants_suspend_to_finance_only():
    """New-tenant path: FINANCE_USER only; admins and sales roles get nothing."""
    with platform_session() as db:
        tenant = _tenant(db, PLATFORM_TENANT_CODE)
        assert tenant is not None, "seed tenant missing"

        # Simulate a brand-new tenant: no pre-existing customer.suspend grants.
        seed_module._revoke_permission_from_other_roles(
            db, tenant.tenant_id, SUSPEND_PERMISSION, ()
        )
        assert _hold_suspend(db, tenant.tenant_id) == set()

        seed_module.provision_tenant_roles(db, tenant.tenant_id)

        holders = _hold_suspend(db, tenant.tenant_id)
        assert FINANCE_ROLE in holders, holders
        for role_code in NON_FINANCE_ROLES:
            assert role_code not in holders, f"{role_code} must not hold {SUSPEND_PERMISSION}"

        # Administrators still hold the rest of the catalogue (requirement 4).
        admin_grants = _all_grants(db, tenant.tenant_id)
        assert ("TENANT_ADMIN", "customer.read") in admin_grants
        assert ("TENANT_ADMIN", "customer.update") in admin_grants
        assert ("PLATFORM_ADMIN", "customer.read") in admin_grants
        # No commit: platform_session closes without committing -> rolled back.


# ------------------------------------------- (b) healing an existing tenant


def test_upgrade_crm_permissions_revokes_erroneous_admin_grants():
    """Re-seed must remove legacy TENANT_ADMIN / PLATFORM_ADMIN grants."""
    with platform_session() as db:
        tenant = _tenant(db, PLATFORM_TENANT_CODE)
        assert tenant is not None

        # Inject the erroneous legacy state.
        _force_grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _force_grant(db, tenant.tenant_id, "PLATFORM_ADMIN")
        before = _hold_suspend(db, tenant.tenant_id)
        assert {"TENANT_ADMIN", "PLATFORM_ADMIN"} <= before, before

        removed = seed_module._revoke_permission_from_other_roles(
            db, tenant.tenant_id, SUSPEND_PERMISSION, (FINANCE_ROLE,)
        )
        assert removed >= 2, removed

        # The real re-seed entry point must produce the same outcome.
        seed_module._upgrade_crm_permissions(db, tenant)

        after = _hold_suspend(db, tenant.tenant_id)
        assert "TENANT_ADMIN" not in after
        assert "PLATFORM_ADMIN" not in after
        assert FINANCE_ROLE in after
        for role_code in ("SALES_EXECUTIVE", "SALES_MANAGER"):
            assert role_code not in after


def test_upgrade_crm_permissions_preserves_all_other_grants():
    """Requirement 4: the revoke must not disturb any unrelated grant."""
    with platform_session() as db:
        tenant = _tenant(db, PLATFORM_TENANT_CODE)
        assert tenant is not None
        _force_grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _force_grant(db, tenant.tenant_id, "PLATFORM_ADMIN")

        before = _all_grants(db, tenant.tenant_id)
        seed_module._upgrade_crm_permissions(db, tenant)
        after = _all_grants(db, tenant.tenant_id)

        # Nothing may disappear except customer.suspend held by a non-Finance role.
        removed = before - after
        unexpected = {
            grant
            for grant in removed
            if not (grant[1] == SUSPEND_PERMISSION and grant[0] != FINANCE_ROLE)
        }
        assert unexpected == set(), f"unrelated grants were removed: {unexpected}"
        # And the rest of the admin/SALES matrix is still present.
        assert ("TENANT_ADMIN", "customer.create") in after
        assert ("PLATFORM_ADMIN", "customer.update") in after
        assert ("SALES_MANAGER", "customer.update") in after


def test_revoke_is_scoped_to_a_single_tenant():
    """Requirement 3: the deletion must not touch another tenant's grants."""
    with platform_session() as db:
        platform_tenant = _tenant(db, PLATFORM_TENANT_CODE)
        other_tenant = _tenant(db, "COMU001")
        assert platform_tenant is not None
        if other_tenant is None:
            pytest.skip("COMU001 tenant not present in this database")

        # Hermetic prerequisite: COMU001 is seeded with only a SALES_EXECUTIVE role
        # (``seed._ensure_community_demo_tenant``), so a fresh database has no
        # TENANT_ADMIN to grant. Provision the system roles inside this rolled-back
        # transaction instead of relying on state left by earlier modules or by a
        # long-lived development database.
        seed_module.provision_tenant_roles(db, other_tenant.tenant_id)
        _force_grant(db, other_tenant.tenant_id, "TENANT_ADMIN")
        assert "TENANT_ADMIN" in _hold_suspend(db, other_tenant.tenant_id)

        # Heal the PLATFORM tenant only.
        seed_module._upgrade_crm_permissions(db, platform_tenant)

        assert "TENANT_ADMIN" not in _hold_suspend(db, platform_tenant.tenant_id)
        # The foreign tenant is untouched.
        assert "TENANT_ADMIN" in _hold_suspend(db, other_tenant.tenant_id)


# --------------------------------------------------------- (c) sales roles


def test_sales_roles_never_receive_customer_suspend():
    """Sales Executive / Sales Manager grants must not contain customer.suspend."""
    assert SUSPEND_PERMISSION not in seed_module.CRM_SALES_EXEC_PERMS
    assert SUSPEND_PERMISSION not in seed_module.CRM_SALES_MANAGER_PERMS
    assert SUSPEND_PERMISSION not in seed_module.CRM_COMMUNITY_PERMS

    with platform_session() as db:
        tenant = _tenant(db, PLATFORM_TENANT_CODE)
        assert tenant is not None
        seed_module.provision_tenant_roles(db, tenant.tenant_id)
        seed_module._upgrade_crm_permissions(db, tenant)
        holders = _hold_suspend(db, tenant.tenant_id)
        assert "SALES_EXECUTIVE" not in holders
        assert "SALES_MANAGER" not in holders


# ------------------------------------------------- (d) Finance still works


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def finance_token(client: TestClient) -> str:
    email = f"req028-grant-fin-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None
        role = _role(db, admin.tenant_id, FINANCE_ROLE)
        assert role is not None
        db.add(
            User(
                tenant_id=admin.tenant_id,
                organization_id=admin.organization_id,
                role_id=role.role_id,
                employee_code=f"G28{uuid.uuid4().hex[:6].upper()}",
                first_name="REQ028",
                last_name="Finance",
                display_name="REQ028 Finance",
                email=email,
                password_hash=hash_password(USER_PASSWORD),
                account_status="ACTIVE",
            )
        )
        db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": USER_PASSWORD, "tenant_code": PLATFORM_TENANT_CODE},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


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
            "tenant_code": PLATFORM_TENANT_CODE,
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.db_write  # C4: commits users + customers, so disposable DB only
def test_finance_suspension_still_works_end_to_end(
    client: TestClient, admin_token: str, finance_token: str
):
    """Requirement 5: the runtime role gate is intact and Finance can still suspend."""
    admin_headers = _auth(admin_token)
    create = client.post(
        "/api/v1/crm/customers",
        headers=admin_headers,
        json={"legal_name": f"Grant Cust {uuid.uuid4().hex[:8]}"},
    )
    assert create.status_code == 201, create.text
    cid = create.json()["customer_id"]
    client.post(
        f"/api/v1/crm/customers/{cid}/contacts",
        headers=admin_headers,
        json={"first_name": "Primary", "is_primary": True},
    )
    client.post(
        f"/api/v1/crm/customers/{cid}/addresses",
        headers=admin_headers,
        json={"address_type": "REGISTERED", "address_line1": "1 Grant Road"},
    )
    activate = client.patch(
        f"/api/v1/crm/customers/{cid}", headers=admin_headers, json={"status": "ACTIVE"}
    )
    assert activate.status_code == 200, activate.text

    suspend = client.post(
        f"/api/v1/crm/customers/{cid}/suspend",
        headers=_auth(finance_token),
        json={"reason_code": "CREDIT_RISK", "comment": "grant-level verification"},
    )
    assert suspend.status_code == 200, suspend.text
    assert suspend.json()["status"] == "SUSPENDED"

    # The admin still cannot suspend (runtime gate), proving defence in depth.
    create2 = client.post(
        "/api/v1/crm/customers",
        headers=admin_headers,
        json={"legal_name": f"Grant Cust2 {uuid.uuid4().hex[:8]}"},
    )
    cid2 = create2.json()["customer_id"]
    denied = client.post(
        f"/api/v1/crm/customers/{cid2}/suspend",
        headers=admin_headers,
        json={"reason_code": "CREDIT_RISK", "comment": "admin attempt"},
    )
    assert denied.status_code == 403, denied.text


# ------------------------------------------- (e) M4 fail-closed keeper resolution


def _make_bare_tenant(db, *, role_codes: tuple[str, ...]) -> Tenant:
    """Throw-away tenant holding only ``role_codes`` (never committed).

    Used to build the "named keeper role is absent" state that triggers the M4 guard.
    """
    tag = uuid.uuid4().hex[:8]
    edition = db.scalars(select(Edition).order_by(Edition.code)).first()
    assert edition is not None, "no edition seeded - cannot create a temporary tenant"
    tenant = Tenant(
        tenant_code=f"M4{tag.upper()}"[:32],
        tenant_name=f"M4 {tag}",
        legal_name=f"M4 {tag} Ltd",
        edition_id=edition.id,
        organization_type="Pvt Ltd",
        email=f"m4-{tag}@example.test",
        mobile="+9190" + str(uuid.uuid4().int)[:8],
        status="ACTIVE",
        activation_date=date.today(),
        is_active=True,
        is_deleted=False,
    )
    db.add(tenant)
    db.flush()
    for role_code in role_codes:
        db.add(
            Role(
                tenant_id=tenant.tenant_id,
                role_code=role_code,
                role_name=role_code.replace("_", " ").title(),
                description=f"System role: {role_code}",
                is_system=True,
            )
        )
    db.flush()
    return tenant


def test_revoke_fails_closed_when_keeper_roles_are_missing():
    """M4: a non-empty keep-list that resolves to nothing must revoke NOTHING."""
    with platform_session() as db:
        tenant = _make_bare_tenant(db, role_codes=("TENANT_ADMIN", "SALES_MANAGER"))
        _force_grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _force_grant(db, tenant.tenant_id, "SALES_MANAGER")
        before = _all_grants(db, tenant.tenant_id)
        assert _hold_suspend(db, tenant.tenant_id) == {
            "TENANT_ADMIN",
            "SALES_MANAGER",
        }

        removed = seed_module._revoke_permission_from_other_roles(
            db, tenant.tenant_id, SUSPEND_PERMISSION, (FINANCE_ROLE,)
        )

        assert removed == 0, removed
        assert _all_grants(db, tenant.tenant_id) == before
        assert _hold_suspend(db, tenant.tenant_id) == {
            "TENANT_ADMIN",
            "SALES_MANAGER",
        }


def test_revoke_with_valid_keeper_still_removes_only_other_roles():
    """M4 must not weaken the intended revoke when the keeper role does exist."""
    with platform_session() as db:
        tenant = _make_bare_tenant(
            db, role_codes=(FINANCE_ROLE, "TENANT_ADMIN", "SALES_MANAGER")
        )
        for role_code in (FINANCE_ROLE, "TENANT_ADMIN", "SALES_MANAGER"):
            _force_grant(db, tenant.tenant_id, role_code)

        removed = seed_module._revoke_permission_from_other_roles(
            db, tenant.tenant_id, SUSPEND_PERMISSION, (FINANCE_ROLE,)
        )

        assert removed == 2, removed
        assert _hold_suspend(db, tenant.tenant_id) == {FINANCE_ROLE}


def test_revoke_with_empty_keep_list_preserves_previous_behaviour():
    """An empty keep-list still means "revoke from every role" (unchanged)."""
    with platform_session() as db:
        tenant = _make_bare_tenant(db, role_codes=("TENANT_ADMIN", "SALES_MANAGER"))
        _force_grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _force_grant(db, tenant.tenant_id, "SALES_MANAGER")

        removed = seed_module._revoke_permission_from_other_roles(
            db, tenant.tenant_id, SUSPEND_PERMISSION, ()
        )

        assert removed == 2, removed
        assert _hold_suspend(db, tenant.tenant_id) == set()


def test_revoke_fail_closed_is_still_tenant_scoped():
    """A fail-closed call touches no tenant, and a successful call touches no other."""
    with platform_session() as db:
        broken = _make_bare_tenant(db, role_codes=("TENANT_ADMIN",))       # no keeper
        healthy = _make_bare_tenant(db, role_codes=(FINANCE_ROLE, "TENANT_ADMIN"))
        for tenant in (broken, healthy):
            _force_grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _force_grant(db, healthy.tenant_id, FINANCE_ROLE)
        broken_before = _all_grants(db, broken.tenant_id)

        assert (
            seed_module._revoke_permission_from_other_roles(
                db, broken.tenant_id, SUSPEND_PERMISSION, (FINANCE_ROLE,)
            )
            == 0
        )
        assert (
            seed_module._revoke_permission_from_other_roles(
                db, healthy.tenant_id, SUSPEND_PERMISSION, (FINANCE_ROLE,)
            )
            == 1
        )

        # The fail-closed tenant is byte-identical; the eligible one only lost the
        # non-keeper grant.
        assert _all_grants(db, broken.tenant_id) == broken_before
        assert _hold_suspend(db, broken.tenant_id) == {"TENANT_ADMIN"}
        assert _hold_suspend(db, healthy.tenant_id) == {FINANCE_ROLE}
