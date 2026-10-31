"""BR-CRM-047 / REQ-CRM-028 — all-tenants ``customer.suspend`` synchronization.

Covers ``app.db.seed.sync_crm_finance_only_matrix`` (per tenant) and
``app.db.seed.sync_finance_only_permissions`` (all tenants, dry-run by default), plus
the ``app.jobs.sync_finance_only_permissions`` job wrapper.

Every mutation runs inside ``platform_session()``, which closes WITHOUT committing, and
the temporary tenants are never committed, so nothing is written to the database.
"""

import uuid
from datetime import date

import pytest
from sqlalchemy import delete, func, select

from app.db import seed as seed_module
from app.jobs.sync_finance_only_permissions import run_sync_finance_only_permissions
from app.models.pf import Edition, Permission, Role, RolePermission, Tenant
from tests.conftest import platform_session

SUSPEND = "customer.suspend"
FINANCE = "FINANCE_USER"

# Skip reasons reported by the sync (app.db.seed.SKIP_REASON_*).
FINANCE_MISSING = "finance_role_missing"
SOFT_DELETED = "soft_deleted"
STATUS_PENDING_ACTIVATION = "status_pending_activation"
STATUS_OFFBOARDING = "status_offboarding"
STATUS_CLOSED = "status_closed"

ROLE_SPECS = (
    ("FINANCE_USER", "Finance User"),
    ("TENANT_ADMIN", "Tenant Admin"),
    ("PLATFORM_ADMIN", "Platform Admin"),
    ("SALES_MANAGER", "Sales Manager"),
    ("SALES_EXECUTIVE", "Sales Executive"),
)


# --------------------------------------------------------------------- helpers


def _edition_id(db):
    edition = db.scalars(select(Edition).order_by(Edition.code)).first()
    assert edition is not None, "no edition seeded - cannot create a temporary tenant"
    return edition.id


def _make_tenant(
    db,
    edition_id,
    *,
    status: str = "ACTIVE",
    role_codes: tuple[str, ...] | None = None,
    is_deleted: bool = False,
    activated: bool = True,
) -> Tenant:
    """Create a throw-away tenant in the requested lifecycle state (never committed).

    ``role_codes`` narrows which system roles exist, which is how the "no FINANCE_USER
    role" and other ineligible-tenant cases are built.
    """
    tag = uuid.uuid4().hex[:8]
    tenant = Tenant(
        tenant_code=f"SYN{tag.upper()}"[:32],
        tenant_name=f"Sync {tag}",
        legal_name=f"Sync {tag} Ltd",
        edition_id=edition_id,
        organization_type="Pvt Ltd",
        email=f"sync-{tag}@example.test",
        mobile="+9190" + str(uuid.uuid4().int)[:8],
        status=status,
        activation_date=date.today() if activated else None,
        is_active=True,
        is_deleted=is_deleted,
    )
    db.add(tenant)
    db.flush()
    wanted = ROLE_SPECS if role_codes is None else tuple(
        spec for spec in ROLE_SPECS if spec[0] in role_codes
    )
    for role_code, role_name in wanted:
        db.add(
            Role(
                tenant_id=tenant.tenant_id,
                role_code=role_code,
                role_name=role_name,
                description=f"System role: {role_name}",
                is_system=True,
            )
        )
    db.flush()
    return tenant


def _role_id(db, tenant_id, role_code: str):
    role = db.scalars(
        select(Role).where(
            Role.tenant_id == tenant_id, Role.role_code == role_code
        )
    ).first()
    assert role is not None, f"role {role_code} missing"
    return role.role_id


def _grant(db, tenant_id, role_code: str, permission_code: str = SUSPEND) -> None:
    perm = db.scalars(
        select(Permission).where(Permission.permission_code == permission_code)
    ).first()
    assert perm is not None, f"permission {permission_code} missing"
    role_id = _role_id(db, tenant_id, role_code)
    existing = db.scalars(
        select(RolePermission).where(
            RolePermission.role_id == role_id,
            RolePermission.permission_id == perm.permission_id,
        )
    ).first()
    if existing is None:
        db.add(RolePermission(role_id=role_id, permission_id=perm.permission_id))
        db.flush()


