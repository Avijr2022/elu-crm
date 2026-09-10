from app.core.deps import CurrentUser
from app.core.exceptions import ForbiddenError

SALES_ROLES = frozenset(
    {"SALES_EXECUTIVE", "SALES_MANAGER", "TENANT_ADMIN", "PLATFORM_ADMIN"}
)
SALES_MANAGER_ROLES = frozenset(
    {"SALES_MANAGER", "TENANT_ADMIN", "PLATFORM_ADMIN"}
)


def has_permission(current: CurrentUser, code: str) -> bool:
    if current.role_code == "PLATFORM_ADMIN":
        return True
    return code in current.permissions


def require_permission(current: CurrentUser, code: str) -> None:
    if not has_permission(current, code):
        raise ForbiddenError(f"Permission '{code}' required", req_id="REQ-CRM-RBAC")


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
