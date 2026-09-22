"""PF-009 Roles & Permissions (RBAC) — Batch 1 foundation tests.

Scope: the Batch 1 foundation only — core.user_role, BR-PF-061 custom-role
edition limits, BR-PF-062 system-role immutability, RBAC tenant-isolation/RLS
enrolment and the PF-009 permission catalogue. The /api/v1/rbac API surface,
multi-role JWT resolution and permission-grain rollout are later batches and are
deliberately NOT tested here.
"""

from contextlib import contextmanager
from collections.abc import Iterator

import pytest
from sqlalchemy import func, select, text

from app.core.exceptions import ValidationAppError
from app.db.migrate_pf003a import rls_enabled
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal
from app.models.pf import Edition, Permission, Role, Tenant
from app.services.pf import rbac_service

PF009_PERMISSION_CODES = (
    "role.create",
    "role.read",
    "role.update",
    "role.delete",
    "role.export",
    "role.configure",
    "role.assign",
    "permission.read",
)

CUSTOM_ROLE_CODE = "PF009_TEST_CUSTOM"


@contextmanager
def platform_session():
    """Platform-context session (mirrors tests/conftest.py)."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        yield db
    finally:
        clear_rls_context(db)
        db.close()


def _edition(db, code: str) -> Edition:
    edition = db.scalars(select(Edition).where(Edition.code == code)).first()
    assert edition is not None, f"seeded edition {code} not found"
    return edition


def _any_tenant_id(db):
    return db.execute(text("select tenant_id from core.tenant limit 1")).scalar()


def _purge_custom_role(db, tenant_id) -> None:
    db.execute(
        text(
            "delete from core.role where tenant_id = :t and role_code = :c"
        ),
        {"t": tenant_id, "c": CUSTOM_ROLE_CODE},
    )
    db.commit()


# ---------------------------------------------------------------------------
# BR-PF-061 — custom-role edition limits
# ---------------------------------------------------------------------------
def test_custom_role_limit_matches_bfs_edition_matrix():
    """Community=5, Professional=25, Enterprise=unlimited (BR-PF-061)."""
    with platform_session() as db:
        assert rbac_service.custom_role_limit(_edition(db, "COMMUNITY")) == 5
        assert rbac_service.custom_role_limit(_edition(db, "PROFESSIONAL")) == 25
        # 999999 is the repo-wide unlimited sentinel -> surfaced as None.
        assert rbac_service.custom_role_limit(_edition(db, "ENTERPRISE")) is None


def test_custom_role_limit_none_when_limit_code_absent():
    """An edition without MAX_ROLES enforces no custom-role bound."""
    with platform_session() as db:
        edition = _edition(db, "COMMUNITY")
        edition.limits = [lim for lim in edition.limits if lim.limit_code != "MAX_ROLES"]
        assert rbac_service.custom_role_limit(edition) is None


def test_count_custom_roles_excludes_system_and_deleted():
    """Only live custom roles count toward BR-PF-061."""
    with platform_session() as db:
        tenant_id = _any_tenant_id(db)
        assert tenant_id is not None
        _purge_custom_role(db, tenant_id)
        try:
            assert rbac_service.count_custom_roles(db, tenant_id) == 0

            db.add(
                Role(
                    tenant_id=tenant_id,
                    role_code=CUSTOM_ROLE_CODE,
                    role_name="PF-009 Test Custom",
                    is_system=False,
                )
            )
            db.commit()
            assert rbac_service.count_custom_roles(db, tenant_id) == 1

            # Soft-deleted custom roles must not count.
            role = db.scalars(
                select(Role).where(
                    Role.tenant_id == tenant_id, Role.role_code == CUSTOM_ROLE_CODE
                )
            ).one()
            role.is_deleted = True
            db.commit()
            assert rbac_service.count_custom_roles(db, tenant_id) == 0
        finally:
            _purge_custom_role(db, tenant_id)

    # System roles are never counted: TENANT_ADMIN etc. exist for the tenant yet
    # the count above was 0 before any custom role was added.
    with platform_session() as db:
        tenant_id = _any_tenant_id(db)
        system_roles = db.scalar(
            select(func.count())
            .select_from(Role)
            .where(Role.tenant_id == tenant_id, Role.is_system.is_(True))
        )
        assert system_roles and system_roles > 0


def test_assert_can_add_custom_role_rejects_the_sixth_on_community():
    """AC-PF-009-02 / BR-PF-061: 6th custom role on Community is rejected."""
    with platform_session() as db:
        tenant_id = _any_tenant_id(db)
        assert tenant_id is not None
        _purge_custom_role(db, tenant_id)
        community = _edition(db, "COMMUNITY")
        try:
            for i in range(5):
                db.add(
                    Role(
                        tenant_id=tenant_id,
                        role_code=f"PF009_TEST_C{i}",
                        role_name=f"PF-009 Test Custom {i}",
                        is_system=False,
                    )
                )
            db.commit()
            assert rbac_service.count_custom_roles(db, tenant_id) == 5

            with pytest.raises(ValidationAppError) as exc:
                rbac_service.assert_can_add_custom_role(db, tenant_id, community)
            assert exc.value.req_id == "BR-PF-061"
        finally:
            db.execute(
                text(
                    "delete from core.role where tenant_id = :t "
                    "and role_code like 'PF009_TEST_C%'"
                ),
                {"t": tenant_id},
            )
            db.commit()


def test_assert_can_add_custom_role_allows_when_enterprise_unlimited():
    """Enterprise (unlimited) never rejects on the custom-role bound."""
    with platform_session() as db:
        tenant_id = _any_tenant_id(db)
        enterprise = _edition(db, "ENTERPRISE")
        # Must not raise regardless of how many custom roles exist.
        rbac_service.assert_can_add_custom_role(db, tenant_id, enterprise)


# ---------------------------------------------------------------------------
# BR-PF-062 — system-role immutability
# ---------------------------------------------------------------------------
def test_system_role_cannot_be_renamed_or_deleted():
    with platform_session() as db:
        system_role = db.scalars(
            select(Role).where(Role.role_code == "TENANT_ADMIN")
        ).first()
        assert system_role is not None and system_role.is_system is True

        with pytest.raises(ValidationAppError) as exc:
            rbac_service.rename_role(db, system_role, "Renamed")
        assert exc.value.req_id == "BR-PF-062"

        with pytest.raises(ValidationAppError) as exc:
            rbac_service.deactivate_role(db, system_role)
        assert exc.value.req_id == "BR-PF-062"

        db.rollback()


def test_custom_role_can_be_renamed_and_deactivated():
    with platform_session() as db:
        tenant_id = _any_tenant_id(db)
        assert tenant_id is not None
        _purge_custom_role(db, tenant_id)
        try:
            db.add(
                Role(
                    tenant_id=tenant_id,
                    role_code=CUSTOM_ROLE_CODE,
                    role_name="Original",
                    is_system=False,
                )
            )
            db.commit()
            role = db.scalars(
                select(Role).where(
                    Role.tenant_id == tenant_id, Role.role_code == CUSTOM_ROLE_CODE
                )
            ).one()

            rbac_service.rename_role(db, role, "Renamed Custom")
            assert role.role_name == "Renamed Custom"

            rbac_service.deactivate_role(db, role)
            assert role.is_deleted is True
            db.commit()
        finally:
            _purge_custom_role(db, tenant_id)


# ---------------------------------------------------------------------------
# core.user_role foundation + backfill
# ---------------------------------------------------------------------------
def test_user_role_backfill_mirrors_users_role_id():
    """``backfill_user_role`` mirrors every live user's role exactly once.

    Batch 1 contract note: the mirror is maintained by an *idempotent backfill*
    (run at bootstrap), not by continuous dual-write. Users created after the last
    backfill are therefore only mirrored on the next run — continuous sync is a
    later authorised batch. This test therefore backfills first, then asserts
    completeness and idempotency.
    """
    from app.db.migrate_pf009 import backfill_user_role

    with platform_session() as db:
        users_with_role = db.execute(
            text(
                "select count(*) from core.users "
                "where role_id is not null and tenant_id is not null "
                "and is_deleted = false"
            )
        ).scalar()

        first_run = backfill_user_role(db)
        mirrored = db.execute(
            text("select count(distinct user_id) from core.user_role")
        ).scalar()
        assert mirrored == users_with_role

        # Idempotent: re-running adds nothing.
        assert backfill_user_role(db) == 0
        assert first_run >= 0

        # No tenant mismatch between core.user_role and core.users.
        mismatched = db.execute(
            text(
                "select count(*) from core.user_role ur "
                "join core.users u on u.user_id = ur.user_id "
                "where ur.tenant_id <> u.tenant_id"
            )
        ).scalar()
        assert mismatched == 0


def test_user_role_unique_constraint_prevents_duplicate_assignment():
    with platform_session() as db:
        row = db.execute(
            text("select tenant_id, user_id, role_id from core.user_role limit 1")
        ).first()
        assert row is not None
        with pytest.raises(Exception):
            db.execute(
                text(
                    "insert into core.user_role "
                    "(user_role_id, tenant_id, user_id, role_id, is_primary) "
                    "values (gen_random_uuid(), :t, :u, :r, true)"
                ),
                {"t": row[0], "u": row[1], "r": row[2]},
            )
            db.flush()
        db.rollback()


# ---------------------------------------------------------------------------
# Tenant isolation / RLS enrolment
# ---------------------------------------------------------------------------
def test_user_role_is_rls_enrolled():
    with platform_session() as db:
        assert rls_enabled(db, "core", "user_role") is True


def test_role_permission_is_rls_enrolled_with_one_policy():
    with platform_session() as db:
        assert rls_enabled(db, "core", "role_permission") is True
        policies = db.execute(
            text(
                "select count(*) from pg_policies "
                "where schemaname='core' and tablename='role_permission' "
                "and policyname='tenant_isolation'"
            )
        ).scalar()
        assert policies == 1


def test_role_permission_has_no_tenant_id_column():
    """Architecture guard: PF-009 Batch 1 must not add tenant_id to that table."""
    with platform_session() as db:
        cols = db.execute(
            text(
                "select count(*) from information_schema.columns "
                "where table_schema='core' and table_name='role_permission' "
                "and column_name='tenant_id'"
            )
        ).scalar()
        assert cols == 0


def test_role_is_still_rls_enrolled_after_pf009():
    with platform_session() as db:
        assert rls_enabled(db, "core", "role") is True


# ---------------------------------------------------------------------------
# PF-009 permission catalogue
# ---------------------------------------------------------------------------
def test_pf009_permission_codes_are_seeded():
    with platform_session() as db:
        codes = {
            row[0]
            for row in db.execute(
                select(Permission.permission_code).where(
                    Permission.permission_code.in_(PF009_PERMISSION_CODES)
                )
            ).all()
        }
        assert codes == set(PF009_PERMISSION_CODES)


# ---------------------------------------------------------------------------
# Regression guard — transitional compatibility
# ---------------------------------------------------------------------------
def test_users_role_id_is_preserved():
    """Batch 1 must NOT remove the transitional single-role column."""
    with platform_session() as db:
        cols = db.execute(
            text(
                "select count(*) from information_schema.columns "
                "where table_schema='core' and table_name='users' "
                "and column_name='role_id' "
                "and is_nullable='NO'"
            )
        ).scalar()
        assert cols == 1


# ---------------------------------------------------------------------------
# Runtime cross-tenant RLS denial (behavioural proof, not just enrolment)
# ---------------------------------------------------------------------------
def test_role_rls_denies_cross_tenant_read():
    """A tenant-bound session sees only its own core.role rows."""
    with platform_session() as db:
        total = db.execute(text("select count(*) from core.role")).scalar()
        per_tenant = db.execute(
            text(
                "select tenant_id, count(*) from core.role "
                "where tenant_id is not null "
                "group by tenant_id having count(*) > 0 "
                "order by count(*) desc limit 2"
            )
        ).all()
        assert len(per_tenant) == 2, "need two tenants owning roles"
        (tenant_a, a_count), (tenant_b, _b_count) = per_tenant

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tenant_a)
        visible = db.execute(text("select count(*) from core.role")).scalar()
        # Exactly the tenant's own rows — NULL-tenant platform roles are excluded.
        assert visible == a_count
        # RLS actually filtered: without a policy this would equal the total.
        assert visible < total
        # The other tenant's rows are invisible even when named explicitly.
        leaked = db.execute(
            text("select count(*) from core.role where tenant_id = :tb"),
            {"tb": tenant_b},
        ).scalar()
        assert leaked == 0
    finally:
        clear_rls_context(db)
        db.close()


def test_role_permission_rls_denies_cross_tenant_read():
    """core.role_permission tenant scope is enforced through core.role."""
    with platform_session() as db:
        total = db.execute(text("select count(*) from core.role_permission")).scalar()
        per_tenant = db.execute(
            text(
                "select r.tenant_id, count(*) from core.role_permission rp "
                "join core.role r on r.role_id = rp.role_id "
                "where r.tenant_id is not null "
                "group by r.tenant_id having count(*) > 0 "
                "order by count(*) desc limit 2"
            )
        ).all()
        assert len(per_tenant) == 2, "need two tenants owning role_permission rows"
        (tenant_a, a_count), _second = per_tenant

    db = SessionLocal()
    try:
        bind_rls_context(db, tenant_id=tenant_a)
        visible = db.execute(text("select count(*) from core.role_permission")).scalar()
        assert visible == a_count, (
            "role_permission RLS must expose exactly the tenant's own rows"
        )
        assert visible < total, "role_permission RLS must filter across tenants"
    finally:
        clear_rls_context(db)
        db.close()


# ---------------------------------------------------------------------------
# Seven authoritative system roles + existing-tenant upgrade path
# ---------------------------------------------------------------------------
BFS_PF009_SYSTEM_ROLES = {
    "TENANT_ADMIN",
    "SALES_MANAGER",
    "SALES_EXECUTIVE",
    "FINANCE_USER",
    "PROJECT_MANAGER",
    "SUPPORT_AGENT",
    "TEAM_MEMBER",
}


def test_roles_catalogue_covers_bfs_pf009_seven_system_roles():
    """The provisioning catalogue must cover all seven BFS-PF-009 §3 roles."""
    from app.db.seed import ROLES

    codes = {code for code, _name, _is_system in ROLES}
    assert BFS_PF009_SYSTEM_ROLES <= codes
    # Every provisioned role is a system role.
    assert all(is_system is True for _c, _n, is_system in ROLES)


def test_rbac_upgrade_backfills_roles_and_grants_for_existing_tenant():
    """_upgrade_rbac_permissions must repair a pre-PF-009 tenant (idempotent)."""
    from app.db.seed import _upgrade_rbac_permissions

    with platform_session() as db:
        tenant = db.scalars(
            select(Tenant).where(Tenant.tenant_code == "EIIP001")
        ).first()
        assert tenant is not None

        # Run twice to prove idempotency.
        _upgrade_rbac_permissions(db, tenant)
        db.commit()
        _upgrade_rbac_permissions(db, tenant)
        db.commit()

        role_codes = {
            row[0]
            for row in db.execute(
                text(
                    "select role_code from core.role "
                    "where tenant_id = :t and is_system = true"
                ),
                {"t": tenant.tenant_id},
            ).all()
        }
        assert BFS_PF009_SYSTEM_ROLES <= role_codes

        granted = db.execute(
            text(
                "select count(distinct p.permission_code) "
                "from core.role_permission rp "
                "join core.role r on r.role_id = rp.role_id "
                "join core.permission p on p.permission_id = rp.permission_id "
                "where r.tenant_id = :t and r.role_code = 'TENANT_ADMIN' "
                "and p.permission_code = any(:codes)"
            ),
            {"t": tenant.tenant_id, "codes": list(PF009_PERMISSION_CODES)},
        ).scalar()
        assert granted == len(PF009_PERMISSION_CODES)


def test_new_system_roles_hold_no_grants():
    """SUPPORT_AGENT / TEAM_MEMBER are seeded with no grants (no invented matrix)."""
    from app.db.seed import _upgrade_rbac_permissions

    with platform_session() as db:
        tenant = db.scalars(
            select(Tenant).where(Tenant.tenant_code == "EIIP001")
        ).first()
        assert tenant is not None
        # Ensure provisioning state regardless of test ordering.
        _upgrade_rbac_permissions(db, tenant)
        db.commit()
        for role_code in ("SUPPORT_AGENT", "TEAM_MEMBER"):
            count = db.execute(
                text(
                    "select count(*) from core.role_permission rp "
                    "join core.role r on r.role_id = rp.role_id "
                    "where r.tenant_id = :t and r.role_code = :c"
                ),
                {"t": tenant.tenant_id, "c": role_code},
            ).scalar()
            assert count == 0, f"{role_code} must not be granted any permission"