def _holders(db, tenant_id) -> set[str]:
    rows = db.execute(
        select(Role.role_code)
        .join(RolePermission, RolePermission.role_id == Role.role_id)
        .join(Permission, Permission.permission_id == RolePermission.permission_id)
        .where(Role.tenant_id == tenant_id, Permission.permission_code == SUSPEND)
    ).all()
    return {row[0] for row in rows}


def _all_grants(db, tenant_id) -> set[tuple[str, str]]:
    rows = db.execute(
        select(Role.role_code, Permission.permission_code)
        .join(RolePermission, RolePermission.role_id == Role.role_id)
        .join(Permission, Permission.permission_id == RolePermission.permission_id)
        .where(Role.tenant_id == tenant_id)
    ).all()
    return {(row[0], row[1]) for row in rows}


# ------------------------------------------------------ per-tenant correction


def test_sync_grants_finance_and_revokes_legacy_grants():
    """Legacy admin/sales grants are removed and the missing Finance grant is added."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _grant(db, tenant.tenant_id, "PLATFORM_ADMIN")
        _grant(db, tenant.tenant_id, "SALES_MANAGER")
        assert _holders(db, tenant.tenant_id) == {
            "TENANT_ADMIN",
            "PLATFORM_ADMIN",
            "SALES_MANAGER",
        }
        assert FINANCE not in _holders(db, tenant.tenant_id)

        summary = seed_module.sync_crm_finance_only_matrix(db, tenant.tenant_id)

        assert summary["granted"] == 1, summary
        assert summary["revoked"] >= 3, summary
        assert summary["finance_holds"] is True
        assert summary["extra_holders"] == []
        assert summary["ok"] is True
        assert _holders(db, tenant.tenant_id) == {FINANCE}


def test_sync_is_idempotent():
    """A second run must change nothing and still report the correct post-condition."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")

        first = seed_module.sync_crm_finance_only_matrix(db, tenant.tenant_id)
        second = seed_module.sync_crm_finance_only_matrix(db, tenant.tenant_id)

        assert first["ok"] is True
        assert second["ok"] is True
        assert second["granted"] == 0, second
        assert second["revoked"] == 0, second
        assert second["permission_created"] is False
        assert _holders(db, tenant.tenant_id) == {FINANCE}


def test_sync_preserves_every_unrelated_grant():
    """Only customer.suspend rows may change."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        for role_code in ("TENANT_ADMIN", "SALES_MANAGER", "SALES_EXECUTIVE"):
            _grant(db, tenant.tenant_id, role_code)
        # An unrelated grain must survive untouched.
        _grant(db, tenant.tenant_id, "TENANT_ADMIN", "customer.update")
        _grant(db, tenant.tenant_id, "SALES_MANAGER", "customer.read")

        before = _all_grants(db, tenant.tenant_id)
        seed_module.sync_crm_finance_only_matrix(db, tenant.tenant_id)
        after = _all_grants(db, tenant.tenant_id)

        removed = before - after
        assert removed == {
            ("TENANT_ADMIN", SUSPEND),
            ("SALES_MANAGER", SUSPEND),
            ("SALES_EXECUTIVE", SUSPEND),
        }, removed
        # Nothing unrelated disappeared, and the unrelated grains are still there.
        assert ("TENANT_ADMIN", "customer.update") in after
        assert ("SALES_MANAGER", "customer.read") in after


# ------------------------------------------------------------- all tenants


def test_all_tenants_sync_corrects_every_tenant():
    """Two tenants with different legacy faults are both corrected in one run."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        first = _make_tenant(db, edition_id)
        second = _make_tenant(db, edition_id)
        _grant(db, first.tenant_id, "TENANT_ADMIN")          # legacy over-grant
        _grant(db, second.tenant_id, "SALES_MANAGER")        # legacy over-grant
        # Neither tenant's Finance role holds it yet: the "missing Finance grant" case.
        assert _holders(db, first.tenant_id) == {"TENANT_ADMIN"}
        assert _holders(db, second.tenant_id) == {"SALES_MANAGER"}

        summary = seed_module.sync_finance_only_permissions(
            db,
            tenant_codes=(first.tenant_code, second.tenant_code),
            apply=True,
        )

        assert summary["apply"] is True
        assert summary["tenants_scanned"] == 2
        assert summary["tenants_changed"] == 2
        assert all(r["ok"] for r in summary["results"]), summary["results"]
        assert _holders(db, first.tenant_id) == {FINANCE}
        assert _holders(db, second.tenant_id) == {FINANCE}


