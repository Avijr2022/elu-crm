from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.edition_gating import BRANCH, BUSINESS_UNIT, has_feature
from app.core.security import hash_password
from app.db.migrate_pf001 import apply_pf001_ddl
from app.db.migrate_pf002 import apply_pf002_ddl
from app.db.migrate_pf003 import apply_pf003_ddl
from app.models.pf import (
    Edition,
    EditionFeature,
    EditionLimit,
    FeatureCatalogue,
    Organization,
    Permission,
    Role,
    RolePermission,
    Subscription,
    Tenant,
    TenantBranding,
    TenantSettings,
    User,
)

def _link_role_permission(db: Session, role_id, permission_id) -> None:
    """Idempotently ensure a (role_id, permission_id) link exists.

    Uses ON CONFLICT DO NOTHING so re-seeding (e.g. multiple app lifespans on a
    fresh database) never violates uk_role_permission.
    """
    db.execute(
        pg_insert(RolePermission)
        .values(role_id=role_id, permission_id=permission_id)
        .on_conflict_do_nothing(constraint="uk_role_permission")
    )


# PF-004 organization capability matrix — BFS-PF-004 §12 (HD-01).
# Runtime-wide permission-grain enforcement for the PF surface is still deferred
# to PF-009; this only makes the *seeded* map match the approved matrix.
ORG_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": (
        "organization.create",
        "organization.read",
        "organization.update",
        "organization.delete",
        "organization.export",
    ),
    "FINANCE_USER": ("organization.read", "organization.export"),
    "SALES_MANAGER": ("organization.read",),
    "PLATFORM_ADMIN": ("organization.read",),  # read-only per BFS-PF-004 §12
    "PROJECT_MANAGER": (),
}


# PF-005 branch capability matrix — BFS-PF-005 §12 (basis) + §2 actors.
# Runtime-wide permission-grain enforcement for the PF surface is still deferred
# to PF-009; this only makes the *seeded* map match the approved matrix.
# TENANT_ADMIN / SALES_MANAGER / PROJECT_MANAGER are exactly BFS-PF-005 §12;
# FINANCE_USER (viewer for invoicing) and PLATFORM_ADMIN (read-only, same convention
# as BFS-PF-004 §12) are the §2 actor-list viewers.
BRANCH_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": (
        "branch.create",
        "branch.read",
        "branch.update",
        "branch.delete",
        "branch.export",
    ),
    "FINANCE_USER": ("branch.read",),
    "SALES_MANAGER": ("branch.read",),
    "PROJECT_MANAGER": ("branch.read",),
    "PLATFORM_ADMIN": ("branch.read",),  # read-only
}


def _sync_org_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded ``organization.*`` grants with the approved matrix (idempotent).

    Grants the approved codes and revokes any ``organization.*`` grain that is not
    approved for the role — needed because the generic platform seeding grants the
    whole permission catalogue to PLATFORM_ADMIN/TENANT_ADMIN.
    """
    org_perm_ids = {
        code: permission_id
        for code, permission_id in db.execute(
            select(Permission.permission_code, Permission.permission_id).where(
                Permission.permission_code.like("organization.%")
            )
        ).all()
    }
    if not org_perm_ids:
        return
    for role_code, allowed_codes in ORG_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            org_perm_ids[code] for code in allowed_codes if code in org_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [pid for pid in org_perm_ids.values() if pid not in allowed_ids]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


def _sync_branch_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded ``branch.*`` grants with the approved matrix (idempotent).

    PF-005 equivalent of ``_sync_org_permission_matrix`` (HD-01 pattern): grants the
    approved codes and revokes any ``branch.*`` grain that is not approved for the
    role. Runtime permission-grain enforcement remains deferred to PF-009.
    """
    branch_perm_ids = {
        code: permission_id
        for code, permission_id in db.execute(
            select(Permission.permission_code, Permission.permission_id).where(
                Permission.permission_code.like("branch.%")
            )
        ).all()
    }
    if not branch_perm_ids:
        return
    for role_code, allowed_codes in BRANCH_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            branch_perm_ids[code] for code in allowed_codes if code in branch_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [
            pid for pid in branch_perm_ids.values() if pid not in allowed_ids
        ]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


# PF-006 department capability matrix — BFS-PF-006 §12 (authoritative actor matrix).
# Runtime-wide permission-grain enforcement for the PF surface is still deferred
# to PF-009; this only makes the *seeded* map match the approved matrix.
#
# §12 lists exactly TENANT_ADMIN (all five actions), SALES_MANAGER (read) and
# PROJECT_MANAGER (read). FINANCE_USER and PLATFORM_ADMIN are listed with an *empty*
# tuple on purpose: the generic platform seeding grants the whole permission catalogue
# to PLATFORM_ADMIN/TENANT_ADMIN, so the empty tuple is what makes the seeded map match
# both the authoritative matrix and the enforced PF-006 role gate
# (``app.services.pf.department_service``). Support Agent appears in BFS §2 but not in
# the §12 matrix, so it is not granted here.
DEPARTMENT_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": (
        "department.create",
        "department.read",
        "department.update",
        "department.delete",
        "department.export",
    ),
    "SALES_MANAGER": ("department.read",),
    "PROJECT_MANAGER": ("department.read",),
    "FINANCE_USER": (),  # no PF-006 grant (BFS-PF-006 §12)
    "PLATFORM_ADMIN": (),  # no PF-006 grant (BFS-PF-006 §12 lists no platform actor)
}


def _sync_department_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded ``department.*`` grants with the approved matrix (idempotent).

    PF-006 equivalent of ``_sync_branch_permission_matrix`` (HD-01 pattern): grants the
    approved codes and revokes any ``department.*`` grain that is not approved for the
    role. Runtime permission-grain enforcement remains deferred to PF-009.
    """
    department_perm_ids = {
        code: permission_id
        for code, permission_id in db.execute(
            select(Permission.permission_code, Permission.permission_id).where(
                Permission.permission_code.like("department.%")
            )
        ).all()
    }
    if not department_perm_ids:
        return
    for role_code, allowed_codes in DEPARTMENT_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            department_perm_ids[code]
            for code in allowed_codes
            if code in department_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [
            pid for pid in department_perm_ids.values() if pid not in allowed_ids
        ]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


# PF-007 business-unit grants per BFS-PF-007 §12 and the approved D2/D3 resolutions:
# Tenant Admin create/read/update/delete/export, Sales Manager read, Finance User read,
# Project Manager read (D3), export Tenant-Admin-only (D2). The explicit empty tuple for
# PLATFORM_ADMIN mirrors PF-004/PF-005/PF-006: the generic platform seeding would
# otherwise leave the whole catalogue (including business_unit.*) granted to
# PLATFORM_ADMIN, which would not match the enforced PF-007 role gate
# (``app.services.pf.business_unit_service``). SUPPORT_AGENT is not an actor in §12.
BUSINESS_UNIT_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": (
        "business_unit.create",
        "business_unit.read",
        "business_unit.update",
        "business_unit.delete",
        "business_unit.export",
    ),
    "SALES_MANAGER": ("business_unit.read",),
    "FINANCE_USER": ("business_unit.read",),
    "PROJECT_MANAGER": ("business_unit.read",),
    "PLATFORM_ADMIN": (),  # no PF-007 grant (BFS-PF-007 §12 lists no platform actor)
}


# PF-008 user & identity capability matrix - BFS-PF-008 §12 (approved actor matrix).
# Tenant Admin and Platform Admin hold create/read/update/delete/reset_password; §10 adds
# ``user.export``. The §12 self-scope of SALES_EXECUTIVE (read/update *self*) is realised by
# the ``/users/me`` endpoints rather than by a directory grant, so no grain is granted here
# (no permission values are invented). Runtime permission-grain enforcement stays PF-009.
USER_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": (
        "user.create",
        "user.read",
        "user.update",
        "user.delete",
        "user.export",
        "user.reset_password",
    ),
    "PLATFORM_ADMIN": (
        "user.create",
        "user.read",
        "user.update",
        "user.delete",
        "user.export",
        "user.reset_password",
    ),
    "SALES_EXECUTIVE": (),
    "SALES_MANAGER": (),
    "PROJECT_MANAGER": (),
    "FINANCE_USER": (),
}


def _sync_user_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded ``user.*`` grants with the approved matrix (idempotent).

    PF-008 equivalent of ``_sync_business_unit_permission_matrix`` (HD-01 pattern):
    grants the approved codes and revokes any ``user.*`` grain that is not approved for
    the role. Runtime permission-grain enforcement remains deferred to PF-009.
    """
    user_perm_ids = {
        code: permission_id
        for code, permission_id in db.execute(
            select(Permission.permission_code, Permission.permission_id).where(
                Permission.permission_code.like("user.%")
            )
        ).all()
    }
    if not user_perm_ids:
        return
    for role_code, allowed_codes in USER_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            user_perm_ids[code] for code in allowed_codes if code in user_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [pid for pid in user_perm_ids.values() if pid not in allowed_ids]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


