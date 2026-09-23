"""PF-006 Department Management service (ELU-BFS-PF-006).

Implements the backend functional layer for Department Management: CRUD, three-state
lifecycle, runtime-derived hierarchy (root depth 1 / maximum depth 5), circular-parent
protection, the same-organization parent rule, soft delete with child guard,
tenant-scoped search/pagination, JSON export and the BR-PF-045 advisory.

Authorisation is enforced at **permission grain** (PF-009 Batch 2): the seeded
``DEPARTMENT_PERMISSION_MATRIX`` in ``app/db/seed.py`` is authoritative for every role, so
the approved PF-006 §12 matrix is applied through ``app.core.rbac.has_permission``
(Platform Admin holds no ``department.*`` grain).

Approved implementation decisions applied here:
  * C-N1  — no ``department_type`` value validation (the specification defines no list).
  * C-N2  — hierarchy depth/path are **derived at runtime**; nothing is persisted.
  * C-N3  — lifecycle ACTIVE / INACTIVE / ARCHIVED (default ACTIVE).
  * C-N4  — ``department.export`` is Tenant Admin only (implementation decision: the
            authoritative matrix carries no export column).
  * C-N7  — root department depth = 1; maximum depth = 5 (a 6th level is rejected).
  * C-N8  — an empty tenant hierarchy raises NOT_FOUND (PF-004/PF-005 precedent).
  * C-N9  — INACTIVE/ARCHIVED departments may be parents; only soft-deleted parents are
            rejected.
  * C-N10 — ``branch_id`` need not share the department's ``organization_id``.
  * C-N11 — a parent and its child MUST belong to the same ``organization_id``.
  * C-N12 — ``department_head_user_id`` is nullable, has no FK/relationship and is never
            client-controlled; ACTIVE-user validation is deferred to PF-008.

EXPLICITLY DEFERRED (must not be implemented here):
  * ``users.department_id`` / user <-> department assignment        -> PF-008
  * department-head assignment/validation (BR-PF-043)               -> PF-008
  * BR-PF-044 user-assignment delete guard                          -> PF-008
  * AC-PF-006-04 approval workflow (CPS-001)                        -> deferred
  * NTF-PF-006-* notifications, RPT-PF-006-01/02 reports            -> deferred
  * CSV/XLSX export (JSON only)                                     -> deferred
  * edition gating (Department is available in all editions)        -> not applicable
  * restore/undelete and the §17 v2/v3 enhancements                 -> deferred

NOTE (typed history schema): the Batch-2 schema module intentionally created only the
endpoint-bearing schemas, so ``history()`` returns JSON-safe ``list[dict]`` rows with the
same keys as the PF-004/PF-005 history items. A typed ``DepartmentHistoryItem/Response``
belongs to the schema/API batch.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.core.rbac import has_permission
from app.models.pf import AuditEvent, Branch, Department, Organization
from app.schemas.pf.department import (
    DepartmentCreate,
    DepartmentHierarchyNode,
    DepartmentHierarchyResponse,
    DepartmentHistoryItem,
    DepartmentHistoryResponse,
    DepartmentListResponse,
    DepartmentResponse,
    DepartmentUpdate,
)
from app.services.pf.audit_service import write_audit_event

_REQ = "PF-006"

# ------------------------------------------------------- permission-grain gates
# BFS-PF-006 §12 (approved matrix, mirrored in app/db/seed.py
# DEPARTMENT_PERMISSION_MATRIX). PF-009 Batch 2: the seeded matrix is authoritative for
# every role, so the gates below check the permission grain instead of the role.
_DEPARTMENT_WRITE_CODES = ("department.create", "department.update", "department.delete")
_DEPARTMENT_EXPORT_CODE = "department.export"


def require_department_read(current: CurrentUser) -> None:
    """Department read (BFS-PF-006 §12) at permission grain."""
    if not has_permission(current, "department.read"):
        raise ForbiddenError("Department read not permitted", req_id=_REQ)


def require_department_write(current: CurrentUser) -> None:
    """Department create/update/delete (BFS-PF-006 §12): Tenant Admin only."""
    if not any(has_permission(current, code) for code in _DEPARTMENT_WRITE_CODES):
        raise ForbiddenError("Department write not permitted", req_id=_REQ)


def require_department_export(current: CurrentUser) -> None:
    """Department export (C-N4): Tenant Admin only."""
    if not has_permission(current, _DEPARTMENT_EXPORT_CODE):
        raise ForbiddenError("Department export not permitted", req_id=_REQ)


# ------------------------------------------------------------------ constants
# C-N7 / BR-PF-041 — root depth 1, maximum depth 5 (6th level rejected). Derived at
# runtime only; no level/path column exists (C-N2).
ROOT_DEPTH = 1
MAX_DEPARTMENT_DEPTH = 5

# BFS-PF-006 §5 — allowed next states (three-state lifecycle, C-N3).
STATUS_TRANSITIONS: dict[str, set[str]] = {
    "ACTIVE": {"INACTIVE"},
    "INACTIVE": {"ACTIVE", "ARCHIVED"},
    "ARCHIVED": set(),
}

# BR-PF-045 — advisory only (Validation / Warning / API). Never blocks a request.
RECOMMENDED_DEPARTMENT_WARNING = (
    "BR-PF-045: no departments exist for this tenant "
    "(at least one department is recommended)"
)


class DepartmentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------- helpers
    def _to_response(
        self, department: Department, *, warnings: Optional[list[str]] = None
    ) -> DepartmentResponse:
        return DepartmentResponse(
            id=department.department_id,
            tenant_id=department.tenant_id,
            code=department.department_code,
            name=department.department_name,
            department_type=department.department_type,
            organization_id=department.organization_id,
            parent_department_id=department.parent_department_id,
            branch_id=department.branch_id,
            department_head_user_id=department.department_head_user_id,
            description=department.description,
            cost_centre_code=department.cost_centre_code,
            status=department.status,
            warnings=list(warnings or []),
            version_no=department.version_no,
            created_on=department.created_on,
            modified_on=department.modified_on,
        )

    def _load(self, tenant_id: UUID, department_id: UUID) -> Optional[Department]:
        """Tenant-scoped load of a non-deleted department."""
        return self.db.scalars(
            select(Department).where(
                Department.department_id == department_id,
                Department.tenant_id == tenant_id,
                Department.is_deleted.is_(False),
            )
        ).first()

    def _get_or_404(self, tenant_id: UUID, department_id: UUID) -> Department:
        department = self._load(tenant_id, department_id)
        if department is None:
            # Soft-deleted and foreign-tenant rows are indistinguishable from missing
            # rows on purpose (never confirm another tenant's records — BR-PF-016).
            raise NotFoundError("Department not found", req_id=_REQ)
        return department

    def _resolve_organization(
        self, tenant_id: UUID, organization_id: UUID
    ) -> Organization:
        """Organization must exist, be non-deleted and belong to the same tenant."""
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

    def _resolve_branch(self, tenant_id: UUID, branch_id: UUID) -> Branch:
        """Branch must exist, be non-deleted and belong to the same tenant.

        C-N10: ``branch.organization_id`` is deliberately NOT compared with the
        department's ``organization_id``.
        """
        branch = self.db.scalars(
            select(Branch).where(
                Branch.branch_id == branch_id,
                Branch.tenant_id == tenant_id,
                Branch.is_deleted.is_(False),
            )
        ).first()
        if branch is None:
            raise NotFoundError("Branch not found for this tenant", req_id=_REQ)
        return branch

    def _resolve_parent(
        self,
        tenant_id: UUID,
        parent_department_id: UUID,
        *,
        department_id: Optional[UUID] = None,
        organization_id: Optional[UUID] = None,
    ) -> Department:
        """Parent must exist, be non-deleted and belong to the same tenant.

        C-N9: ACTIVE, INACTIVE and ARCHIVED parents are all accepted — only a
        soft-deleted parent is rejected. C-N11: when ``organization_id`` is supplied the
        parent must belong to that organisation.
        """
        parent = self.db.scalars(
            select(Department).where(
                Department.department_id == parent_department_id,
                Department.tenant_id == tenant_id,
                Department.is_deleted.is_(False),
            )
        ).first()
        if parent is None:
            raise NotFoundError(
                "Parent department not found for this tenant", req_id=_REQ
            )
        if department_id is not None:
            self._assert_no_cycle(tenant_id, department_id, parent.department_id)
        if organization_id is not None and parent.organization_id != organization_id:
            raise ValidationAppError(
                "Parent department must belong to the same organization (C-N11)",
                req_id=_REQ,
            )
        return parent

    # ------------------------------------------------------------ hierarchy
    def _depth_of(self, tenant_id: UUID, department: Department) -> int:
        """Runtime depth of a department (root = 1, C-N7), walking upward.

        Traversal is protected with a ``seen`` set so an unexpected pre-existing cycle
        can never loop forever.
        """
        depth = ROOT_DEPTH
        seen: set[UUID] = set()
        current: Optional[Department] = department
        while current is not None:
            if current.department_id in seen:
                raise ValidationAppError(
                    "Circular department ancestry detected (BR-PF-042)",
                    req_id="BR-PF-042",
                )
            seen.add(current.department_id)
            if current.parent_department_id is None:
                break
            parent = self._load(tenant_id, current.parent_department_id)
            if parent is None:
                # Ancestry ends at a missing/soft-deleted parent; treat the reachable
                # chain as authoritative (defensive: the delete guard prevents this).
                break
            depth += 1
            current = parent
        return depth

    def _subtree_height(
        self, tenant_id: UUID, department_id: UUID, *, path: frozenset[UUID] = frozenset()
    ) -> int:
        """Height of the subtree rooted at ``department_id`` (1 for a leaf)."""
        if department_id in path:
            raise ValidationAppError(
                "Circular department ancestry detected (BR-PF-042)", req_id="BR-PF-042"
            )
        child_ids = list(
            self.db.scalars(
                select(Department.department_id).where(
                    Department.tenant_id == tenant_id,
                    Department.parent_department_id == department_id,
                    Department.is_deleted.is_(False),
                )
            ).all()
        )
        if not child_ids:
            return 1
        next_path = path | {department_id}
        return 1 + max(
            self._subtree_height(tenant_id, child_id, path=next_path)
            for child_id in child_ids
        )

    def _assert_depth(
        self,
        tenant_id: UUID,
        parent: Optional[Department],
        *,
        node_height: int = 1,
    ) -> None:
        """BR-PF-041 / C-N7 — reject any placement that would exceed depth 5."""
        node_depth = (
            ROOT_DEPTH
            if parent is None
            else self._depth_of(tenant_id, parent) + 1
        )
        max_depth_after = node_depth + node_height - 1
        if max_depth_after > MAX_DEPARTMENT_DEPTH:
            raise ValidationAppError(
                f"Department hierarchy maximum depth is {MAX_DEPARTMENT_DEPTH} "
                f"(BR-PF-041); this placement would reach depth {max_depth_after}",
                req_id="BR-PF-041",
            )

    def _assert_no_cycle(
        self, tenant_id: UUID, department_id: Optional[UUID], parent_department_id: UUID
    ) -> None:
        """Reject self-parenting and circular ancestry (BR-PF-042)."""
        if department_id is not None and parent_department_id == department_id:
            raise ValidationAppError(
                "A department cannot be its own parent (BR-PF-042)",
                req_id="BR-PF-042",
            )
        seen: set[UUID] = set()
        current: Optional[UUID] = parent_department_id
        while current is not None:
            if current == department_id or current in seen:
                raise ValidationAppError(
                    "Circular department ancestry is not allowed (BR-PF-042)",
                    req_id="BR-PF-042",
                )
            seen.add(current)
            current = self.db.scalar(
                select(Department.parent_department_id).where(
                    Department.department_id == current,
                    Department.tenant_id == tenant_id,
                )
            )

    def _children_count(self, tenant_id: UUID, department_id: UUID) -> int:
        """Non-deleted direct children (BR-PF-044 delete guard)."""
        return int(
            self.db.scalar(
                select(func.count())
                .select_from(Department)
                .where(
                    Department.tenant_id == tenant_id,
                    Department.parent_department_id == department_id,
                    Department.is_deleted.is_(False),
                )
            )
            or 0
        )

    # -------------------------------------------------------------- helpers
    def _assert_code_unique(
        self, tenant_id: UUID, code: str, *, exclude_id: Optional[UUID] = None
    ) -> None:
        """BR-PF-040 service-level pre-check (the partial unique index stays authoritative)."""
        q = select(Department).where(
            Department.tenant_id == tenant_id,
            Department.department_code == code,
            Department.is_deleted.is_(False),
        )
        if exclude_id is not None:
            q = q.where(Department.department_id != exclude_id)
        if self.db.scalars(q).first() is not None:
            raise ConflictError("Department code already exists", req_id="BR-PF-040")

    def _apply_status(self, department: Department, new_status: str) -> bool:
        """Apply the BFS-PF-006 §5 lifecycle (C-N3). Returns True when status changed."""
        new_status = new_status.upper()
        if new_status == department.status:
            return False
        if new_status not in STATUS_TRANSITIONS.get(department.status, set()):
            raise ValidationAppError(
                f"Invalid department status transition "
                f"{department.status} → {new_status}",
                req_id=_REQ,
            )
        department.status = new_status
        return True

    def _recommended_warnings(self, tenant_id: UUID) -> list[str]:
        """BR-PF-045 advisory (non-blocking)."""
        count = self.db.scalar(
            select(func.count())
            .select_from(Department)
            .where(
                Department.tenant_id == tenant_id,
                Department.is_deleted.is_(False),
            )
        ) or 0
        return [] if int(count) > 0 else [RECOMMENDED_DEPARTMENT_WARNING]

    # ------------------------------------------------------------- read side
    def list_departments(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> DepartmentListResponse:
        """Tenant-scoped department list (BFS-PF-006 §10)."""
        q = select(Department).where(
            Department.tenant_id == tenant_id,
            Department.is_deleted.is_(False),
        )
        if status:
            q = q.where(Department.status == status.upper())
        if organization_id:
            q = q.where(Department.organization_id == organization_id)
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Department.department_code.ilike(like),
                    Department.department_name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        order: tuple[Any, ...] = (Department.department_name.asc(),)
        if sort:
            key = sort.lstrip("-").lower()
            col_map = {
                "name": Department.department_name,
                "code": Department.department_code,
                "status": Department.status,
                "created_on": Department.created_on,
            }
            col = col_map.get(key)
            if col is not None:
                order = (col.desc() if sort.startswith("-") else col.asc(),)
        items = list(
            self.db.scalars(
                q.order_by(*order).offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        warnings = self._recommended_warnings(tenant_id)
        return DepartmentListResponse(
            items=[self._to_response(d, warnings=warnings) for d in items],
            page=page,
            page_size=page_size,
            total=int(total),
            warnings=warnings,
        )

    def get(self, tenant_id: UUID, department_id: UUID) -> DepartmentResponse:
        department = self._get_or_404(tenant_id, department_id)
        return self._to_response(
            department, warnings=self._recommended_warnings(tenant_id)
        )

    def hierarchy(self, tenant_id: UUID) -> DepartmentHierarchyResponse:
        """Tenant-wide department tree (BFS-PF-006 §10).

        A forest is returned because departments without a parent are valid roots.
        C-N8: an empty hierarchy raises NOT_FOUND (PF-004/PF-005 precedent).
        """
        departments = list(
            self.db.scalars(
                select(Department).where(
                    Department.tenant_id == tenant_id,
                    Department.is_deleted.is_(False),
                )
            ).all()
        )
        if not departments:
            raise NotFoundError("No departments found", req_id=_REQ)

        by_id = {d.department_id: d for d in departments}
        children_map: dict[Optional[UUID], list[Department]] = {}
        for d in departments:
            parent_id = d.parent_department_id if d.parent_department_id in by_id else None
            children_map.setdefault(parent_id, []).append(d)

        def build(
            department: Department, path: frozenset[UUID]
        ) -> DepartmentHierarchyNode:
            kids = sorted(
                children_map.get(department.department_id, []),
                key=lambda x: x.department_name,
            )
            next_path = path | {department.department_id}
            return DepartmentHierarchyNode(
                id=department.department_id,
                code=department.department_code,
                name=department.department_name,
                department_type=department.department_type,
                organization_id=department.organization_id,
                parent_department_id=department.parent_department_id,
                branch_id=department.branch_id,
                status=department.status,
                children=[
                    build(k, next_path) for k in kids if k.department_id not in next_path
                ],
            )

        return DepartmentHierarchyResponse(
            items=[build(d, frozenset()) for d in children_map.get(None, [])],
            warnings=self._recommended_warnings(tenant_id),
        )

    def export_rows(self, tenant_id: UUID) -> list[dict]:
        """BFS-PF-006 §10 export (JSON only — CSV/XLSX deferred).

        Tenant Admin only (role gate at the API layer, C-N4).
        """
        items = self.list_departments(tenant_id, page=1, page_size=500).items
        return [
            {
                "id": str(i.id),
                "code": i.code,
                "name": i.name,
                "department_type": i.department_type,
                "status": i.status,
                "organization_id": str(i.organization_id),
                "parent_department_id": (
                    str(i.parent_department_id) if i.parent_department_id else None
                ),
                "branch_id": str(i.branch_id) if i.branch_id else None,
                "cost_centre_code": i.cost_centre_code,
                "created_on": i.created_on.isoformat() if i.created_on else None,
            }
            for i in items
        ]

    def history(
        self, tenant_id: UUID, department_id: UUID, *, limit: int = 50
    ) -> DepartmentHistoryResponse:
        """Audit trail for a department (BFS-PF-006 §15).

        Typed response following the PF-004/PF-005 history convention
        (``OrganizationHistoryResponse`` / ``BranchHistoryResponse``). BFS-PF-006 §10
        lists no history endpoint; the route mirrors the PF-004 precedent.
        """
        department = self._get_or_404(tenant_id, department_id)
        rows = list(
            self.db.scalars(
                select(AuditEvent)
                .where(
                    AuditEvent.entity_type == "department",
                    AuditEvent.entity_id == department.department_id,
                    or_(
                        AuditEvent.tenant_id == tenant_id,
                        AuditEvent.tenant_id.is_(None),
                    ),
                )
                .order_by(AuditEvent.created_on.desc())
                .limit(limit)
            ).all()
        )
        return DepartmentHistoryResponse(
            items=[
                DepartmentHistoryItem(
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

    # ------------------------------------------------------------ write side
    def create(
        self, tenant_id: UUID, payload: DepartmentCreate, actor_id: UUID
    ) -> DepartmentResponse:
        """Create a department (BFS-PF-006 §10).

        ``department_head_user_id`` is never accepted from the client (C-N12).
        """
        organization = self._resolve_organization(tenant_id, payload.organization_id)
        branch = (
            self._resolve_branch(tenant_id, payload.branch_id)
            if payload.branch_id is not None
            else None
        )
        parent = (
            self._resolve_parent(
                tenant_id,
                payload.parent_department_id,
                organization_id=organization.organization_id,
            )
            if payload.parent_department_id is not None
            else None
        )
        self._assert_code_unique(tenant_id, payload.code)
        self._assert_depth(tenant_id, parent)

        department = Department(
            department_id=uuid4(),
            tenant_id=tenant_id,
            organization_id=organization.organization_id,
            parent_department_id=parent.department_id if parent else None,
            branch_id=branch.branch_id if branch else None,
            department_code=payload.code,
            department_name=payload.name,
            description=payload.description,
            department_type=payload.department_type,
            cost_centre_code=payload.cost_centre_code,
            status=payload.status.upper(),
            created_by=actor_id,
            version_no=1,
        )
        self.db.add(department)
        write_audit_event(
            self.db,
            event_type="DEPARTMENT_CREATED",
            event_category="DEPARTMENT",
            entity_type="department",
            entity_id=department.department_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "code": department.department_code,
                "organization_id": str(department.organization_id),
                "parent_id": (
                    str(department.parent_department_id)
                    if department.parent_department_id
                    else None
                ),
            },
        )
        self.db.commit()
        return self._to_response(
            self._get_or_404(tenant_id, department.department_id),
            warnings=self._recommended_warnings(tenant_id),
        )

    def update(
        self,
        tenant_id: UUID,
        department_id: UUID,
        payload: DepartmentUpdate,
        actor_id: UUID,
        *,
        replace: bool = False,
    ) -> DepartmentResponse:
        """PATCH/PUT update (BFS-PF-006 §10). ``code`` is immutable (C-N5/PF convention)."""
        department = self._get_or_404(tenant_id, department_id)
        if department.version_no != payload.version_no:
            raise ConflictError("Department version conflict", req_id=_REQ)

        data = (
            payload.model_dump(exclude={"version_no"})
            if replace
            else payload.model_dump(exclude_unset=True, exclude={"version_no"})
        )

        if "name" in data and data["name"] is not None:
            department.department_name = data["name"]
        elif replace:
            raise ValidationAppError("name is required on PUT", req_id=_REQ)
        if "department_type" in data and data["department_type"] is not None:
            department.department_type = data["department_type"]
        if "description" in data:
            department.description = data["description"]
        if "cost_centre_code" in data:
            department.cost_centre_code = data["cost_centre_code"]

        # ---- organisation (adopted organization-change policy: the change is allowed
        #      only when the department ends THIS request at root level, i.e. its
        #      effective parent is NULL, and it has no non-deleted children; the change
        #      is never cascaded and never silently reparents anything — C-N11)
        if data.get("organization_id"):
            organization = self._resolve_organization(
                tenant_id, data["organization_id"]
            )
            if organization.organization_id != department.organization_id:
                # Effective parent *after* this request — evaluated up front so the
                # outcome never depends on the order of the mutation blocks below.
                # PATCH: an omitted field means "unchanged"; an explicit null means
                # "detach". PUT: the replacement payload is authoritative.
                effective_parent_id = (
                    data["parent_department_id"]
                    if "parent_department_id" in data
                    else department.parent_department_id
                )
                if effective_parent_id is not None:
                    raise ValidationAppError(
                        "Cannot change organization: the department must have no "
                        "effective parent (detach the parent in the same request)",
                        req_id=_REQ,
                    )
                if self._children_count(tenant_id, department.department_id) > 0:
                    raise ValidationAppError(
                        "Cannot change organization: child departments belong to the "
                        "current organization (C-N11)",
                        req_id=_REQ,
                    )
                department.organization_id = organization.organization_id

        # ---- branch (nullable; C-N10 — no organization cross-check)
        if "branch_id" in data:
            branch = (
                self._resolve_branch(tenant_id, data["branch_id"])
                if data["branch_id"] is not None
                else None
            )
            department.branch_id = branch.branch_id if branch else None

        # ---- parent (nullable; cycle + same-organization + depth)
        if "parent_department_id" in data:
            if data["parent_department_id"] is None:
                department.parent_department_id = None
            else:
                parent = self._resolve_parent(
                    tenant_id,
                    data["parent_department_id"],
                    department_id=department.department_id,
                    organization_id=department.organization_id,
                )
                self._assert_depth(
                    tenant_id,
                    parent,
                    node_height=self._subtree_height(tenant_id, department.department_id),
                )
                department.parent_department_id = parent.department_id

        if "status" in data and data["status"] is not None:
            self._apply_status(department, data["status"])

        department.version_no += 1
        department.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="DEPARTMENT_REPLACED" if replace else "DEPARTMENT_UPDATED",
            event_category="DEPARTMENT",
            entity_type="department",
            entity_id=department.department_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"fields": sorted(data.keys()), "replace": replace},
        )
        self.db.commit()
        return self._to_response(
            self._get_or_404(tenant_id, department_id),
            warnings=self._recommended_warnings(tenant_id),
        )

    def move(
        self,
        tenant_id: UUID,
        department_id: UUID,
        parent_department_id: Optional[UUID],
        version_no: int,
        actor_id: UUID,
    ) -> DepartmentResponse:
        """Reparent a department (BFS-PF-006 §10 ``PATCH /{id}/move``).

        ``parent_department_id = None`` detaches the department to root level.
        """
        department = self._get_or_404(tenant_id, department_id)
        if department.version_no != version_no:
            raise ConflictError("Department version conflict", req_id=_REQ)

        old_parent_id = department.parent_department_id
        if parent_department_id is None:
            department.parent_department_id = None
        else:
            parent = self._resolve_parent(
                tenant_id,
                parent_department_id,
                department_id=department.department_id,
                organization_id=department.organization_id,
            )
            self._assert_depth(
                tenant_id,
                parent,
                node_height=self._subtree_height(tenant_id, department.department_id),
            )
            department.parent_department_id = parent.department_id

        department.version_no += 1
        department.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="DEPARTMENT_REPARENTED",
            event_category="DEPARTMENT",
            entity_type="department",
            entity_id=department.department_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "old_parent_id": str(old_parent_id) if old_parent_id else None,
                "new_parent_id": (
                    str(department.parent_department_id)
                    if department.parent_department_id
                    else None
                ),
            },
        )
        self.db.commit()
        return self._to_response(
            self._get_or_404(tenant_id, department_id),
            warnings=self._recommended_warnings(tenant_id),
        )

    def soft_delete(self, tenant_id: UUID, department_id: UUID, actor_id: UUID) -> None:
        """Soft delete (BFS-PF-006 §10). Hard DELETE is never used.

        A department with non-deleted child departments cannot be deleted
        (BR-PF-044, DB RESTRICT + service guard). The user-assignment half of
        BR-PF-044 is deferred to PF-008.
        """
        department = self._get_or_404(tenant_id, department_id)
        if self._children_count(tenant_id, department.department_id) > 0:
            raise ValidationAppError(
                "Department has child departments and cannot be deleted (BR-PF-044)",
                req_id="BR-PF-044",
            )
        department.is_deleted = True
        department.is_active = False
        department.version_no += 1
        department.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="DEPARTMENT_DELETED",
            event_category="DEPARTMENT",
            entity_type="department",
            entity_id=department.department_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"code": department.department_code},
        )
        self.db.commit()