def test_all_tenants_sync_is_idempotent():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")

        first = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=True
        )
        second = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=True
        )

        assert first["tenants_changed"] == 1
        assert second["tenants_changed"] == 0, second["results"]
        assert _holders(db, tenant.tenant_id) == {FINANCE}


def test_dry_run_writes_nothing():
    """The default mode must be a pure read: it reports the change but makes none."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        before = _holders(db, tenant.tenant_id)

        summary = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=False
        )

        assert summary["apply"] is False
        assert summary["tenants_changed"] == 1
        flagged = [r for r in summary["results"] if r["tenant_code"] == tenant.tenant_code][0]
        assert flagged["needs_change"] is True
        assert flagged["ok"] is False
        assert flagged["extra_holders"] == ["TENANT_ADMIN"]
        assert _holders(db, tenant.tenant_id) == before  # untouched


def test_job_wrapper_dry_run_is_read_only():
    """The job wrapper's default (no --apply) scans without writing."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        before = _holders(db, tenant.tenant_id)

        result = run_sync_finance_only_permissions(
            apply=False, tenant_codes=(tenant.tenant_code,), db=db
        )

        assert result.apply is False
        assert result.tenants_scanned == 1
        assert result.tenants_changed == 1
        assert _holders(db, tenant.tenant_id) == before


def test_job_wrapper_apply_corrects_tenant():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "PLATFORM_ADMIN")

        result = run_sync_finance_only_permissions(
            apply=True, tenant_codes=(tenant.tenant_code,), db=db
        )

        assert result.apply is True
        assert result.tenants_changed == 1
        assert _holders(db, tenant.tenant_id) == {FINANCE}


# ------------------------------------- integration with the existing mechanism


def test_sync_pf_module_matrices_applies_the_finance_only_correction():
    """Every tenant touched by the existing matrix sync also gets BR-CRM-047 enforced."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id)
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        assert "TENANT_ADMIN" in _holders(db, tenant.tenant_id)

        seed_module._sync_pf_module_matrices(db, tenant.tenant_id)

        holders = _holders(db, tenant.tenant_id)
        assert "TENANT_ADMIN" not in holders
        assert FINANCE in holders, holders
        assert holders == {FINANCE}, holders


# ------------------------------------------------ eligibility: keeper role absent


def test_matrix_skips_tenant_without_finance_role():
    """No FINANCE_USER role: nothing granted, and crucially nothing revoked."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(
            db, edition_id, role_codes=("TENANT_ADMIN", "PLATFORM_ADMIN")
        )
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _grant(db, tenant.tenant_id, "PLATFORM_ADMIN")
        before = _all_grants(db, tenant.tenant_id)
        assert before == {
            ("TENANT_ADMIN", SUSPEND),
            ("PLATFORM_ADMIN", SUSPEND),
        }

        summary = seed_module.sync_crm_finance_only_matrix(db, tenant.tenant_id)

        assert summary["skipped"] is True
        assert summary["ok"] is False
        assert summary["skip_reason"] == FINANCE_MISSING
        assert summary["finance_role_present"] is False
        assert summary["granted"] == 0
        assert summary["revoked"] == 0
        assert summary["permission_created"] is False
        assert summary["finance_holds"] is False
        # The legacy grants survive untouched - this is the whole point of the guard.
        assert _all_grants(db, tenant.tenant_id) == before
        assert _holders(db, tenant.tenant_id) == {"TENANT_ADMIN", "PLATFORM_ADMIN"}


