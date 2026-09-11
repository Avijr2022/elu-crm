from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import delete, select, text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.core.config import get_settings
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
    ("role.assign", "Assign roles", "PF"),
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
    ("lead.create", "Create lead", "CRM"),
    ("lead.read", "View lead", "CRM"),
    ("lead.update", "Update lead", "CRM"),
    ("lead.convert", "Convert lead", "CRM"),
    ("lead.qualify", "Qualify lead", "CRM"),
    ("lead.disqualify", "Disqualify lead", "CRM"),
    ("customer.read", "View customer", "CRM"),
    ("customer.create", "Create customer", "CRM"),
    ("customer.update", "Update customer", "CRM"),
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

    all_codes = tuple(code for code, _, _ in PERMISSIONS)
    for role_code in ("TENANT_ADMIN", "PLATFORM_ADMIN"):
        _grant_role_permissions(db, tenant_id, role_code, all_codes)
    _grant_role_permissions(db, tenant_id, "SALES_EXECUTIVE", CRM_SALES_EXEC_PERMS)
    _grant_role_permissions(db, tenant_id, "SALES_MANAGER", CRM_SALES_MANAGER_PERMS)
    # PF-004 organization grants per BFS-PF-004 §12 (HD-01 correction).
    _sync_org_permission_matrix(db, tenant_id)


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
    crm_perm_codes = tuple(
        code
        for code, _, _ in PERMISSIONS
        if code.split(".", 1)[0] in {"lead", "customer", "activity", "opportunity"}
    )
    _grant_role_permissions(db, tenant.tenant_id, "SALES_EXECUTIVE", CRM_SALES_EXEC_PERMS)
    _grant_role_permissions(db, tenant.tenant_id, "SALES_MANAGER", CRM_SALES_MANAGER_PERMS)
    for role_code in ("PLATFORM_ADMIN", "TENANT_ADMIN"):
        _grant_role_permissions(db, tenant.tenant_id, role_code, crm_perm_codes)


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


def _ensure_community_demo_tenant(db: Session, editions: dict[str, Edition]) -> None:
    """Idempotent Community-edition tenant for manual smoke tests."""
    settings = get_settings()
    existing = db.scalars(select(Tenant).where(Tenant.tenant_code == "COMU001")).first()
    if existing:
        _grant_role_permissions(db, existing.tenant_id, "SALES_EXECUTIVE", CRM_COMMUNITY_PERMS)
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
