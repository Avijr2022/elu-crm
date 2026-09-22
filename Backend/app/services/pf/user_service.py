"""PF-008 User & Identity Management CORE service (ELU-BFS-PF-008).

Implementation map and recorded decisions: ``Documentation/PF008_CORE_IMPLEMENTATION_MAP.md``
(D1..D13). In scope: user profile CRUD + tenant-scoped directory, invitation/activation with
72-hour expiry, account lifecycle (`INVITED`/`ACTIVE`/`INACTIVE`/`LOCKED`/`EXPIRED`/`CANCELLED`),
seat enforcement (`BR-PF-052`), password reset/change challenges, and tenant-scoped linkage to
the released PF-005 branch / PF-006 department / PF-007 business-unit structures.

Deferred (per authorization): MFA (`BR-PF-058`), `NTF-PF-008-*` notifications,
`RPT-PF-008-*` reports, the `JOB-PF-008-01` scheduler (expiry/lock release are evaluated
lazily — D6/D7), SSO, SCIM and any PF-009 RBAC redesign.

`tenant_id` is always supplied by the caller from the authenticated context
(`CurrentUser.tenant_id`) and is never read from a request body (`BR-PF-059` / ADR-015).
"""

from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.core.security import generate_opaque_token, hash_password, hash_token
from app.models.pf import (
    Branch,
    BusinessUnit,
    Department,
    Organization,
    Subscription,
    Tenant,
    User,
    UserInvite,
)
from app.repositories.pf.user_repository import (
    RoleRepository,
    TenantRepository,
    UserInviteRepository,
    UserRepository,
)
from app.schemas.pf.auth import PasswordActionResponse
from app.schemas.pf.user import (
    PASSWORD_MIN_LENGTH,
    UserCreateResponse,
    UserInviteCreate,
    UserListResponse,
    UserPatch,
    UserResponse,
    UserSelfUpdate,
    UserUpdate,
    normalize_status,
)
from app.services.pf.audit_service import write_audit_event

_REQ = "REQ-PF-008"

# BR-PF-054 invitation validity.
INVITE_TTL_HOURS = 72
# D3/D11 — single-use password-reset challenge lifetime (implementation decision: the
# authoritative specification defines no reset TTL).
RESET_TTL_MINUTES = 60
# BR-PF-055.
LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 30

#: Statuses that occupy a subscription seat (D8, BR-PF-052).
SEAT_HOLDING_STATUSES = ("ACTIVE", "INVITED", "LOCKED")

#: Account lifecycle (`ELU-BFS-PF-008` §5).
ALLOWED_TRANSITIONS: dict[str, frozenset[str]] = {
    "INVITED": frozenset({"ACTIVE", "EXPIRED", "CANCELLED"}),
    "ACTIVE": frozenset({"INACTIVE", "LOCKED"}),
    "INACTIVE": frozenset({"ACTIVE"}),
    "LOCKED": frozenset({"ACTIVE"}),
    "EXPIRED": frozenset({"INVITED"}),
    "CANCELLED": frozenset(),
}

# ---------------------------------------------------------------- role gates
# BFS-PF-008 §12 actor matrix: Tenant Admin and Platform Admin hold create/read/update/
# delete/reset_password. The §12 self-scope of SALES_EXECUTIVE is realised by the
# ``/users/me`` endpoints, not by a list grant. Runtime permission-grain enforcement
# remains PF-009, so an explicit role gate is used (PF-004 HD-02 / PF-005 / PF-006
# convention) because ``app.core.rbac.has_permission`` grants PLATFORM_ADMIN a bypass.
_USER_READ_ROLES = frozenset({"TENANT_ADMIN", "PLATFORM_ADMIN"})
_USER_WRITE_ROLES = frozenset({"TENANT_ADMIN", "PLATFORM_ADMIN"})
_USER_EXPORT_ROLES = frozenset({"TENANT_ADMIN", "PLATFORM_ADMIN"})


def require_user_read(role_code: str) -> None:
    """User read matrix (BFS-PF-008 §12)."""
    if role_code not in _USER_READ_ROLES:
        raise ForbiddenError("User read not permitted", req_id=_REQ)


def require_user_write(role_code: str) -> None:
    """User write matrix (BFS-PF-008 §12)."""
    if role_code not in _USER_WRITE_ROLES:
        raise ForbiddenError("User write not permitted", req_id=_REQ)


