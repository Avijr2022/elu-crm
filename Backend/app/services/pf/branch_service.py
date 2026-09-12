"""PF-005 Branch Management service (ELU-BFS-PF-005).

Implements the backend functional layer for Branch Management: CRUD, lifecycle,
hierarchy, address upsert, search, JSON export, edition gate (BR-PF-034) and the
per-edition branch limit (BR-PF-039).

Authorisation is intentionally a *role gate* on the lines of PF-004
(``organization_service.require_org_*``). Runtime permission-grain enforcement for
the PF surface remains deferred to PF-009 (HD-01); ``app.core.rbac.has_permission``
grants PLATFORM_ADMIN a universal bypass, which would contradict the read-only
Platform Admin rule, so an explicit role check is used instead.

EXPLICITLY DEFERRED (must not be implemented here):
  * branch-head assignment/validation (BR-PF-038 / AC-PF-005-04) -> PF-008
  * ``users.branch_id`` / user-to-branch assignment             -> PF-008
  * department linkage                                          -> PF-006
  * project -> branch linkage (BR-PF-037 delete restriction)    -> deferred
  * NTF-PF-005-* notifications and RPT-PF-005-* reports         -> deferred
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.edition_gating import BRANCH, require_feature
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.models.pf import AuditEvent, Branch, BranchAddress, Edition, Organization, Tenant
from app.schemas.pf.branch import (
    BranchAddressIn,
    BranchAddressResponse,
    BranchCreate,
    BranchHierarchyNode,
    BranchHierarchyResponse,
    BranchHistoryItem,
    BranchHistoryResponse,
    BranchListResponse,
    BranchReplace,
    BranchResponse,
    BranchUpdate,
)
from app.services.pf.audit_service import write_audit_event

_REQ = "PF-005"

# ---------------------------------------------------------------- role gates
# BFS-PF-005 §12 (approved matrix, mirrored in app/db/seed.py BRANCH_PERMISSION_MATRIX).
_BRANCH_READ_ROLES = frozenset(
    {"PLATFORM_ADMIN", "TENANT_ADMIN", "SALES_MANAGER", "PROJECT_MANAGER", "FINANCE_USER"}
)
_BRANCH_WRITE_ROLES = frozenset({"TENANT_ADMIN"})
_BRANCH_EXPORT_ROLES = frozenset({"TENANT_ADMIN"})


def require_branch_read(role_code: str) -> None:
    """Branch read matrix (BFS-PF-005 §12)."""
    if role_code not in _BRANCH_READ_ROLES:
        raise ForbiddenError("Branch read not permitted", req_id=_REQ)


def require_branch_write(role_code: str) -> None:
    """Branch create/update/delete matrix (BFS-PF-005 §12): Tenant Admin only."""
    if role_code not in _BRANCH_WRITE_ROLES:
        raise ForbiddenError("Branch write not permitted", req_id=_REQ)


def require_branch_export(role_code: str) -> None:
    """Branch export matrix (BFS-PF-005 §12 + seeded ``branch.export`` grain)."""
    if role_code not in _BRANCH_EXPORT_ROLES:
        raise ForbiddenError("Branch export not permitted", req_id=_REQ)


# ------------------------------------------------------------------ constants
# BFS-PF-005 §5 — allowed next states.
STATUS_TRANSITIONS: dict[str, set[str]] = {
    "DRAFT": {"ACTIVE", "CANCELLED"},
    "ACTIVE": {"INACTIVE"},
    "INACTIVE": {"ACTIVE", "ARCHIVED"},
    "ARCHIVED": set(),
    "CANCELLED": set(),
}

MAX_BRANCHES_LIMIT_CODE = "MAX_BRANCHES"

# BR-PF-036 — "At least one HEAD_OFFICE branch per tenant *recommended*"
# (Type: Validation, Severity: Warning, Enforcement: API). This is deliberately a
# NON-BLOCKING advisory: it never rejects a request.
HEAD_OFFICE_WARNING = (
    "BR-PF-036: no HEAD_OFFICE branch exists for this tenant "
    "(at least one HEAD_OFFICE branch is recommended)"
)


class BranchService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------- helpers
    def assert_branch_feature(self, tenant_id: UUID) -> None:
        """BR-PF-034 / AC-PF-005-01 — Branch requires Professional or Enterprise.

        Reuses the project's established edition-gating convention
        (``app.core.edition_gating.require_feature`` → HTTP 403 FORBIDDEN).
        """
        require_feature(self.db, tenant_id, BRANCH)

    def _to_address_response(
        self, address: Optional[BranchAddress]
    ) -> Optional[BranchAddressResponse]:
        if address is None:
            return None
        return BranchAddressResponse(
            id=address.branch_address_id,
            address_line_1=address.address_line_1,
            address_line_2=address.address_line_2,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            country_code=address.country_code,
            latitude=address.latitude,
            longitude=address.longitude,
        )

    def _address_of(self, branch: Branch) -> Optional[BranchAddress]:
        if branch.branch_address_id is None:
            return None
        return self.db.scalars(
            select(BranchAddress).where(
                BranchAddress.branch_address_id == branch.branch_address_id,
                BranchAddress.tenant_id == branch.tenant_id,
                BranchAddress.is_deleted.is_(False),
            )
        ).first()

    def _to_response(
        self, branch: Branch, *, warnings: Optional[list[str]] = None
    ) -> BranchResponse:
        return BranchResponse(
            id=branch.branch_id,
            tenant_id=branch.tenant_id,
            code=branch.branch_code,
            name=branch.branch_name,
            branch_type=branch.branch_type,
            organization_id=branch.organization_id,
            parent_branch_id=branch.parent_branch_id,
            branch_head_user_id=branch.branch_head_user_id,
            email=branch.email,
            phone=branch.phone,
            timezone_id=branch.timezone_id,
            working_hours=branch.working_hours,
            status=branch.status,
            opened_date=branch.opened_date,
            closed_date=branch.closed_date,
            address=self._to_address_response(self._address_of(branch)),
            warnings=list(warnings or []),
            version_no=branch.version_no,
            created_on=branch.created_on,
            modified_on=branch.modified_on,
        )

    def _load(self, tenant_id: UUID, branch_id: UUID) -> Optional[Branch]:
        return self.db.scalars(
            select(Branch).where(
                Branch.branch_id == branch_id,
                Branch.tenant_id == tenant_id,
                Branch.is_deleted.is_(False),
            )
        ).first()

    def _get_or_404(self, tenant_id: UUID, branch_id: UUID) -> Branch:
        branch = self._load(tenant_id, branch_id)
        if branch is None:
            raise NotFoundError("Branch not found", req_id=_REQ)
        return branch

    def _resolve_organization(self, tenant_id: UUID, organization_id: UUID) -> Organization:
        """Organization must exist, be non-deleted and belong to the same tenant.

        A missing or foreign-tenant organization yields NOT_FOUND so that branch
        APIs never confirm the existence of another tenant's organization.
        """
        org = self.db.scalars(
            select(Organization).where(
                Organization.organization_id == organization_id,
                Organization.tenant_id == tenant_id,
                Organization.is_deleted.is_(False),
            )
        ).first()
        if org is None:
            raise NotFoundError(
                "Organization not found for this tenant", req_id=_REQ
            )
        return org

    def _resolve_parent(
        self, tenant_id: UUID, parent_branch_id: UUID, *, branch_id: Optional[UUID] = None
    ) -> Branch:
        parent = self.db.scalars(
            select(Branch).where(
                Branch.branch_id == parent_branch_id,
                Branch.tenant_id == tenant_id,
                Branch.is_deleted.is_(False),
            )
        ).first()
        if parent is None:
            raise NotFoundError(
                "Parent branch not found for this tenant", req_id=_REQ
            )
        self._assert_no_cycle(tenant_id, branch_id, parent.branch_id)
        return parent

    def _assert_no_cycle(
        self, tenant_id: UUID, branch_id: Optional[UUID], parent_branch_id: UUID
    ) -> None:
        """Reject self-parenting and circular ancestry (BFS-PF-005 §8 hierarchy)."""
        if branch_id is not None and parent_branch_id == branch_id:
            raise ValidationAppError(
                "A branch cannot be its own parent", req_id=_REQ
            )
        seen: set[UUID] = set()
        current: Optional[UUID] = parent_branch_id
        while current is not None:
            if current == branch_id or current in seen:
                raise ValidationAppError(
                    "Circular branch ancestry is not allowed", req_id=_REQ
                )
            seen.add(current)
            current = self.db.scalar(
                select(Branch.parent_branch_id).where(
                    Branch.branch_id == current,
                    Branch.tenant_id == tenant_id,
                )
            )

    def _max_branches_limit(self, tenant_id: UUID) -> Optional[Decimal]:
        """BR-PF-039 — read the tenant edition's ``MAX_BRANCHES`` limit.

        The value is read from ``core.edition_limit`` via the tenant's edition
        (the project's existing edition-limit mechanism); it is never hard-coded.
        """
        tenant = self.db.scalars(
            select(Tenant)
            .options(joinedload(Tenant.edition).joinedload(Edition.limits))
            .where(Tenant.tenant_id == tenant_id, Tenant.is_deleted.is_(False))
        ).first()
        if tenant is None or tenant.edition is None:
            return None
        for limit in tenant.edition.limits:
            if limit.limit_code.upper() == MAX_BRANCHES_LIMIT_CODE:
                return limit.limit_value
        return None

    def _count_branches(self, tenant_id: UUID) -> int:
        """Count non-deleted branches (soft-deleted rows never consume the quota)."""
        return int(
            self.db.scalar(
                select(func.count())
                .select_from(Branch)
                .where(Branch.tenant_id == tenant_id, Branch.is_deleted.is_(False))
            )
            or 0
        )

    def _assert_branch_quota(self, tenant_id: UUID) -> None:
        limit = self._max_branches_limit(tenant_id)
        if limit is None:
            return
        if self._count_branches(tenant_id) >= int(limit):
            raise ValidationAppError(
                f"Maximum branches for this edition reached ({int(limit)}) — BR-PF-039",
                req_id="BR-PF-039",
            )

    def _head_office_warnings(self, tenant_id: UUID) -> list[str]:
        """BR-PF-036 advisory (non-blocking)."""
        count = self.db.scalar(
            select(func.count())
            .select_from(Branch)
            .where(
                Branch.tenant_id == tenant_id,
                Branch.branch_type == "HEAD_OFFICE",
                Branch.is_deleted.is_(False),
            )
        ) or 0
        return [] if int(count) > 0 else [HEAD_OFFICE_WARNING]

    def _apply_status(self, branch: Branch, new_status: str) -> bool:
        """Apply the BFS-PF-005 §5 lifecycle. Returns True when status changed."""
        new_status = new_status.upper()
        if new_status == branch.status:
            return False
        if new_status not in STATUS_TRANSITIONS.get(branch.status, set()):
            raise ValidationAppError(
                f"Invalid branch status transition {branch.status} → {new_status}",
                req_id=_REQ,
            )
        branch.status = new_status
        if new_status == "ACTIVE" and branch.opened_date is None:
            branch.opened_date = date.today()
        if new_status == "ARCHIVED" and branch.closed_date is None:
            branch.closed_date = date.today()
        return True

    def _upsert_address(
        self,
        tenant_id: UUID,
        branch: Branch,
        payload: BranchAddressIn,
        actor_id: Optional[UUID],
    ) -> BranchAddress:
        """Create/update the single branch_address row (BFS-PF-005 §9, 1:1)."""
        address = self.db.scalars(
            select(BranchAddress).where(
                BranchAddress.branch_id == branch.branch_id,
                BranchAddress.tenant_id == tenant_id,
                BranchAddress.is_deleted.is_(False),
            )
        ).first()
        fields: dict[str, Any] = {
            "address_line_1": payload.address_line_1,
            "address_line_2": payload.address_line_2,
            "city": payload.city,
            "state": payload.state,
            "postal_code": payload.postal_code,
            "country_code": payload.country_code,
            "latitude": payload.latitude,
            "longitude": payload.longitude,
        }
        if address is None:
            address = BranchAddress(
                branch_address_id=uuid4(),
                tenant_id=tenant_id,
                branch_id=branch.branch_id,
                created_by=actor_id,
                **fields,
            )
            self.db.add(address)
        else:
            for key, value in fields.items():
                setattr(address, key, value)
            address.version_no += 1
            address.modified_by = actor_id
        self.db.flush()
        branch.branch_address_id = address.branch_address_id
        return address

    # ----------------------------------------------------------------- CRUD
    def list_branches(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        branch_type: Optional[str] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> BranchListResponse:
        q = select(Branch).where(
            Branch.tenant_id == tenant_id,
            Branch.is_deleted.is_(False),
        )
        if status:
            q = q.where(Branch.status == status.upper())
        if branch_type:
            q = q.where(Branch.branch_type == branch_type.upper())
        if organization_id:
            q = q.where(Branch.organization_id == organization_id)
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Branch.branch_code.ilike(like),
                    Branch.branch_name.ilike(like),
                    Branch.email.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        order: tuple[Any, ...] = (Branch.branch_name.asc(),)
        if sort:
            key = sort.lstrip("-").lower()
            col_map = {
                "name": Branch.branch_name,
                "code": Branch.branch_code,
                "status": Branch.status,
                "type": Branch.branch_type,
                "created_on": Branch.created_on,
            }
            col = col_map.get(key)
            if col is not None:
                order = (col.desc() if sort.startswith("-") else col.asc(),)
        items = list(
            self.db.scalars(
                q.order_by(*order).offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        warnings = self._head_office_warnings(tenant_id)
        return BranchListResponse(
            items=[self._to_response(b, warnings=warnings) for b in items],
            page=page,
            page_size=page_size,
            total=int(total),
            warnings=warnings,
        )

    def get(self, tenant_id: UUID, branch_id: UUID) -> BranchResponse:
        branch = self._get_or_404(tenant_id, branch_id)
        return self._to_response(branch, warnings=self._head_office_warnings(tenant_id))

    def create(
        self, tenant_id: UUID, payload: BranchCreate, actor_id: UUID
    ) -> BranchResponse:
        # BR-PF-034 edition gate
        self.assert_branch_feature(tenant_id)
        # BR-PF-039 per-edition branch limit
        self._assert_branch_quota(tenant_id)
        # BR-PF-035 code unique within tenant (non-deleted)
        exists = self.db.scalars(
            select(Branch).where(
                Branch.tenant_id == tenant_id,
                Branch.branch_code == payload.code,
                Branch.is_deleted.is_(False),
            )
        ).first()
        if exists:
            raise ConflictError("Branch code already exists", req_id="BR-PF-035")

        organization = self._resolve_organization(tenant_id, payload.organization_id)
        parent = (
            self._resolve_parent(tenant_id, payload.parent_branch_id)
            if payload.parent_branch_id is not None
            else None
        )

        branch = Branch(
            branch_id=uuid4(),
            tenant_id=tenant_id,
            organization_id=organization.organization_id,
            parent_branch_id=parent.branch_id if parent else None,
            branch_code=payload.code,
            branch_name=payload.name,
            branch_type=payload.branch_type,
            branch_head_user_id=None,  # deferred to PF-008 (BR-PF-038)
            email=str(payload.email).lower() if payload.email else None,
            phone=payload.phone,
            timezone_id=payload.timezone_id,
            working_hours=payload.working_hours,
            status=payload.status,
            opened_date=payload.opened_date,
            closed_date=payload.closed_date,
            created_by=actor_id,
            version_no=1,
        )
        if branch.status == "ACTIVE" and branch.opened_date is None:
            branch.opened_date = date.today()
        self.db.add(branch)
        self.db.flush()

        if payload.address is not None:
            self._upsert_address(tenant_id, branch, payload.address, actor_id)

        write_audit_event(
            self.db,
            event_type="BRANCH_CREATED",
            event_category="BRANCH",
            entity_type="branch",
            entity_id=branch.branch_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "branch_id": str(branch.branch_id),
                "code": branch.branch_code,
                "name": branch.branch_name,
                "branch_type": branch.branch_type,
                "organization_id": str(branch.organization_id),
                "parent_branch_id": str(branch.parent_branch_id)
                if branch.parent_branch_id
                else None,
                "status": branch.status,
            },
        )
        self.db.commit()
        created = self._get_or_404(tenant_id, branch.branch_id)
        return self._to_response(created, warnings=self._head_office_warnings(tenant_id))

    def update(
        self,
        tenant_id: UUID,
        branch_id: UUID,
        payload: BranchUpdate | BranchReplace,
        actor_id: UUID,
        *,
        replace: bool = False,
    ) -> BranchResponse:
        branch = self._get_or_404(tenant_id, branch_id)
        if branch.version_no != payload.version_no:
            raise ConflictError("Branch version conflict", req_id=_REQ)

        data = (
            payload.model_dump(exclude={"version_no"})
            if replace
            else payload.model_dump(exclude_unset=True, exclude={"version_no"})
        )
        if replace and not data.get("name"):
            raise ValidationAppError("name is required on PUT", req_id=_REQ)

        status_change: Optional[tuple[str, str]] = None
        parent_changed = False

        if data.get("name"):
            branch.branch_name = data["name"]
        if data.get("branch_type"):
            branch.branch_type = data["branch_type"]
        if data.get("organization_id"):
            organization = self._resolve_organization(tenant_id, data["organization_id"])
            branch.organization_id = organization.organization_id
        if "parent_branch_id" in data:
            new_parent_id = data["parent_branch_id"]
            if new_parent_id is None:
                parent_changed = branch.parent_branch_id is not None
                branch.parent_branch_id = None
            else:
                parent = self._resolve_parent(tenant_id, new_parent_id, branch_id=branch_id)
                parent_changed = branch.parent_branch_id != parent.branch_id
                branch.parent_branch_id = parent.branch_id
        if "email" in data:
            branch.email = str(data["email"]).lower() if data["email"] else None
        if "phone" in data:
            branch.phone = data["phone"]
        if "timezone_id" in data:
            branch.timezone_id = data["timezone_id"]
        if "working_hours" in data:
            branch.working_hours = data["working_hours"]
        if "opened_date" in data:
            branch.opened_date = data["opened_date"]
        if "closed_date" in data:
            branch.closed_date = data["closed_date"]
        if data.get("status"):
            old_status = branch.status
            if self._apply_status(branch, data["status"]):
                status_change = (old_status, branch.status)
        if data.get("address") is not None:
            address_payload = (
                data["address"]
                if isinstance(data["address"], BranchAddressIn)
                else BranchAddressIn(**data["address"])
            )
            self._upsert_address(tenant_id, branch, address_payload, actor_id)

        branch.version_no += 1
        branch.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="BRANCH_REPLACED" if replace else "BRANCH_UPDATED",
            event_category="BRANCH",
            entity_type="branch",
            entity_id=branch.branch_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"fields": sorted(data.keys()), "replace": replace},
        )
        if status_change is not None:
            write_audit_event(
                self.db,
                event_type="BRANCH_STATUS_CHANGED",
                event_category="BRANCH",
                entity_type="branch",
                entity_id=branch.branch_id,
                actor_id=actor_id,
                tenant_id=tenant_id,
                payload={"old_status": status_change[0], "new_status": status_change[1]},
            )
        if parent_changed:
            write_audit_event(
                self.db,
                event_type="BRANCH_HIERARCHY_CHANGED",
                event_category="BRANCH",
                entity_type="branch",
                entity_id=branch.branch_id,
                actor_id=actor_id,
                tenant_id=tenant_id,
                payload={
                    "parent_branch_id": str(branch.parent_branch_id)
                    if branch.parent_branch_id
                    else None
                },
            )
        self.db.commit()
        updated = self._get_or_404(tenant_id, branch_id)
        return self._to_response(updated, warnings=self._head_office_warnings(tenant_id))

    def soft_delete(self, tenant_id: UUID, branch_id: UUID, actor_id: UUID) -> None:
        """Soft delete (BFS-PF-005 §10). The 1:1 address row is soft-deleted too,
        mirroring the documented ``branch -> branch_address`` CASCADE."""
        branch = self._get_or_404(tenant_id, branch_id)
        children = self.db.scalar(
            select(func.count())
            .select_from(Branch)
            .where(
                Branch.tenant_id == tenant_id,
                Branch.parent_branch_id == branch.branch_id,
                Branch.is_deleted.is_(False),
            )
        ) or 0
        if int(children) > 0:
            raise ValidationAppError(
                "Branch has child branches and cannot be deleted (parent FK RESTRICT)",
                req_id=_REQ,
            )
        branch.is_deleted = True
        branch.is_active = False
        branch.version_no += 1
        branch.modified_by = actor_id
        address = self._address_of(branch)
        if address is not None:
            address.is_deleted = True
            address.is_active = False
            address.version_no += 1
            address.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="BRANCH_DELETED",
            event_category="BRANCH",
            entity_type="branch",
            entity_id=branch.branch_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"code": branch.branch_code},
        )
        self.db.commit()

    # ------------------------------------------------------------- read side
    def export_rows(self, tenant_id: UUID) -> list[dict]:
        """BFS-PF-005 §10 export (JSON). Tenant Admin only (role gate at API)."""
        items = self.list_branches(tenant_id, page=1, page_size=500).items
        return [
            {
                "id": str(i.id),
                "code": i.code,
                "name": i.name,
                "branch_type": i.branch_type,
                "status": i.status,
                "organization_id": str(i.organization_id),
                "parent_branch_id": str(i.parent_branch_id) if i.parent_branch_id else None,
                "city": i.address.city if i.address else None,
                "country_code": i.address.country_code if i.address else None,
                "opened_date": i.opened_date.isoformat() if i.opened_date else None,
                "closed_date": i.closed_date.isoformat() if i.closed_date else None,
            }
            for i in items
        ]

    def hierarchy(self, tenant_id: UUID) -> BranchHierarchyResponse:
        """Tenant-wide branch tree (BFS-PF-005 §10)."""
        branches = list(
            self.db.scalars(
                select(Branch).where(
                    Branch.tenant_id == tenant_id,
                    Branch.is_deleted.is_(False),
                )
            ).all()
        )
        if not branches:
            raise NotFoundError("No branches found", req_id=_REQ)

        by_id = {b.branch_id: b for b in branches}
        children_map: dict[Optional[UUID], list[Branch]] = {}
        for b in branches:
            parent_id = b.parent_branch_id if b.parent_branch_id in by_id else None
            children_map.setdefault(parent_id, []).append(b)

        def build(branch: Branch, path: frozenset[UUID]) -> BranchHierarchyNode:
            kids = sorted(
                children_map.get(branch.branch_id, []), key=lambda x: x.branch_name
            )
            next_path = path | {branch.branch_id}
            return BranchHierarchyNode(
                id=branch.branch_id,
                code=branch.branch_code,
                name=branch.branch_name,
                branch_type=branch.branch_type,
                organization_id=branch.organization_id,
                parent_branch_id=branch.parent_branch_id,
                status=branch.status,
                children=[
                    build(k, next_path)
                    for k in kids
                    if k.branch_id not in next_path
                ],
            )

        return BranchHierarchyResponse(
            items=[build(b, frozenset()) for b in children_map.get(None, [])],
            warnings=self._head_office_warnings(tenant_id),
        )

    def history(
        self, tenant_id: UUID, branch_id: UUID, *, limit: int = 50
    ) -> BranchHistoryResponse:
        """Audit trail for a branch (BFS-PF-005 §15).

        NOTE: BFS-PF-005 §10 does not list a history endpoint (unlike PF-004), so
        this is exposed at service level only and consumed by the test suite.
        """
        branch = self._get_or_404(tenant_id, branch_id)
        rows = list(
            self.db.scalars(
                select(AuditEvent)
                .where(
                    AuditEvent.entity_type == "branch",
                    AuditEvent.entity_id == branch.branch_id,
                    or_(
                        AuditEvent.tenant_id == tenant_id,
                        AuditEvent.tenant_id.is_(None),
                    ),
                )
                .order_by(AuditEvent.created_on.desc())
                .limit(limit)
            ).all()
        )
        return BranchHistoryResponse(
            items=[
                BranchHistoryItem(
                    id=r.id,
                    event_type=r.event_type,
                    event_category=r.event_category,
                    actor_email=r.actor_email,
                    payload_json=r.payload_json,
                    created_on=r.created_on,
                )
                for r in rows
            ],
            total=len(rows),
        )