def test_matrix_skip_does_not_create_the_catalogue_row():
    """The catalogue row is not created for a tenant that could never hold it."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        roleless = _make_tenant(db, edition_id, role_codes=("TENANT_ADMIN",))
        _grant(db, roleless.tenant_id, "TENANT_ADMIN")

        perm = db.scalars(
            select(Permission).where(Permission.permission_code == SUSPEND)
        ).first()
        assert perm is not None, "customer.suspend must be seeded globally"
        # Simulate a catalogue that predates the grain, inside this transaction only.
        db.execute(
            delete(RolePermission).where(
                RolePermission.permission_id == perm.permission_id
            )
        )
        db.delete(perm)
        db.flush()
        assert (
            db.scalars(
                select(Permission).where(Permission.permission_code == SUSPEND)
            ).first()
            is None
        )

        skipped = seed_module.sync_crm_finance_only_matrix(db, roleless.tenant_id)

        assert skipped["skipped"] is True
        assert skipped["skip_reason"] == FINANCE_MISSING
        assert skipped["permission_created"] is False
        assert (
            db.scalars(
                select(Permission).where(Permission.permission_code == SUSPEND)
            ).first()
            is None
        ), "no catalogue row may be created for a tenant without FINANCE_USER"

        # Control: an eligible tenant DOES create the row - the guard is the only reason.
        eligible = _make_tenant(db, edition_id)
        control = seed_module.sync_crm_finance_only_matrix(db, eligible.tenant_id)
        assert control["skipped"] is False
        assert control["permission_created"] is True
        assert control["ok"] is True


# -------------------------------------------------- eligibility: lifecycle state


def test_roleless_pending_activation_tenant_is_skipped():
    """A PENDING_ACTIVATION tenant that cannot hold the grain is left alone."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(
            db, edition_id, status="PENDING_ACTIVATION", role_codes=("TENANT_ADMIN",)
        )
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        before = _all_grants(db, tenant.tenant_id)

        summary = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=True
        )

        assert summary["tenants_scanned"] == 1
        assert summary["tenants_eligible"] == 0
        assert summary["tenants_skipped"] == 1
        assert summary["tenants_changed"] == 0
        assert summary["skip_reasons"] == {STATUS_PENDING_ACTIVATION: 1}
        assert summary["results"][0]["skipped"] is True
        assert summary["results"][0]["needs_change"] is False
        assert _all_grants(db, tenant.tenant_id) == before


def test_roleless_offboarding_tenant_is_skipped():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(
            db, edition_id, status="OFFBOARDING", role_codes=("TENANT_ADMIN",)
        )
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        before = _all_grants(db, tenant.tenant_id)

        summary = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=True
        )

        assert summary["tenants_eligible"] == 0
        assert summary["tenants_skipped"] == 1
        assert summary["tenants_changed"] == 0
        assert summary["skip_reasons"] == {STATUS_OFFBOARDING: 1}
        assert _all_grants(db, tenant.tenant_id) == before


def test_closed_and_soft_deleted_tenants_are_skipped():
    """CLOSED lifecycle state and soft-deleted rows are both skipped, even with a
    FINANCE_USER role present, and neither is mutated."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        closed = _make_tenant(db, edition_id, status="CLOSED")
        deleted = _make_tenant(db, edition_id, is_deleted=True)
        for tenant in (closed, deleted):
            _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        before_closed = _all_grants(db, closed.tenant_id)
        before_deleted = _all_grants(db, deleted.tenant_id)

        summary = seed_module.sync_finance_only_permissions(
            db,
            tenant_codes=(closed.tenant_code, deleted.tenant_code),
            apply=True,
        )

        assert summary["tenants_scanned"] == 2
        assert summary["tenants_eligible"] == 0
        assert summary["tenants_skipped"] == 2
        assert summary["tenants_changed"] == 0
        assert summary["skip_reasons"] == {STATUS_CLOSED: 1, SOFT_DELETED: 1}
        assert _all_grants(db, closed.tenant_id) == before_closed
        assert _all_grants(db, deleted.tenant_id) == before_deleted


def test_active_tenant_with_finance_user_is_corrected():
    """The eligible case still does the real work."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _make_tenant(db, edition_id, status="ACTIVE")
        _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        _grant(db, tenant.tenant_id, "SALES_MANAGER")
        assert _holders(db, tenant.tenant_id) == {"TENANT_ADMIN", "SALES_MANAGER"}

        summary = seed_module.sync_finance_only_permissions(
            db, tenant_codes=(tenant.tenant_code,), apply=True
        )

        assert summary["tenants_eligible"] == 1
        assert summary["tenants_skipped"] == 0
        assert summary["skip_reasons"] == {}
        assert summary["tenants_changed"] == 1
        assert summary["results"][0]["ok"] is True
        assert summary["results"][0]["revoked"] == 2
        assert _holders(db, tenant.tenant_id) == {FINANCE}