def require_user_export(role_code: str) -> None:
    """User export matrix (BFS-PF-008 §12 — ``user.export``)."""
    if role_code not in _USER_EXPORT_ROLES:
        raise ForbiddenError("User export not permitted", req_id=_REQ)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.users = UserRepository(db)
        self.invites = UserInviteRepository(db)
        self.roles = RoleRepository(db)
        self.tenants = TenantRepository(db)

    # ------------------------------------------------------------------ helpers
    def _tenant(self, tenant_id: UUID) -> Tenant:
        tenant = self.tenants.get_by_id(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id=_REQ)
        return tenant

    def _get_user(self, tenant_id: UUID, user_id: UUID) -> User:
        user = self.users.get_by_id(user_id, tenant_id)
        if user is None:
            # Cross-tenant ids are indistinguishable from unknown ids (BR-PF-059).
            raise NotFoundError("User not found", req_id=_REQ)
        return user

    def _resolve_role(self, tenant_id: UUID, role_id: UUID | None, role_code: str | None):
        if role_id is not None:
            role = self.roles.get_by_id(tenant_id, role_id)
            if role is None:
                raise ValidationAppError(
                    "role_id does not belong to this tenant", req_id=_REQ
                )
            return role
        if role_code:
            role = self.roles.get_by_code(tenant_id, role_code)
            if role is None:
                raise ValidationAppError(
                    f"role_code {role_code} does not exist in this tenant", req_id=_REQ
                )
            return role
        raise ValidationAppError(
            "role_code or role_id is required", req_id=_REQ
        )

    def _resolve_organization(self, tenant_id: UUID, organization_id: UUID | None) -> Organization:
        stmt = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.is_deleted.is_(False),
        )
        if organization_id is None:
            stmt = stmt.where(Organization.is_root.is_(True))
        else:
            stmt = stmt.where(Organization.organization_id == organization_id)
        organization = self.db.scalars(stmt).first()
        if organization is None:
            raise ValidationAppError(
                "organization_id does not resolve inside this tenant "
                "(a root organization is created at tenant provisioning)",
                req_id=_REQ,
            )
        return organization

    def _assert_active_reference(
        self,
        model,
        tenant_id: UUID,
        entity_id: UUID | None,
        label: str,
    ) -> None:
        """BR-PF-059 + PF-007 precedent: the referenced structure must be an ACTIVE
        same-tenant, non-deleted row. Mirrors PF-007 ``BR-PF-049`` (inactive business
        unit is not assignable)."""
        if entity_id is None:
            return
        entity = self.db.scalars(
            select(model).where(
                model.tenant_id == tenant_id,
                getattr(model, f"{model.__tablename__}_id") == entity_id,
                model.is_deleted.is_(False),
            )
        ).first()
        if entity is None:
            raise ValidationAppError(
                f"{label} does not belong to this tenant", req_id=_REQ
            )
        if entity.status != "ACTIVE":
            raise ValidationAppError(
                f"{label} is not ACTIVE and cannot be assigned", req_id=_REQ
            )

    def _assert_linkage(
        self,
        tenant_id: UUID,
        *,
        branch_id: UUID | None,
        department_id: UUID | None,
        business_unit_id: UUID | None,
    ) -> None:
        self._assert_active_reference(Branch, tenant_id, branch_id, "branch_id")
        self._assert_active_reference(Department, tenant_id, department_id, "department_id")
        self._assert_active_reference(
            BusinessUnit, tenant_id, business_unit_id, "business_unit_id"
        )

    def _assert_seat_available(self, tenant_id: UUID) -> None:
        """BR-PF-052 — seats are bounded by the current subscription (D8)."""
        tenant = self._tenant(tenant_id)
        subscription = None
        if tenant.current_subscription_id is not None:
            subscription = self.db.get(Subscription, tenant.current_subscription_id)
        if subscription is None:
            subscription = self.db.scalars(
                select(Subscription)
                .where(
                    Subscription.tenant_id == tenant_id,
                    Subscription.is_deleted.is_(False),
                    Subscription.subscription_status.in_(("ACTIVE", "TRIAL")),
                )
                .order_by(Subscription.start_date.desc())
            ).first()
        if subscription is None or subscription.subscription_status not in ("ACTIVE", "TRIAL"):
            raise ValidationAppError(
                "An ACTIVE or TRIAL subscription is required to add users",
                req_id="BR-PF-004",
            )

        used = self.users.active_invite_holder_count(tenant_id)
        if used + 1 > subscription.seat_count:
            raise ValidationAppError(
                f"Seat limit reached: {used} of {subscription.seat_count} seats used",
                req_id="BR-PF-052",
            )

        edition = subscription.edition
        if edition is not None:
            for limit in edition.limits:
                if limit.limit_code.upper() == "MAX_USERS":
                    if used + 1 > int(limit.limit_value):
                        raise ValidationAppError(
                            f"Edition MAX_USERS limit reached ({int(limit.limit_value)})",
                            req_id="BR-PF-021",
                        )
                    break

    def _assert_last_tenant_admin_guard(self, tenant_id: UUID, user: User) -> None:
        """BR-PF-060 — at least one ACTIVE Tenant Admin per tenant at all times."""
        if user.role is None or user.role.role_code != "TENANT_ADMIN":
            return
        if user.account_status != "ACTIVE":
            return
        remaining = self.users.count_by_role_code(tenant_id, "TENANT_ADMIN")
        if remaining <= 1:
            raise ValidationAppError(
                "The last ACTIVE Tenant Admin of the tenant cannot be deactivated",
                req_id="BR-PF-060",
            )

    def _expire_stale_invites(self, user: User) -> bool:
        """D6 — lazy `BR-PF-054` evaluation (no `JOB-PF-008-01` scheduler in CORE)."""
        if user.account_status != "INVITED":
            return False
        invite = self.invites.get_active_for_user(user.user_id)
        if invite is None:
            return False
        if invite.expires_on <= utcnow():
            invite.status = "EXPIRED"
            user.account_status = "EXPIRED"
            self.db.add_all([invite, user])
            self.db.commit()
            return True
        return False

    def _mint_invite(self, tenant_id: UUID, user: User, actor_id: UUID) -> tuple[str, datetime]:
        token = generate_opaque_token()
        expires_on = utcnow() + timedelta(hours=INVITE_TTL_HOURS)
        self.invites.add(
            UserInvite(
                invite_id=uuid4(),
                tenant_id=tenant_id,
                user_id=user.user_id,
                token_hash=hash_token(token),
                status="ACTIVE",
                expires_on=expires_on,
                created_by=actor_id,
            )
        )
        return token, expires_on

    def _to_response(self, user: User) -> UserResponse:
        return UserResponse(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            employee_code=user.employee_code,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            email=user.email,
            mobile=user.mobile,
            designation=user.designation,
            account_status=user.account_status,
            organization_id=user.organization_id,
            organization_name=(
                user.organization.organization_name if user.organization else None
            ),
            role_id=user.role_id,
            role_code=user.role.role_code if user.role else None,
            role_name=user.role.role_name if user.role else None,
            branch_id=user.branch_id,
            department_id=user.department_id,
            business_unit_id=user.business_unit_id,
            invited_at=user.invited_at,
            activated_at=user.activated_at,
            deactivated_at=user.deactivated_at,
            last_login=user.last_login,
            created_on=user.created_on,
            modified_on=user.modified_on,
            version_no=user.version_no,
        )

    # ------------------------------------------------------------------- queries
    def list_users(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        role_id: UUID | None = None,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        business_unit_id: UUID | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> UserListResponse:
        normalized_status = normalize_status(status) if status else None
        items, total = self.users.list_users(
            tenant_id,
            page=page,
            page_size=page_size,
            status=normalized_status,
            role_id=role_id,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
            sort=sort,
        )
        return UserListResponse(
            items=[self._to_response(user) for user in items],
            page=page,
            page_size=page_size,
            total=total,
        )

    def export_rows(
        self,
        tenant_id: UUID,
        *,
        status: str | None = None,
        role_id: UUID | None = None,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        business_unit_id: UUID | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> list[dict]:
        rows = self.users.list_for_export(
            tenant_id,
            status=normalize_status(status) if status else None,
            role_id=role_id,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
            sort=sort,
        )
        return [
            {
                "user_id": str(user.user_id),
                "employee_code": user.employee_code,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "display_name": user.display_name,
                "account_status": user.account_status,
                "role_code": user.role.role_code if user.role else None,
                "organization_name": (
                    user.organization.organization_name if user.organization else None
                ),
                "branch_id": str(user.branch_id) if user.branch_id else None,
                "department_id": str(user.department_id) if user.department_id else None,
                "business_unit_id": (
                    str(user.business_unit_id) if user.business_unit_id else None
                ),
                "last_login": user.last_login.isoformat() if user.last_login else None,
            }
            for user in rows
        ]

    def get_user(self, tenant_id: UUID, user_id: UUID) -> UserResponse:
        user = self._get_user(tenant_id, user_id)
        self._expire_stale_invites(user)
        self.db.refresh(user)
        return self._to_response(user)

    def self_profile(self, tenant_id: UUID, user_id: UUID) -> UserResponse:
        return self.get_user(tenant_id, user_id)

    # ------------------------------------------------------------------ commands
    def invite_or_create(
        self, tenant_id: UUID, payload: UserInviteCreate, actor_id: UUID
    ) -> UserCreateResponse:
        """POST /users — invite (INVITED + 72 h token) or create (ACTIVE + password)."""
        email = str(payload.email).lower()
        if self.users.email_exists(tenant_id, email):
            raise ConflictError(
                "email already exists in this tenant", req_id="BR-PF-051"
            )
        role = self._resolve_role(tenant_id, payload.role_id, payload.role_code)
        organization = self._resolve_organization(tenant_id, payload.organization_id)
        self._assert_linkage(
            tenant_id,
            branch_id=payload.branch_id,
            department_id=payload.department_id,
            business_unit_id=payload.business_unit_id,
        )
        self._assert_seat_available(tenant_id)

        now = utcnow()
        invite_mode = payload.password is None
        display_name = payload.display_name or " ".join(
            part for part in (payload.first_name, payload.last_name) if part
        )
        user = User(
            user_id=uuid4(),
            tenant_id=tenant_id,
            organization_id=organization.organization_id,
            role_id=role.role_id,
            employee_code=payload.employee_code,
            first_name=payload.first_name,
            last_name=payload.last_name,
            display_name=display_name,
            email=email,
            mobile=payload.mobile,
            # An invited user has no usable credential until activation; a random
            # secret is stored so no account can be authenticated by accident (D5).
            password_hash=hash_password(payload.password or generate_opaque_token()),
            designation=payload.designation,
            account_status="INVITED" if invite_mode else "ACTIVE",
            branch_id=payload.branch_id,
            department_id=payload.department_id,
            business_unit_id=payload.business_unit_id,
            invited_at=now if invite_mode else None,
            activated_at=None if invite_mode else now,
            password_changed_at=None if invite_mode else now,
        )
        self.db.add(user)
        self.db.flush()

        token: str | None = None
        expires_on: datetime | None = None
        if invite_mode:
            token, expires_on = self._mint_invite(tenant_id, user, actor_id)

        write_audit_event(
            self.db,
            event_type="USER_INVITED" if invite_mode else "USER_CREATED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "email": user.email,
                "role_code": role.role_code,
                "account_status": user.account_status,
                "status": "INVITED" if invite_mode else "ACTIVE",
            },
        )
        self.db.commit()
        self.db.refresh(user)
        response = UserCreateResponse(
            **self._to_response(user).model_dump(),
            invite_token=token,
            invite_expires_on=expires_on,
        )
        return response

    def update_user(
        self, tenant_id: UUID, user_id: UUID, payload: UserUpdate, actor_id: UUID
    ) -> UserResponse:
        """PUT /users/{id} — full profile update (optimistic locking via version_no)."""
        user = self._get_user(tenant_id, user_id)
        if payload.version_no != user.version_no:
            raise ConflictError(
                "Stale version_no; reload the user and retry", req_id=_REQ
            )
        if payload.email is not None and str(payload.email).lower() != user.email:
            if self.users.email_exists(tenant_id, str(payload.email).lower(), user.user_id):
                raise ConflictError(
                    "email already exists in this tenant", req_id="BR-PF-051"
                )
            user.email = str(payload.email).lower()

        # PUT semantics (D14): a role/organization that is omitted keeps its current value —
        # an omission must never silently re-scope or re-privilege an account.
        if payload.role_id is not None or payload.role_code is not None:
            role = self._resolve_role(tenant_id, payload.role_id, payload.role_code)
            if (
                role.role_code != "TENANT_ADMIN"
                and user.role
                and user.role.role_code == "TENANT_ADMIN"
            ):
                self._assert_last_tenant_admin_guard(tenant_id, user)
            user.role_id = role.role_id
        self._assert_linkage(
            tenant_id,
            branch_id=payload.branch_id,
            department_id=payload.department_id,
            business_unit_id=payload.business_unit_id,
        )
        if payload.organization_id is not None:
            user.organization_id = self._resolve_organization(
                tenant_id, payload.organization_id
            ).organization_id

        user.first_name = payload.first_name
        user.last_name = payload.last_name
        user.display_name = payload.display_name or " ".join(
            part for part in (payload.first_name, payload.last_name) if part
        )
        user.employee_code = payload.employee_code
        user.mobile = payload.mobile
        user.designation = payload.designation
        user.branch_id = payload.branch_id
        user.department_id = payload.department_id
        user.business_unit_id = payload.business_unit_id
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_UPDATED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "email": user.email,
                "role_code": user.role.role_code if user.role else None,
            },
        )
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)

    def patch_user(
        self, tenant_id: UUID, user_id: UUID, payload: UserPatch, actor_id: UUID
    ) -> UserResponse:
        """PATCH /users/{id} — partial update incl. validated lifecycle transitions."""
        user = self._get_user(tenant_id, user_id)
        if payload.version_no != user.version_no:
            raise ConflictError(
                "Stale version_no; reload the user and retry", req_id=_REQ
            )

        if payload.role_id is not None or payload.role_code is not None:
            role = self._resolve_role(tenant_id, payload.role_id, payload.role_code)
            if role.role_code != "TENANT_ADMIN":
                self._assert_last_tenant_admin_guard(tenant_id, user)
            user.role_id = role.role_id
        if payload.organization_id is not None:
            user.organization_id = self._resolve_organization(
                tenant_id, payload.organization_id
            ).organization_id
        provided = payload.model_fields_set
        if {"branch_id", "department_id", "business_unit_id"} & provided:
            self._assert_linkage(
                tenant_id,
                branch_id=payload.branch_id,
                department_id=payload.department_id,
                business_unit_id=payload.business_unit_id,
            )
            if "branch_id" in provided:
                user.branch_id = payload.branch_id
            if "department_id" in provided:
                user.department_id = payload.department_id
            if "business_unit_id" in provided:
                user.business_unit_id = payload.business_unit_id

        for field in ("first_name", "last_name", "employee_code", "mobile", "designation"):
            value = getattr(payload, field)
            if value is not None:
                setattr(user, field, value)
        if payload.display_name is not None:
            user.display_name = payload.display_name
        elif payload.first_name is not None or payload.last_name is not None:
            user.display_name = " ".join(
                part
                for part in (user.first_name, user.last_name)
                if part
            )

        if payload.account_status is not None and payload.account_status != user.account_status:
            self._apply_transition(tenant_id, user, payload.account_status, actor_id)

        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_UPDATED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"account_status": user.account_status},
        )
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)

    def _apply_transition(
        self, tenant_id: UUID, user: User, target: str, actor_id: UUID
    ) -> None:
        allowed = ALLOWED_TRANSITIONS.get(user.account_status, frozenset())
        if target not in allowed:
            raise ValidationAppError(
                f"Illegal account status transition {user.account_status} -> {target}",
                req_id=_REQ,
            )
        now = utcnow()
        if target in SEAT_HOLDING_STATUSES and user.account_status not in SEAT_HOLDING_STATUSES:
            self._assert_seat_available(tenant_id)
        if user.account_status == "ACTIVE" and target in {"INACTIVE", "LOCKED"}:
            self._assert_last_tenant_admin_guard(tenant_id, user)
        if target == "INACTIVE":
            user.deactivated_at = now
            user.sessions_invalid_before = now
            user.is_active = False
            invite = self.invites.get_active_for_user(user.user_id)
            if invite is not None:
                invite.status = "CANCELLED"
                self.db.add(invite)
        elif target == "ACTIVE":
            user.activated_at = user.activated_at or now
            user.is_active = True
            user.deactivated_at = None
            user.failed_login_count = 0
            user.locked_until = None
        elif target == "LOCKED":
            user.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        elif target in {"EXPIRED", "CANCELLED"}:
            invite = self.invites.get_active_for_user(user.user_id)
            if invite is not None:
                invite.status = target
                self.db.add(invite)
        elif target == "INVITED":
            user.invited_at = now
        user.account_status = target
        write_audit_event(
            self.db,
            event_type=f"USER_{target}",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"account_status": target},
        )

    def deactivate(self, tenant_id: UUID, user_id: UUID, actor_id: UUID) -> UserResponse:
        """DELETE /users/{id} — BFS-PF-008 §10 defines DELETE as *deactivate*.

        The row is retained (no soft delete): ``account_status = INACTIVE``,
        ``is_active = False``, refresh sessions invalidated (`BR-PF-057`).
        """
        user = self._get_user(tenant_id, user_id)
        if user.account_status != "INACTIVE":
            self._apply_transition(tenant_id, user, "INACTIVE", actor_id)
            user.version_no += 1
            self.db.add(user)
            write_audit_event(
                self.db,
                event_type="USER_DEACTIVATED",
                event_category="USER",
                entity_type="user",
                entity_id=user.user_id,
                actor_id=actor_id,
                tenant_id=tenant_id,
                payload={"account_status": "INACTIVE"},
            )
            self.db.commit()
            self.db.refresh(user)
        return self._to_response(user)

    def reinvite(
        self, tenant_id: UUID, user_id: UUID, actor_id: UUID
    ) -> UserCreateResponse:
        """POST /users/{id}/reinvite — new 72-hour invitation token (BR-PF-054)."""
        user = self._get_user(tenant_id, user_id)
        if user.account_status not in {"INVITED", "EXPIRED"}:
            raise ValidationAppError(
                "Only INVITED or EXPIRED users can be re-invited", req_id=_REQ
            )
        self._assert_seat_available(tenant_id)
        existing = self.invites.get_active_for_user(user.user_id)
        if existing is not None:
            existing.status = "CANCELLED"
            self.db.add(existing)
            self.db.flush()
        token, expires_on = self._mint_invite(tenant_id, user, actor_id)
        user.account_status = "INVITED"
        user.invited_at = utcnow()
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_REINVITED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"email": user.email},
        )
        self.db.commit()
        self.db.refresh(user)
        return UserCreateResponse(
            **self._to_response(user).model_dump(),
            invite_token=token,
            invite_expires_on=expires_on,
        )

    def admin_reset_password(
        self, tenant_id: UUID, user_id: UUID, actor_id: UUID
    ) -> PasswordActionResponse:
        """POST /users/{id}/reset-password — permission-gated reset (D11).

        Issues a single-use reset challenge and returns the token because
        ``NTF-PF-008-03`` e-mail delivery is deferred.
        """
        user = self._get_user(tenant_id, user_id)
        if user.account_status != "ACTIVE":
            raise ValidationAppError(
                "Only ACTIVE users can be reset", req_id=_REQ
            )
        token = generate_opaque_token()
        user.reset_token_hash = hash_token(token)
        user.reset_token_expires_at = utcnow() + timedelta(minutes=RESET_TTL_MINUTES)
        user.sessions_invalid_before = utcnow()
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_PASSWORD_RESET_ISSUED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"email": user.email, "expires_in_minutes": RESET_TTL_MINUTES},
        )
        self.db.commit()
        return PasswordActionResponse(
            message="Password reset challenge issued",
            user_id=user.user_id,
            reset_token=token,
            expires_in_minutes=RESET_TTL_MINUTES,
        )

    def self_update(
        self, tenant_id: UUID, user_id: UUID, payload: UserSelfUpdate
    ) -> UserResponse:
        """PUT /users/me — own profile (no role/organization/status change possible)."""
        user = self._get_user(tenant_id, user_id)
        for field in ("first_name", "last_name", "mobile", "designation"):
            value = getattr(payload, field)
            if value is not None:
                setattr(user, field, value)
        if payload.display_name is not None:
            user.display_name = payload.display_name
        elif payload.first_name is not None or payload.last_name is not None:
            user.display_name = " ".join(
                part for part in (user.first_name, user.last_name) if part
            )
        user.version_no += 1
        self.db.add(user)
        write_audit_event(
            self.db,
            event_type="USER_PROFILE_UPDATED",
            event_category="USER",
            entity_type="user",
            entity_id=user.user_id,
            actor_id=user_id,
            tenant_id=tenant_id,
            payload={"self_service": True},
        )
        self.db.commit()
        self.db.refresh(user)
        return self._to_response(user)


# Exported for the authentication service (invitation activation / password challenges).
__all__ = [
    "ALLOWED_TRANSITIONS",
    "INVITE_TTL_HOURS",
    "LOCKOUT_MINUTES",
    "LOCKOUT_THRESHOLD",
    "PASSWORD_MIN_LENGTH",
    "RESET_TTL_MINUTES",
    "SEAT_HOLDING_STATUSES",
    "UserService",
    "require_user_export",
    "require_user_read",
    "require_user_write",
    "utcnow",
]
