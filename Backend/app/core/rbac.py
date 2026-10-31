"""CRM RBAC helpers.

``has_permission`` is the single permission-grain decision point. PF-009 Batch 2 removed
the PLATFORM_ADMIN universal bypass, so the seeded matrix is authoritative for all roles.
"""

from app.core.deps import CurrentUser
from app.core.exceptions import ForbiddenError

SALES_ROLES = frozenset(
    {"SALES_EXECUTIVE", "SALES_MANAGER", "TENANT_ADMIN", "PLATFORM_ADMIN"}
)
SALES_MANAGER_ROLES = frozenset(
    {"SALES_MANAGER", "TENANT_ADMIN", "PLATFORM_ADMIN"}
)


def has_permission(current: CurrentUser, code: str) -> bool:
    """Permission-grain decision from the seeded matrix (PF-009 Batch 2).

    The seeded role-permission matrix is authoritative for every role, including
    PLATFORM_ADMIN: the per-module matrices in ``app/db/seed.py`` carry the approved
    BFS §12 grains (Platform Admin holds e.g. ``organization.read`` / ``branch.read``
    only, and no ``department.*`` / ``business_unit.*`` grain).
    """
    return code in current.permissions


def require_permission(current: CurrentUser, code: str) -> None:
    if not has_permission(current, code):
        raise ForbiddenError(f"Permission '{code}' required", req_id="REQ-CRM-RBAC")


# BR-CRM-047: credit-classification and suspension are Finance User only.
CUSTOMER_SUSPEND_ROLES = frozenset({"FINANCE_USER"})


def require_customer_suspend(current: CurrentUser) -> None:
    """REQ-CRM-028 / BR-CRM-047: suspension needs ``customer.suspend`` AND Finance User.

    The explicit role gate is deliberate. Generic tenant provisioning hands the whole
    permission catalogue to TENANT_ADMIN / PLATFORM_ADMIN, so requiring the permission
    alone would not make suspension Finance-only. Mirrors the existing convention in
    ``organization_service`` / ``user_service`` (explicit role gate over a grain).
    """
    require_permission(current, "customer.suspend")
    if current.role_code not in CUSTOMER_SUSPEND_ROLES:
        raise ForbiddenError(
            "Customer suspension is Finance User only (BR-CRM-047)",
            req_id="REQ-CRM-028",
        )


def require_sales(current: CurrentUser) -> None:
    if current.role_code not in SALES_ROLES:
        raise ForbiddenError("Sales role required", req_id="REQ-CRM-RBAC")


def require_sales_manager(current: CurrentUser) -> None:
    if not has_permission(current, "opportunity.approve"):
        if current.role_code not in SALES_MANAGER_ROLES:
            raise ForbiddenError(
                "Sales Manager approval required", req_id="REQ-CRM-RBAC"
            )


def can_close_won(current: CurrentUser) -> bool:
    return has_permission(current, "opportunity.approve") or (
        current.role_code in SALES_MANAGER_ROLES
    )


def can_view_pipeline(current: CurrentUser) -> bool:
    return has_permission(current, "opportunity.read") and (
        has_permission(current, "opportunity.approve")
        or current.role_code in SALES_MANAGER_ROLES
    )


def can_create_lead(current: CurrentUser) -> bool:
    return has_permission(current, "lead.create")


def can_create_activity(current: CurrentUser) -> bool:
    return has_permission(current, "activity.create")