def test_dry_run_and_apply_agree_on_eligibility():
    """Both modes select exactly the same tenants and agree on who needs a change."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        eligible = _make_tenant(db, edition_id)
        pending = _make_tenant(
            db, edition_id, status="PENDING_ACTIVATION", role_codes=("TENANT_ADMIN",)
        )
        deleted = _make_tenant(db, edition_id, is_deleted=True)
        offboarding = _make_tenant(
            db, edition_id, status="OFFBOARDING", role_codes=("TENANT_ADMIN",)
        )
        unprovisioned = _make_tenant(db, edition_id, activated=False)
        for tenant in (eligible, pending, deleted, offboarding, unprovisioned):
            _grant(db, tenant.tenant_id, "TENANT_ADMIN")
        codes = tuple(
            tenant.tenant_code
            for tenant in (eligible, pending, deleted, offboarding, unprovisioned)
        )

        dry = seed_module.sync_finance_only_permissions(
            db, tenant_codes=codes, apply=False
        )
        applied = seed_module.sync_finance_only_permissions(
            db, tenant_codes=codes, apply=True
        )

        for key in (
            "tenants_scanned",
            "tenants_eligible",
            "tenants_changed",
            "tenants_skipped",
            "skip_reasons",
        ):
            assert dry[key] == applied[key], (key, dry[key], applied[key])

        assert applied["tenants_scanned"] == 5
        assert applied["tenants_eligible"] == 1
        assert applied["tenants_skipped"] == 4
        assert applied["tenants_changed"] == 1
        assert applied["skip_reasons"] == {
            STATUS_PENDING_ACTIVATION: 1,
            SOFT_DELETED: 1,
            STATUS_OFFBOARDING: 1,
            "not_provisioned": 1,
        }

        def _selection(summary, predicate):
            return {r["tenant_code"] for r in summary["results"] if predicate(r)}

        assert _selection(dry, lambda r: r["skipped"]) == _selection(
            applied, lambda r: r["skipped"]
        ) == {
            pending.tenant_code,
            deleted.tenant_code,
            offboarding.tenant_code,
            unprovisioned.tenant_code,
        }
        assert _selection(dry, lambda r: r["needs_change"]) == _selection(
            applied, lambda r: r["needs_change"]
        ) == {eligible.tenant_code}


def test_skipped_tenants_change_nothing_and_unrelated_grants_survive():
    """End to end: only customer.suspend rows of eligible tenants move."""
    with platform_session() as db:
        edition_id = _edition_id(db)
        eligible = _make_tenant(db, edition_id)
        skipped = _make_tenant(
            db, edition_id, status="PENDING_ACTIVATION", role_codes=("TENANT_ADMIN",)
        )
        _grant(db, eligible.tenant_id, "TENANT_ADMIN")
        _grant(db, eligible.tenant_id, "TENANT_ADMIN", "customer.update")
        _grant(db, eligible.tenant_id, "SALES_MANAGER", "customer.read")
        _grant(db, skipped.tenant_id, "TENANT_ADMIN")

        eligible_before = _all_grants(db, eligible.tenant_id)
        skipped_before = _all_grants(db, skipped.tenant_id)
        permission_count_before = db.scalar(select(func.count()).select_from(Permission))

        seed_module.sync_finance_only_permissions(
            db,
            tenant_codes=(eligible.tenant_code, skipped.tenant_code),
            apply=True,
        )

        eligible_after = _all_grants(db, eligible.tenant_id)
        assert eligible_before - eligible_after == {("TENANT_ADMIN", SUSPEND)}
        assert eligible_after - eligible_before == {(FINANCE, SUSPEND)}
        assert ("TENANT_ADMIN", "customer.update") in eligible_after
        assert ("SALES_MANAGER", "customer.read") in eligible_after

        assert _all_grants(db, skipped.tenant_id) == skipped_before
        # No catalogue churn anywhere.
        assert (
            db.scalar(select(func.count()).select_from(Permission))
            == permission_count_before
        )