def _sync_business_unit_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded ``business_unit.*`` grants with the approved matrix (idempotent).

    PF-007 equivalent of ``_sync_department_permission_matrix`` (HD-01 pattern): grants
    the approved codes and revokes any ``business_unit.*`` grain that is not approved for
    the role. Runtime permission-grain enforcement remains deferred to PF-009.
    """
    business_unit_perm_ids = {
        code: permission_id
        for code, permission_id in db.execute(
            select(Permission.permission_code, Permission.permission_id).where(
                Permission.permission_code.like("business_unit.%")
            )
        ).all()
    }
    if not business_unit_perm_ids:
        return
    for role_code, allowed_codes in BUSINESS_UNIT_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            business_unit_perm_ids[code]
            for code in allowed_codes
            if code in business_unit_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [
            pid for pid in business_unit_perm_ids.values() if pid not in allowed_ids
        ]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


# PF-011 system-configuration capability matrix — BFS-PF-011 §12 (approved actor matrix).
# Tenant Admin configures tenant settings; Platform Admin holds all four grains because
# /api/v1/platform/settings is platform-global; Finance User and Sales Manager are
# read-only / read-limited viewers (no configure grant). The generic platform seeding
# hands the *whole* catalogue to TENANT_ADMIN/PLATFORM_ADMIN, so this sync is precisely
# what prevents the four PF-011 grains from being granted universally by accident.
SETTINGS_PERMISSION_MATRIX: dict[str, tuple[str, ...]] = {
    "TENANT_ADMIN": ("settings.read", "settings.configure"),
    "PLATFORM_ADMIN": (
        "settings.read",
        "settings.configure",
        "platform_settings.read",
        "platform_settings.configure",
    ),
    "FINANCE_USER": ("settings.read",),
    "SALES_MANAGER": ("settings.read",),
    "SALES_EXECUTIVE": (),
    "PROJECT_MANAGER": (),
}


def _sync_settings_permission_matrix(db: Session, tenant_id) -> None:
    """Align seeded PF-011 grants with the approved matrix (idempotent).

    PF-011 equivalent of ``_sync_user_permission_matrix`` (HD-01 pattern): grants the
    approved codes and revokes any grain that is not approved for the role. Both
    ``settings.*`` and ``platform_settings.*`` are governed by this one matrix because
    PF-011 owns both families, and the two prefixes cannot overlap under ``LIKE``.

    PF-011 has no edition feature (``app.core.edition_gating`` carries no PF-011 constant),
    so unlike ``branch.*`` / ``business_unit.*`` there is no edition gate to mirror here.
    """
    settings_perm_ids = {}
    for prefix in ("settings.%", "platform_settings.%"):
        settings_perm_ids.update(
            {
                code: permission_id
                for code, permission_id in db.execute(
                    select(Permission.permission_code, Permission.permission_id).where(
                        Permission.permission_code.like(prefix)
                    )
                ).all()
            }
        )
    if not settings_perm_ids:
        return
    for role_code, allowed_codes in SETTINGS_PERMISSION_MATRIX.items():
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        if role is None:
            continue
        allowed_ids = {
            settings_perm_ids[code] for code in allowed_codes if code in settings_perm_ids
        }
        for permission_id in allowed_ids:
            _link_role_permission(db, role.role_id, permission_id)
        stale_ids = [
            pid for pid in settings_perm_ids.values() if pid not in allowed_ids
        ]
        if stale_ids:
            db.execute(
                delete(RolePermission).where(
                    RolePermission.role_id == role.role_id,
                    RolePermission.permission_id.in_(stale_ids),
                )
            )
    db.flush()


# 1x1 JPEG for seeded tenant branding (PDF logo smoke test).
_SEED_LOGO_JPEG = (
    "data:image/jpeg;base64,"
    "/9j/4AAQSkZJRgABAQEAYABgAAD/2wBDAAgGBgcGBQgHBwcJCQgKDBQNDAsLDBkSEw8UHRof"
    "Hh0aHBwgJC4nICIsIxwcKDcpLDAxNDQ0Hyc5PTgyPC4zNDL/2wBDAQkJCQwLDBgNDRgyIRwh"
    "MjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjL/wAAR"
    "CAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAn/xAAUEAEAAAAAAAAAAAAAAAAA"
    "AAAA/8QAFQEBAQAAAAAAAAAAAAAAAAAAAAX/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAA"
    "IRAxEAPwCwAA8A/9k="
)


PERMISSIONS = [
    ("tenant.read", "View tenant", "PF"),
    ("tenant.update", "Update tenant", "PF"),
    ("user.create", "Create user", "PF"),
    ("user.read", "View user", "PF"),
    ("user.update", "Update user", "PF"),
    ("user.delete", "Deactivate user", "PF"),
    ("user.export", "Export users", "PF"),
    ("user.reset_password", "Admin password reset", "PF"),
    ("role.create", "Create role", "PF"),
    ("role.read", "View role", "PF"),
    ("role.update", "Update role", "PF"),
    ("role.delete", "Deactivate role", "PF"),
    ("role.export", "Export roles", "PF"),
    ("role.configure", "Configure role permissions", "PF"),
    ("role.assign", "Assign roles", "PF"),
    ("permission.read", "View permission catalogue", "PF"),
    ("edition.create", "Create edition", "PF"),
    ("edition.read", "View edition", "PF"),
    ("edition.update", "Update edition", "PF"),
    ("edition.delete", "Delete edition", "PF"),
    ("edition.publish", "Publish edition", "PF"),
    ("edition.deprecate", "Deprecate edition", "PF"),
    ("edition.export", "Export edition matrix", "PF"),
    ("organization.create", "Create organization", "PF"),
    ("organization.read", "View organization", "PF"),
    ("organization.update", "Update organization", "PF"),
    ("organization.delete", "Delete organization", "PF"),
    ("organization.export", "Export organizations", "PF"),
    ("branch.create", "Create branch", "PF"),
    ("branch.read", "View branch", "PF"),
    ("branch.update", "Update branch", "PF"),
    ("branch.delete", "Delete branch", "PF"),
    ("branch.export", "Export branches", "PF"),
    ("department.create", "Create department", "PF"),
    ("department.read", "View department", "PF"),
    ("department.update", "Update department", "PF"),
    ("department.delete", "Delete department", "PF"),
    ("department.export", "Export departments", "PF"),
    ("business_unit.create", "Create business unit", "PF"),
    ("business_unit.read", "View business unit", "PF"),
    ("business_unit.update", "Update business unit", "PF"),
    ("business_unit.delete", "Delete business unit", "PF"),
    ("business_unit.export", "Export business units", "PF"),
    ("settings.read", "View system settings", "PF"),
    ("settings.configure", "Configure system settings", "PF"),
    ("platform_settings.read", "View platform-global settings", "PF"),
    ("platform_settings.configure", "Configure platform-global settings", "PF"),
    ("lead.create", "Create lead", "CRM"),
    ("lead.read", "View lead", "CRM"),
    ("lead.update", "Update lead", "CRM"),
    ("lead.convert", "Convert lead", "CRM"),
    ("lead.qualify", "Qualify lead", "CRM"),
    ("lead.disqualify", "Disqualify lead", "CRM"),
    ("customer.read", "View customer", "CRM"),
    ("customer.create", "Create customer", "CRM"),
    ("customer.update", "Update customer", "CRM"),
    ("customer.suspend", "Suspend customer", "CRM"),
    ("activity.read", "View activity", "CRM"),
    ("activity.create", "Create activity", "CRM"),
    ("opportunity.read", "View opportunity", "CRM"),
    ("opportunity.update", "Update opportunity", "CRM"),
    ("opportunity.approve", "Close won / approve opportunity", "CRM"),
    ("quotation.read", "View quotation", "SAL"),
    ("quotation.create", "Create quotation", "SAL"),
    ("quotation.update", "Update quotation", "SAL"),
    ("quotation.submit", "Submit quotation", "SAL"),
    ("quotation.approve", "Approve quotation", "SAL"),
    ("quotation.cancel", "Cancel quotation", "SAL"),
]

ROLES = [
    ("PLATFORM_ADMIN", "Platform Admin", True),
    ("TENANT_ADMIN", "Tenant Admin", True),
    ("SALES_EXECUTIVE", "Sales Executive", True),
    ("SALES_MANAGER", "Sales Manager", True),
    ("PROJECT_MANAGER", "Project Manager", True),
    ("FINANCE_USER", "Finance User", True),
    # BFS-PF-009 §3 seeds SEVEN system roles. These two were missing from
    # provisioning (tests worked around it by creating the role ad hoc). They are
    # seeded with NO grants on purpose: their §3 capabilities (Support Agent
    # "SRV full", Team Member "read-only base") reference modules/permission sets
    # that are not implemented, and inventing a grant set is out of scope for
    # PF-009 Batch 1. FINANCE_USER / other PF matrices already record the
    # "Support Agent has no grant" position.
    ("SUPPORT_AGENT", "Support Agent", True),
    ("TEAM_MEMBER", "Team Member", True),
]

FEATURE_CATALOGUE = [
    ("CRM_LEAD", "CRM Lead Management", "CRM", "Lead capture and convert"),
    ("CRM_OPPORTUNITY", "Opportunity Pipeline", "CRM", "Opportunity module"),
    ("CRM_CUSTOMER", "Customer Management", "CRM", "Customer accounts"),
    ("CRM_ACTIVITY", "Activity Ledger", "CRM", "Calls, tasks, timeline"),
    ("SAL_QUOTE", "Quotations", "SAL", "Sales quotations"),
    ("PRJ_WO", "Projects / Work Orders", "PRJ", "Delivery"),
    ("FIN_INVOICE", "Invoicing", "FIN", "AR invoicing"),
    ("SSO", "Single Sign-On", "PF", "Enterprise SSO"),
    ("AUDIT_RETENTION_7Y", "7-year audit retention", "PF", "Enterprise audit"),
    ("MFA", "Multi-factor authentication", "PF", "MFA"),
    ("BRANCH", "Branch hierarchy", "PF", "Multi-branch"),
    ("BUSINESS_UNIT", "Business units", "PF", "BU management"),
]

# ELU-EDM-001 limits
EDITION_SPECS = {
    "COMMUNITY": {
        "name": "Community Edition",
        "description": "Learning & demo",
        "display_order": 1,
        "max_users": 5,
        "features": [
            "CRM_LEAD",
            "CRM_CUSTOMER",
            "CRM_ACTIVITY",
            "MFA",
        ],
        "limits": [
            ("MAX_USERS", "Maximum users", Decimal("5"), "users"),
            ("MAX_STORAGE_GB", "Maximum storage", Decimal("5"), "GB"),
            ("MAX_ROLES", "Maximum custom roles", Decimal("5"), "roles"),
        ],
    },
    "PROFESSIONAL": {
        "name": "Professional Edition",
        "description": "SME full CRM/ERP suite",
        "display_order": 2,
        "max_users": 50,
        "features": [
            "CRM_LEAD",
            "CRM_OPPORTUNITY",
            "CRM_CUSTOMER",
            "CRM_ACTIVITY",
            "SAL_QUOTE",
            "PRJ_WO",
            "FIN_INVOICE",
            "MFA",
            "BRANCH",
            "BUSINESS_UNIT",
        ],
        "limits": [
            ("MAX_USERS", "Maximum users", Decimal("50"), "users"),
            ("MAX_STORAGE_GB", "Maximum storage", Decimal("100"), "GB"),
            ("MAX_ROLES", "Maximum custom roles", Decimal("25"), "roles"),
            ("MAX_BRANCHES", "Maximum branches", Decimal("10"), "branches"),
            # D5 / BR-PF-050: Professional = 20 business units.
            ("MAX_BUSINESS_UNITS", "Maximum business units", Decimal("20"), "business units"),
        ],
    },
    "ENTERPRISE": {
        "name": "Enterprise Edition",
        "description": "Large enterprise SaaS",
        "display_order": 3,
        "max_users": None,
        "features": [
            "CRM_LEAD",
            "CRM_OPPORTUNITY",
            "CRM_CUSTOMER",
            "CRM_ACTIVITY",
            "SAL_QUOTE",
            "PRJ_WO",
            "FIN_INVOICE",
            "MFA",
            "BRANCH",
            "BUSINESS_UNIT",
            "SSO",
            "AUDIT_RETENTION_7Y",
        ],
        "limits": [
            ("MAX_USERS", "Maximum users", Decimal("999999"), "users"),
            ("MAX_STORAGE_GB", "Maximum storage", Decimal("999999"), "GB"),
            ("MAX_ROLES", "Maximum custom roles", Decimal("999999"), "roles"),
            ("MAX_BRANCHES", "Maximum branches", Decimal("999999"), "branches"),
            # D5 / BR-PF-050: Enterprise = unlimited (same convention as MAX_BRANCHES).
            ("MAX_BUSINESS_UNITS", "Maximum business units", Decimal("999999"), "business units"),
        ],
    },
}


def ensure_schemas(db: Session) -> None:
    for schema in (
        "core",
        "master",
        "crm",
        "sales",
        "projects",
        "finance",
        "service",
        "integration",
        "shared",
        "audit",
    ):
        db.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
    db.commit()


def _ensure_feature_catalogue(db: Session) -> None:
    existing = {
        r.feature_code
        for r in db.scalars(select(FeatureCatalogue)).all()
    }
    for code, name, domain, desc in FEATURE_CATALOGUE:
        if code in existing:
            continue
        db.add(
            FeatureCatalogue(
                id=uuid4(),
                feature_code=code,
                feature_name=name,
                module_domain=domain,
                description=desc,
            )
        )
    db.flush()


def _ensure_editions(db: Session) -> dict[str, Edition]:
    result: dict[str, Edition] = {}
    for code, spec in EDITION_SPECS.items():
        edition = db.scalars(
            select(Edition).where(Edition.code == code)
        ).first()
        if edition is None:
            edition = Edition(
                id=uuid4(),
                code=code,
                name=spec["name"],
                description=spec["description"],
                status="ACTIVE",
                display_order=spec["display_order"],
                currency_code="INR",
                published_at=datetime.now(timezone.utc),
                version_no=1,
            )
            db.add(edition)
            db.flush()
        else:
            edition.name = spec["name"]
            edition.description = spec["description"]
            edition.display_order = spec["display_order"]
            if edition.status not in ("DEPRECATED", "ARCHIVED", "CANCELLED"):
                edition.status = "ACTIVE"
            if edition.published_at is None and edition.status == "ACTIVE":
                edition.published_at = datetime.now(timezone.utc)

        # Features
        have_f = {f.feature_code for f in edition.features}
        for fcode in spec["features"]:
            if fcode in have_f:
                continue
            edition.features.append(
                EditionFeature(
                    id=uuid4(),
                    feature_code=fcode,
                    is_enabled=True,
                    is_visible=True,
                )
            )

        # Limits
        have_l = {lim.limit_code for lim in edition.limits}
        for lcode, lname, lval, lunit in spec["limits"]:
            if lcode in have_l:
                continue
            edition.limits.append(
                EditionLimit(
                    id=uuid4(),
                    limit_code=lcode,
                    limit_name=lname,
                    limit_value=lval,
                    limit_unit=lunit,
                    is_hard_limit=True,
                    grace_percent=Decimal("0"),
                )
            )
        result[code] = edition
    db.flush()
    return result


def seed_platform(db: Session) -> None:
    settings = get_settings()
    ensure_schemas(db)
    apply_pf001_ddl(db)
    apply_pf002_ddl(db)
    apply_pf003_ddl(db)
    _ensure_feature_catalogue(db)
    editions = _ensure_editions(db)

    existing = db.scalars(
        select(Tenant).where(Tenant.tenant_code == "EIIP001")
    ).first()
    if existing:
        # Ensure platform admin role/user even on re-seed skip path
        _ensure_platform_admin(db, existing, editions)
        _upgrade_crm_permissions(db, existing)
        _upgrade_sal_permissions(db, existing)
        _upgrade_rbac_permissions(db, existing)
        _ensure_community_demo_tenant(db, editions)
        _ensure_tenant_branding(db, existing)
        db.commit()
        return

    professional = editions["PROFESSIONAL"]

    tenant = Tenant(
        tenant_code="EIIP001",
        tenant_name="Euphoria",
        legal_name="Euphoria Infotech (I) Limited",
        edition_id=professional.id,
        organization_type="Pvt Ltd",
        gstin="19AABCE1234F1Z5",
        pan="AABCE1234F",
        website="https://www.euphoriainfotech.com",
        email="admin@euphoriainfotech.com",
        mobile="+919876543210",
        status="ACTIVE",
        activation_date=date.today(),
    )
    db.add(tenant)
    db.flush()

    org = Organization(
        tenant_id=tenant.tenant_id,
        organization_code="HO001",
        organization_name="Euphoria Head Office",
        legal_name="Euphoria Infotech (I) Limited",
        organization_type="ROOT",
        email="ho@euphoriainfotech.com",
        phone="+913340000000",
        status="ACTIVE",
        is_root=True,
        level=0,
        default_currency_code="INR",
        fiscal_year_start_month=4,
    )
    db.add(org)
    db.flush()

    fy_start = date(
        date.today().year if date.today().month >= 4 else date.today().year - 1,
        settings.default_fy_start_month,
        settings.default_fy_start_day,
    )
    db.add(
        TenantSettings(
            tenant_id=tenant.tenant_id,
            financial_year_start=fy_start,
            currency_code=settings.default_currency,
            time_zone=settings.default_timezone,
            date_format=settings.default_date_format,
            default_language=settings.default_language,
        )
    )
    _ensure_tenant_branding(db, tenant)

    db.add(
        Subscription(
            tenant_id=tenant.tenant_id,
            edition_id=professional.id,
            subscription_number="SUB-2026-000001",
            plan_type="Yearly",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            amount="0",
            currency_code="INR",
            payment_status="PAID",
            subscription_status="ACTIVE",
        )
    )

    perm_map: dict[str, Permission] = {}
    for code, name, module in PERMISSIONS:
        perm = Permission(
            permission_code=code, permission_name=name, module_code=module
        )
        db.add(perm)
        perm_map[code] = perm
    db.flush()

    role_map: dict[str, Role] = {}
    for code, name, is_system in ROLES:
        role = Role(
            tenant_id=tenant.tenant_id,
            role_code=code,
            role_name=name,
            description=f"System role: {name}",
            is_system=is_system,
        )
        db.add(role)
        role_map[code] = role
    db.flush()

    for perm in perm_map.values():
        _link_role_permission(
            db, role_map["PLATFORM_ADMIN"].role_id, perm.permission_id
        )
        _link_role_permission(
            db, role_map["TENANT_ADMIN"].role_id, perm.permission_id
        )
    for code in ("lead.create", "lead.read", "lead.update", "customer.read", "customer.create", "activity.read", "activity.create", "opportunity.read", "opportunity.update"):
        _link_role_permission(
            db, role_map["SALES_EXECUTIVE"].role_id, perm_map[code].permission_id
        )
    for code in ("lead.create", "lead.read", "lead.update", "lead.convert", "customer.read", "customer.create", "customer.update", "activity.read", "activity.create", "opportunity.read", "opportunity.update", "opportunity.approve"):
        _link_role_permission(
            db, role_map["SALES_MANAGER"].role_id, perm_map[code].permission_id
        )
    db.flush()

    # PF-004 organization grants per BFS-PF-004 §12 (HD-01 correction).
    _sync_org_permission_matrix(db, tenant.tenant_id)

    # PF-005 branch grants per BFS-PF-005 §12 (groundwork; no runtime grain enforcement).
    _sync_branch_permission_matrix(db, tenant.tenant_id)

    # PF-006 department grants per BFS-PF-006 §12 (groundwork; no runtime grain enforcement).
    _sync_department_permission_matrix(db, tenant.tenant_id)

    # PF-007 business-unit grants per BFS-PF-007 §12 (groundwork; no runtime grain enforcement).
    _sync_business_unit_permission_matrix(db, tenant.tenant_id)

    # PF-008 user/identity grants per BFS-PF-008 §12 (groundwork; no runtime grain enforcement).
    _sync_user_permission_matrix(db, tenant.tenant_id)

    # PF-011 settings/platform-settings grants per BFS-PF-011 §12 (scoped; no universal grant).
    _sync_settings_permission_matrix(db, tenant.tenant_id)

    # Seed admin acts as Platform Admin for PF-001 ops (Euphoria demo)
    admin = User(
        tenant_id=tenant.tenant_id,
        organization_id=org.organization_id,
        role_id=role_map["PLATFORM_ADMIN"].role_id,
        employee_code="EMP000001",
        first_name="Euphoria",
        last_name="Admin",
        display_name="Euphoria Admin",
        email=settings.seed_admin_email.lower(),
        mobile="+919876543210",
        password_hash=hash_password(settings.seed_admin_password),
        designation="Platform Administrator",
        account_status="ACTIVE",
    )
    db.add(admin)
    _upgrade_crm_permissions(db, tenant)
    _upgrade_sal_permissions(db, tenant)
    _ensure_community_demo_tenant(db, editions)
    db.commit()


def _ensure_platform_admin(
    db: Session, tenant: Tenant, editions: dict[str, Edition]
) -> None:
    """Upgrade existing Euphoria seed to PF-001 roles/permissions when re-running."""
    settings = get_settings()
    _ = editions

    # Permissions
    for code, name, module in PERMISSIONS:
        exists = db.scalars(
            select(Permission).where(Permission.permission_code == code)
        ).first()
        if not exists:
            db.add(
                Permission(
                    permission_code=code, permission_name=name, module_code=module
                )
            )
    db.flush()

    # PF-004 organization grants per BFS-PF-004 §12 (HD-01 correction).
    _sync_org_permission_matrix(db, tenant.tenant_id)

    # PF-005 branch grants per BFS-PF-005 §12 (groundwork; no runtime grain enforcement).
    _sync_branch_permission_matrix(db, tenant.tenant_id)

    # PF-006 department grants per BFS-PF-006 §12 (groundwork; no runtime grain enforcement).
    _sync_department_permission_matrix(db, tenant.tenant_id)

    # PF-007 business-unit grants per BFS-PF-007 §12 (groundwork; no runtime grain enforcement).
    _sync_business_unit_permission_matrix(db, tenant.tenant_id)

    # PF-008 user/identity grants per BFS-PF-008 §12 (groundwork; no runtime grain enforcement).
    _sync_user_permission_matrix(db, tenant.tenant_id)

    # PF-011 settings/platform-settings grants per BFS-PF-011 §12 (scoped; no universal grant).
    _sync_settings_permission_matrix(db, tenant.tenant_id)

    platform_role = db.scalars(
        select(Role).where(
            Role.tenant_id == tenant.tenant_id,
            Role.role_code == "PLATFORM_ADMIN",
        )
    ).first()
    if platform_role is None:
        platform_role = Role(
            tenant_id=tenant.tenant_id,
            role_code="PLATFORM_ADMIN",
            role_name="Platform Admin",
            description="System role: Platform Admin",
            is_system=True,
        )
        db.add(platform_role)
        db.flush()

    admin = db.scalars(
        select(User).where(
            User.tenant_id == tenant.tenant_id,
            User.email == settings.seed_admin_email.lower(),
        )
    ).first()
    if admin:
        admin.role_id = platform_role.role_id
        admin.designation = "Platform Administrator"


CRM_SALES_EXEC_PERMS = (
    "lead.create",
    "lead.read",
    "lead.update",
    "lead.qualify",
    "lead.disqualify",
    "customer.read",
    "customer.create",
    "activity.read",
    "activity.create",
    "opportunity.read",
    "opportunity.update",
    "quotation.read",
    "quotation.create",
    "quotation.update",
    "quotation.submit",
    "quotation.cancel",
)
CRM_COMMUNITY_PERMS = tuple(
    c for c in CRM_SALES_EXEC_PERMS if not c.startswith("opportunity.")
) + ("lead.convert", "lead.qualify", "lead.disqualify", "customer.update")
CRM_SALES_MANAGER_PERMS = CRM_SALES_EXEC_PERMS + (
    "lead.convert",
    "customer.update",
    "opportunity.approve",
    "quotation.approve",
)


# BR-CRM-047 / REQ-CRM-028: ``customer.suspend`` is Finance-User-only. It is excluded
# from the generic whole-catalogue grant to TENANT_ADMIN / PLATFORM_ADMIN and granted
# explicitly to FINANCE_USER. ``app.core.rbac.require_customer_suspend`` additionally
# enforces the Finance role at runtime (defence in depth).
FINANCE_ONLY_PERMISSIONS: tuple[str, ...] = ("customer.suspend",)


def _exclude_finance_only(perm_codes: tuple[str, ...]) -> tuple[str, ...]:
    """Drop the Finance-only grains from a generic grant tuple (BR-CRM-047)."""
    return tuple(code for code in perm_codes if code not in FINANCE_ONLY_PERMISSIONS)


def _revoke_permission_from_other_roles(
    db: Session,
    tenant_id,
    permission_code: str,
    keep_role_codes: tuple[str, ...],
) -> int:
    """Delete RolePermission rows for ONE permission in ONE tenant.

    Every grant held by a role in ``keep_role_codes`` is preserved, and the deletion is
    scoped to ``permission_code`` *and* ``tenant_id`` so no other grant and no other
    tenant is affected. Used to heal tenants provisioned before ``customer.suspend``
    became Finance-User-only (BR-CRM-047). Returns the number of rows deleted.

    FAIL-CLOSED: when ``keep_role_codes`` is non-empty but NONE of those roles exist in
    the tenant, nothing is deleted and ``0`` is returned. Without this guard the
    ``notin_`` filter would be skipped and every holder of the permission would be
    removed, leaving the tenant unable to perform the guarded operation at all. An
    empty ``keep_role_codes`` still means "revoke from every role" (unchanged).
    """
    perm = db.scalars(
        select(Permission).where(Permission.permission_code == permission_code)
    ).first()
    if perm is None:
        return 0
    tenant_role_ids = list(
        db.scalars(select(Role.role_id).where(Role.tenant_id == tenant_id)).all()
    )
    if not tenant_role_ids:
        return 0
    keep_role_ids = list(
        db.scalars(
            select(Role.role_id).where(
                Role.tenant_id == tenant_id,
                Role.role_code.in_(keep_role_codes),
            )
        ).all()
    )
    # M4: named keepers that do not resolve must not turn into "revoke everything".
    if keep_role_codes and not keep_role_ids:
        return 0
    stmt = delete(RolePermission).where(
        RolePermission.permission_id == perm.permission_id,
        RolePermission.role_id.in_(tenant_role_ids),
    )
    if keep_role_ids:
        stmt = stmt.where(RolePermission.role_id.notin_(keep_role_ids))
    result = db.execute(stmt)
    db.flush()
    return int(result.rowcount or 0)


FINANCE_SUSPEND_ROLE_CODE = "FINANCE_USER"


def _role_codes_holding(db: Session, tenant_id, permission_code: str) -> set[str]:
    """Return the role codes in ``tenant_id`` that currently hold ``permission_code``."""
    rows = db.execute(
        select(Role.role_code)
        .join(RolePermission, RolePermission.role_id == Role.role_id)
        .join(Permission, Permission.permission_id == RolePermission.permission_id)
        .where(
            Role.tenant_id == tenant_id,
            Permission.permission_code == permission_code,
        )
    ).all()
    return {row[0] for row in rows}


#: Only provisioned tenants in these lifecycle states are eligible for the
#: ``customer.suspend`` correction. Every other state is reported and skipped.
SYNC_ELIGIBLE_TENANT_STATUSES: frozenset[str] = frozenset({"ACTIVE", "TRIAL"})

SKIP_REASON_FINANCE_ROLE_MISSING = "finance_role_missing"
SKIP_REASON_SOFT_DELETED = "soft_deleted"
SKIP_REASON_TENANT_INACTIVE = "tenant_inactive"
SKIP_REASON_NOT_PROVISIONED = "not_provisioned"


def _tenant_status_skip_reason(status: str | None) -> str:
    """Skip reason for a tenant whose lifecycle state is not eligible."""
    return f"status_{(status or 'unknown').lower()}"


def _finance_role_present(db: Session, tenant_id) -> bool:
    """True when the tenant owns a live ``FINANCE_USER`` role.

    Read-only probe: the role is NEVER created here (no tenant provisioning happens
    in this module) and a soft-deleted role does not count as present.
    """
    return (
        db.scalars(
            select(Role.role_id).where(
                Role.tenant_id == tenant_id,
                Role.role_code == FINANCE_SUSPEND_ROLE_CODE,
                Role.is_deleted.is_(False),
            )
        ).first()
        is not None
    )


def _finance_only_skipped_result(
    tenant_id,
    skip_reason: str,
    *,
    finance_role_present: bool = False,
) -> dict:
    """Structured "nothing was touched" summary for an ineligible tenant."""
    return {
        "tenant_id": str(tenant_id),
        "permission_created": False,
        "finance_role_present": finance_role_present,
        "granted": 0,
        "revoked": 0,
        "finance_holds": False,
        "extra_holders": [],
        "ok": False,
        "skipped": True,
        "skip_reason": skip_reason,
    }


def _tenant_sync_skip_reason(
    *,
    status: str | None,
    is_active: bool | None,
    is_deleted: bool | None,
    activation_date,
    activated_on,
    finance_role_present: bool,
) -> str | None:
    """Return why a tenant must be skipped, or ``None`` when it is eligible.

    Shared by the dry run and the apply path so both use identical rules. Order is
    significant: soft-delete and inactive flags win over the lifecycle status, and a
    non-eligible status wins over the (less informative) missing-role reason.
    """
    if is_deleted:
        return SKIP_REASON_SOFT_DELETED
    if is_active is False:
        return SKIP_REASON_TENANT_INACTIVE
    if status not in SYNC_ELIGIBLE_TENANT_STATUSES:
        return _tenant_status_skip_reason(status)
    if activation_date is None and activated_on is None:
        return SKIP_REASON_NOT_PROVISIONED
    if not finance_role_present:
        return SKIP_REASON_FINANCE_ROLE_MISSING
    return None


def sync_crm_finance_only_matrix(db: Session, tenant_id) -> dict:
    """Make ``customer.suspend`` FINANCE_USER-only for ONE tenant (BR-CRM-047).

    Idempotent and tenant-scoped. Reuses the existing seed helpers so no unrelated
    grant is disturbed:

      1. skip the tenant entirely when it has no live ``FINANCE_USER`` role;
      2. create the catalogue row if this tenant's catalogue predates it;
      3. grant it to FINANCE_USER (``_grant_role_permissions``);
      4. revoke it from every other role in the tenant
         (``_revoke_permission_from_other_roles``, scoped to one permission).

    Returns a summary dict (see the ``ok`` key for the post-condition, and
    ``skipped`` / ``skip_reason`` for a tenant that was deliberately left alone).
    """
    permission_code = FINANCE_ONLY_PERMISSIONS[0]
    # BR-CRM-047: without the keeper role there is nobody to hold the grain, so
    # granting is a no-op (``_grant_role_permissions`` returns early) and revoking
    # would strip EVERY holder, leaving the tenant unable to suspend anyone at all.
    # The catalogue row is not created either - it could never be granted here.
    if not _finance_role_present(db, tenant_id):
        return _finance_only_skipped_result(
            tenant_id,
            SKIP_REASON_FINANCE_ROLE_MISSING,
            finance_role_present=False,
        )

    created = False
    if (
        db.scalars(
            select(Permission).where(Permission.permission_code == permission_code)
        ).first()
        is None
    ):
        db.add(
            Permission(
                permission_code=permission_code,
                permission_name="Suspend customer",
                module_code="CRM",
            )
        )
        db.flush()
        created = True

    before = _role_codes_holding(db, tenant_id, permission_code)
    _grant_role_permissions(
        db, tenant_id, FINANCE_SUSPEND_ROLE_CODE, FINANCE_ONLY_PERMISSIONS
    )
    revoked = _revoke_permission_from_other_roles(
        db, tenant_id, permission_code, (FINANCE_SUSPEND_ROLE_CODE,)
    )
    after = _role_codes_holding(db, tenant_id, permission_code)
    extra = sorted(after - {FINANCE_SUSPEND_ROLE_CODE})

    return {
        "tenant_id": str(tenant_id),
        "permission_created": created,
        "finance_role_present": True,
        "granted": len(after - before),
        "revoked": revoked,
        "finance_holds": FINANCE_SUSPEND_ROLE_CODE in after,
        "extra_holders": extra,
        "ok": (not extra) and (FINANCE_SUSPEND_ROLE_CODE in after),
        "skipped": False,
        "skip_reason": None,
    }


def sync_finance_only_permissions(
    db: Session,
    *,
    tenant_codes: tuple[str, ...] | None = None,
    apply: bool = False,
) -> dict:
    """All-tenants correction: ``customer.suspend`` held by FINANCE_USER only.

    This is the all-tenants synchronization point. ``seed_platform`` only re-seeds the
    platform tenant (EIIP001) and the Community demo tenant (COMU001), so a tenant that
    predates a catalogue change is never healed by startup seeding alone.

    ELIGIBILITY (identical for dry run and apply): a tenant is processed only when it
    is not soft-deleted, not inactive, in an ``ACTIVE`` / ``TRIAL`` lifecycle state,
    provisioned (activation evidence present) and owns a live ``FINANCE_USER`` role.
    Every other tenant is reported once under ``skip_reasons`` and is never written to.

    ``apply=False`` (the default) is a DRY RUN: it reports what would change and writes
    nothing - and it never counts a skipped tenant as needing a change. ``apply=True``
    performs the writes in the caller's transaction; the caller owns the commit.
    Idempotent - a second run reports zero changes.
    """
    permission_code = FINANCE_ONLY_PERMISSIONS[0]
    stmt = (
        select(
            Tenant.tenant_id,
            Tenant.tenant_code,
            Tenant.status,
            Tenant.is_active,
            Tenant.is_deleted,
            Tenant.activation_date,
            Tenant.activated_on,
        )
        .order_by(Tenant.tenant_code)
    )
    if tenant_codes:
        stmt = stmt.where(Tenant.tenant_code.in_(tenant_codes))
    rows = list(db.execute(stmt).all())

    tenant_ids = [row[0] for row in rows]
    finance_tenant_ids: set = set()
    if tenant_ids:
        finance_tenant_ids = set(
            db.scalars(
                select(Role.tenant_id)
                .where(
                    Role.role_code == FINANCE_SUSPEND_ROLE_CODE,
                    Role.tenant_id.in_(tenant_ids),
                    Role.is_deleted.is_(False),
                )
                .distinct()
            ).all()
        )

    # One grouped read instead of one query per tenant; dry run only, since the apply
    # path reads the post-condition from the per-tenant summary.
    holders_by_tenant: dict = {}
    if rows and not apply:
        for holder_tenant_id, role_code in db.execute(
            select(Role.tenant_id, Role.role_code)
            .join(RolePermission, RolePermission.role_id == Role.role_id)
            .join(Permission, Permission.permission_id == RolePermission.permission_id)
            .where(
                Permission.permission_code == permission_code,
                Role.tenant_id.in_(tenant_ids),
            )
        ).all():
            holders_by_tenant.setdefault(holder_tenant_id, set()).add(role_code)

    results: list[dict] = []
    changed = 0
    eligible = 0
    skipped = 0
    skip_reasons: dict[str, int] = {}

    for (
        tenant_id,
        tenant_code,
        status,
        is_active,
        is_deleted,
        activation_date,
        activated_on,
    ) in rows:
        has_finance_role = tenant_id in finance_tenant_ids
        skip_reason = _tenant_sync_skip_reason(
            status=status,
            is_active=is_active,
            is_deleted=is_deleted,
            activation_date=activation_date,
            activated_on=activated_on,
            finance_role_present=has_finance_role,
        )

        summary: dict | None = None
        if skip_reason is None and apply:
            summary = sync_crm_finance_only_matrix(db, tenant_id)
            # Defensive: the matrix re-checks the keeper role. If it changed since the
            # eligibility read, report the tenant as skipped rather than as changed.
            if summary["skipped"]:
                skip_reason = summary["skip_reason"]

        if skip_reason is not None:
            skipped += 1
            skip_reasons[skip_reason] = skip_reasons.get(skip_reason, 0) + 1
            entry = _finance_only_skipped_result(
                tenant_id,
                skip_reason,
                finance_role_present=has_finance_role,
            )
            entry["tenant_code"] = tenant_code
            entry["status"] = status
            entry["needs_change"] = False
            results.append(entry)
            continue

        eligible += 1

        if apply and summary is not None:
            summary["tenant_code"] = tenant_code
            summary["status"] = status
            summary["needs_change"] = bool(
                summary["granted"]
                or summary["revoked"]
                or summary["permission_created"]
            )
            if summary["needs_change"]:
                changed += 1
            results.append(summary)
            continue

        holders = holders_by_tenant.get(tenant_id, set())
        extra = sorted(holders - {FINANCE_SUSPEND_ROLE_CODE})
        needs_change = bool(extra) or (FINANCE_SUSPEND_ROLE_CODE not in holders)
        if needs_change:
            changed += 1
        results.append(
            {
                "tenant_id": str(tenant_id),
                "tenant_code": tenant_code,
                "status": status,
                "holders": sorted(holders),
                "extra_holders": extra,
                "needs_change": needs_change,
                "skipped": False,
                "skip_reason": None,
                "ok": holders == {FINANCE_SUSPEND_ROLE_CODE},
            }
        )

    return {
        "apply": apply,
        "tenants_scanned": len(rows),
        "tenants_eligible": eligible,
        "tenants_changed": changed,
        "tenants_skipped": skipped,
        "skip_reasons": skip_reasons,
        "results": results,
    }


def _grant_role_permissions(
    db: Session, tenant_id, role_code: str, perm_codes: tuple[str, ...]
) -> None:
    role = db.scalars(
        select(Role).where(Role.tenant_id == tenant_id, Role.role_code == role_code)
    ).first()
    if role is None:
        return
    for pcode in perm_codes:
        perm = db.scalars(
            select(Permission).where(Permission.permission_code == pcode)
        ).first()
        if perm is None:
            continue
        linked = db.scalars(
            select(RolePermission).where(
                RolePermission.role_id == role.role_id,
                RolePermission.permission_id == perm.permission_id,
            )
        ).first()
        if linked is None:
            db.add(
                RolePermission(
                    role_id=role.role_id,
                    permission_id=perm.permission_id,
                )
            )
            db.flush()


def provision_tenant_roles(db: Session, tenant_id) -> None:
    """Idempotent system roles + permission grants when a tenant is activated."""
    for code, name, module in PERMISSIONS:
        exists = db.scalars(
            select(Permission).where(Permission.permission_code == code)
        ).first()
        if not exists:
            db.add(
                Permission(
                    permission_code=code, permission_name=name, module_code=module
                )
            )
    db.flush()

    for code, name, is_system in ROLES:
        exists = db.scalars(
            select(Role).where(Role.tenant_id == tenant_id, Role.role_code == code)
        ).first()
        if exists is None:
            db.add(
                Role(
                    tenant_id=tenant_id,
                    role_code=code,
                    role_name=name,
                    description=f"System role: {name}",
                    is_system=is_system,
                )
            )
    db.flush()

    all_codes = _exclude_finance_only(tuple(code for code, _, _ in PERMISSIONS))
    for role_code in ("TENANT_ADMIN", "PLATFORM_ADMIN"):
        _grant_role_permissions(db, tenant_id, role_code, all_codes)
    _grant_role_permissions(db, tenant_id, "SALES_EXECUTIVE", CRM_SALES_EXEC_PERMS)
    _grant_role_permissions(db, tenant_id, "SALES_MANAGER", CRM_SALES_MANAGER_PERMS)
    # BR-CRM-047: Finance User is the only role granted ``customer.suspend``.
    _grant_role_permissions(db, tenant_id, "FINANCE_USER", FINANCE_ONLY_PERMISSIONS)
    # PF-004 organization grants per BFS-PF-004 §12 (HD-01 correction).
    _sync_org_permission_matrix(db, tenant_id)
    # PF-005 branch grants per BFS-PF-005 §12 (groundwork; no runtime grain enforcement).
    _sync_branch_permission_matrix(db, tenant_id)
    # PF-006 department grants per BFS-PF-006 §12 (groundwork; no runtime grain enforcement).
    _sync_department_permission_matrix(db, tenant_id)
    # PF-007 business-unit grants per BFS-PF-007 §12 (groundwork; no runtime grain enforcement).
    _sync_business_unit_permission_matrix(db, tenant_id)
    # PF-008 user/identity grants per BFS-PF-008 §12 (groundwork; no runtime grain enforcement).
    _sync_user_permission_matrix(db, tenant_id)
    # PF-011 settings/platform-settings grants per BFS-PF-011 §12 (scoped; no universal grant).
    _sync_settings_permission_matrix(db, tenant_id)


def _upgrade_sal_permissions(db: Session, tenant: Tenant) -> None:
    """Idempotent backfill of SAL quotation permissions on re-seed."""
    sal_perm_codes = tuple(
        code for code, _, module in PERMISSIONS if module == "SAL"
    )
    for code, name, module in PERMISSIONS:
        if module != "SAL":
            continue
        exists = db.scalars(
            select(Permission).where(Permission.permission_code == code)
        ).first()
        if not exists:
            db.add(
                Permission(
                    permission_code=code, permission_name=name, module_code=module
                )
            )
    db.flush()
    _grant_role_permissions(db, tenant.tenant_id, "SALES_EXECUTIVE", CRM_SALES_EXEC_PERMS)
    _grant_role_permissions(db, tenant.tenant_id, "SALES_MANAGER", CRM_SALES_MANAGER_PERMS)
    for role_code in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        _grant_role_permissions(db, tenant.tenant_id, role_code, sal_perm_codes)


def _upgrade_crm_permissions(db: Session, tenant: Tenant) -> None:
    """Idempotent backfill of CRM permissions and edition features on re-seed."""
    for code, name, module in PERMISSIONS:
        if not code.split(".", 1)[0] in {"lead", "customer", "activity", "opportunity"}:
            continue
        exists = db.scalars(
            select(Permission).where(Permission.permission_code == code)
        ).first()
        if not exists:
            db.add(
                Permission(
                    permission_code=code, permission_name=name, module_code=module
                )
            )
    db.flush()
    crm_perm_codes = _exclude_finance_only(
        tuple(
            code
            for code, _, _ in PERMISSIONS
            if code.split(".", 1)[0] in {"lead", "customer", "activity", "opportunity"}
        )
    )
    _grant_role_permissions(db, tenant.tenant_id, "SALES_EXECUTIVE", CRM_SALES_EXEC_PERMS)
    _grant_role_permissions(db, tenant.tenant_id, "SALES_MANAGER", CRM_SALES_MANAGER_PERMS)
    # BR-CRM-047: Finance User is the only role granted ``customer.suspend``.
    _grant_role_permissions(
        db, tenant.tenant_id, "FINANCE_USER", FINANCE_ONLY_PERMISSIONS
    )
    for role_code in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        _grant_role_permissions(db, tenant.tenant_id, role_code, crm_perm_codes)
    # Heal tenants provisioned before ``customer.suspend`` became Finance-only: revoke it
    # from every other role in THIS tenant. Scoped to this one permission and this one
    # tenant, so no unrelated grant is affected. Never revoke when the keeper role is
    # absent - that would leave the tenant with no holder of the grain at all.
    if _finance_role_present(db, tenant.tenant_id):
        _revoke_permission_from_other_roles(
            db, tenant.tenant_id, "customer.suspend", ("FINANCE_USER",)
        )


def _upgrade_rbac_permissions(db: Session, tenant: Tenant) -> None:
    """Idempotent PF-009 backfill for already-provisioned tenants (re-seed path).

    ``provision_tenant_roles`` only runs on tenant activation, so a tenant created
    before PF-009 would otherwise never receive the ``role.*`` / ``permission.*``
    catalogue rows, the authoritative BFS-PF-009 §3 system roles, or their RBAC
    grants. This mirrors the established ``_upgrade_crm_permissions`` /
    ``_upgrade_sal_permissions`` pattern.

    Only the RBAC catalogue is granted (to PLATFORM_ADMIN + TENANT_ADMIN, matching
    the generic provisioning convention). No role receives a ``department.*`` /
    ``branch.*`` grain here and no universal PLATFORM_ADMIN bypass is introduced.
    """
    prefixes = {"role", "permission"}
    for code, name, module in PERMISSIONS:
        if code.split(".", 1)[0] not in prefixes:
            continue
        exists = db.scalars(
            select(Permission).where(Permission.permission_code == code)
        ).first()
        if not exists:
            db.add(
                Permission(
                    permission_code=code, permission_name=name, module_code=module
                )
            )
    db.flush()

    for code, name, is_system in ROLES:
        exists = db.scalars(
            select(Role).where(
                Role.tenant_id == tenant.tenant_id, Role.role_code == code
            )
        ).first()
        if exists is None:
            db.add(
                Role(
                    tenant_id=tenant.tenant_id,
                    role_code=code,
                    role_name=name,
                    description=f"System role: {name}",
                    is_system=is_system,
                )
            )
    db.flush()

    rbac_codes = tuple(
        code for code, _, _ in PERMISSIONS if code.split(".", 1)[0] in prefixes
    )
    for role_code in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        _grant_role_permissions(db, tenant.tenant_id, role_code, rbac_codes)


def _ensure_tenant_branding(db: Session, tenant: Tenant) -> None:
    row = db.scalars(
        select(TenantBranding).where(TenantBranding.tenant_id == tenant.tenant_id)
    ).first()
    if row is None:
        db.add(
            TenantBranding(
                tenant_id=tenant.tenant_id,
                logo_url=_SEED_LOGO_JPEG,
                primary_color="#1565C0",
                secondary_color="#424242",
            )
        )
        return
    if not row.logo_url:
        row.logo_url = _SEED_LOGO_JPEG


def _sync_pf_module_matrices(db: Session, tenant_id) -> None:
    """Bring a tenant's role grants in line with the approved PF-004..PF-008 matrices.

    PF-009 Batch 2: the seeded matrix is authoritative and runtime permission-grain
    enforcement is active, so every tenant must carry the approved grains (the platform
    tenant already does).

    ``branch.*`` and ``business_unit.*`` are additionally edition-gated, mirroring the
    runtime feature gates (``app.core.edition_gating``): a tenant whose edition does not
    carry ``BRANCH`` / ``BUSINESS_UNIT`` must not hold those grains, otherwise the role
    gate would pass and the edition gate would be the one to deny.
    """
    _sync_org_permission_matrix(db, tenant_id)
    if has_feature(db, tenant_id, BRANCH):
        _sync_branch_permission_matrix(db, tenant_id)
    _sync_department_permission_matrix(db, tenant_id)
    if has_feature(db, tenant_id, BUSINESS_UNIT):
        _sync_business_unit_permission_matrix(db, tenant_id)
    _sync_user_permission_matrix(db, tenant_id)
    _sync_settings_permission_matrix(db, tenant_id)
    # BR-CRM-047 / REQ-CRM-028: every tenant that is synchronised also gets
    # ``customer.suspend`` corrected to FINANCE_USER-only, so COMU001 (the only other
    # tenant seeded at startup) is healed without a separate backfill.
    sync_crm_finance_only_matrix(db, tenant_id)


def _ensure_community_demo_tenant(db: Session, editions: dict[str, Edition]) -> None:
    """Idempotent Community-edition tenant for manual smoke tests."""
    settings = get_settings()
    existing = db.scalars(select(Tenant).where(Tenant.tenant_code == "COMU001")).first()
    if existing:
        _grant_role_permissions(db, existing.tenant_id, "SALES_EXECUTIVE", CRM_COMMUNITY_PERMS)
        _sync_pf_module_matrices(db, existing.tenant_id)
        return
    community = editions["COMMUNITY"]
    tenant = Tenant(
        tenant_code="COMU001",
        tenant_name="Community Demo",
        legal_name="Community Demo Org",
        edition_id=community.id,
        organization_type="Pvt Ltd",
        email="community@euphoriainfotech.com",
        mobile="+919876543211",
        status="ACTIVE",
        activation_date=date.today(),
    )
    db.add(tenant)
    db.flush()
    org = Organization(
        tenant_id=tenant.tenant_id,
        organization_code="HO001",
        organization_name="Community HQ",
        legal_name="Community Demo Org",
        organization_type="ROOT",
        email="ho@community-demo.com",
        phone="+913340000001",
        status="ACTIVE",
        is_root=True,
        level=0,
        default_currency_code="INR",
        fiscal_year_start_month=4,
    )
    db.add(org)
    db.flush()
    db.add(
        TenantSettings(
            tenant_id=tenant.tenant_id,
            financial_year_start=date(date.today().year, 4, 1),
            currency_code="INR",
            time_zone="Asia/Kolkata",
            date_format="DD/MM/YYYY",
            default_language="en",
        )
    )
    db.add(
        Subscription(
            tenant_id=tenant.tenant_id,
            edition_id=community.id,
            subscription_number="SUB-COMU-000001",
            plan_type="Yearly",
            start_date=date.today(),
            end_date=date.today() + timedelta(days=365),
            amount="0",
            currency_code="INR",
            payment_status="PAID",
            subscription_status="ACTIVE",
        )
    )
    role = Role(
        tenant_id=tenant.tenant_id,
        role_code="SALES_EXECUTIVE",
        role_name="Sales Executive",
        description="Community demo sales role",
        is_system=True,
    )
    db.add(role)
    db.flush()
    for code in CRM_COMMUNITY_PERMS:
        perm = db.scalars(select(Permission).where(Permission.permission_code == code)).first()
        if perm:
            _link_role_permission(db, role.role_id, perm.permission_id)
    db.add(
        User(
            tenant_id=tenant.tenant_id,
            organization_id=org.organization_id,
            role_id=role.role_id,
            employee_code="COMU0001",
            first_name="Community",
            last_name="User",
            display_name="Community Demo User",
            email="community@euphoriainfotech.com",
            mobile="+919876543211",
            password_hash=hash_password("Community@12345"),
            account_status="ACTIVE",
        )
    )
    _sync_pf_module_matrices(db, tenant.tenant_id)
