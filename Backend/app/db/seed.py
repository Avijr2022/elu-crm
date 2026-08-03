from datetime import date, timedelta

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.pf import (
    Edition,
    Organization,
    Permission,
    Role,
    RolePermission,
    Subscription,
    Tenant,
    TenantSettings,
    User,
)


PERMISSIONS = [
    ("tenant.read", "View tenant", "PF"),
    ("tenant.update", "Update tenant", "PF"),
    ("user.create", "Create user", "PF"),
    ("user.read", "View user", "PF"),
    ("user.update", "Update user", "PF"),
    ("role.assign", "Assign roles", "PF"),
    ("lead.create", "Create lead", "CRM"),
    ("lead.read", "View lead", "CRM"),
    ("lead.update", "Update lead", "CRM"),
    ("lead.convert", "Convert lead", "CRM"),
]

ROLES = [
    ("TENANT_ADMIN", "Tenant Admin", True),
    ("SALES_EXECUTIVE", "Sales Executive", True),
    ("SALES_MANAGER", "Sales Manager", True),
    ("PROJECT_MANAGER", "Project Manager", True),
    ("FINANCE_USER", "Finance User", True),
]


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


def seed_platform(db: Session) -> None:
    settings = get_settings()
    ensure_schemas(db)

    existing = db.scalars(
        select(Tenant).where(Tenant.tenant_code == "EIIP001")
    ).first()
    if existing:
        return

    editions = [
        Edition(
            edition_code="COMMUNITY",
            edition_name="Community Edition",
            description="Learning & demo",
            max_users=5,
        ),
        Edition(
            edition_code="PROFESSIONAL",
            edition_name="Professional Edition",
            description="SME full CRM/ERP suite",
            max_users=100,
        ),
        Edition(
            edition_code="ENTERPRISE",
            edition_name="Enterprise Edition",
            description="Large enterprise SaaS",
            max_users=None,
        ),
    ]
    db.add_all(editions)
    db.flush()

    professional = next(e for e in editions if e.edition_code == "PROFESSIONAL")

    tenant = Tenant(
        tenant_code="EIIP001",
        tenant_name="Euphoria",
        legal_name="Euphoria Infotech (I) Limited",
        edition_id=professional.edition_id,
        organization_type="Pvt Ltd",
        gstin="19AABCE1234F1Z5",
        pan="AABCE1234F",
        website="https://www.euphoriainfotech.com",
        email="admin@euphoria.local",
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
        organization_type="Head Office",
        email="ho@euphoria.local",
        phone="+913340000000",
        status="ACTIVE",
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

    db.add(
        Subscription(
            tenant_id=tenant.tenant_id,
            edition_id=professional.edition_id,
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

    # Tenant Admin gets all permissions
    for perm in perm_map.values():
        db.add(
            RolePermission(
                role_id=role_map["TENANT_ADMIN"].role_id,
                permission_id=perm.permission_id,
            )
        )
    for code in ("lead.create", "lead.read", "lead.update"):
        db.add(
            RolePermission(
                role_id=role_map["SALES_EXECUTIVE"].role_id,
                permission_id=perm_map[code].permission_id,
            )
        )
    for code in ("lead.create", "lead.read", "lead.update", "lead.convert"):
        db.add(
            RolePermission(
                role_id=role_map["SALES_MANAGER"].role_id,
                permission_id=perm_map[code].permission_id,
            )
        )

    admin = User(
        tenant_id=tenant.tenant_id,
        organization_id=org.organization_id,
        role_id=role_map["TENANT_ADMIN"].role_id,
        employee_code="EMP000001",
        first_name="Euphoria",
        last_name="Admin",
        display_name="Euphoria Admin",
        email=settings.seed_admin_email.lower(),
        mobile="+919876543210",
        password_hash=hash_password(settings.seed_admin_password),
        designation="Tenant Administrator",
        account_status="ACTIVE",
    )
    db.add(admin)
    db.commit()
