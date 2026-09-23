"""PF-007 Business Unit Management service (ELU-BFS-PF-007).

Implements the backend functional layer for Business Unit Management: CRUD, the
three-state lifecycle, tenant-scoped search/pagination, JSON export and the approved
Batch-1 business rules.

Authorisation is enforced at **permission grain** (PF-009 Batch 2): the seeded
``BUSINESS_UNIT_PERMISSION_MATRIX`` in ``app/db/seed.py`` is authoritative for every role,
so the approved PF-007 §12 matrix (incl. D2/D3) is applied through
``app.core.rbac.has_permission`` (Platform Admin holds no ``business_unit.*`` grain).

Approved human scope decisions (D1-D11, recorded 2026-09-16) applied here:
  * D1  — exactly the 8 BFS §10 endpoints; **no history API** is implemented.
  * D2  — ``business_unit.export`` is Tenant Admin only.
  * D3  — Project Manager is read-only; project-to-BU linkage is **not** implemented.
  * D4  — ``BR-PF-048``: ``bu_manager_user_id``, when supplied, must identify an ACTIVE
          user in the same tenant (service-level validation). No ``users.business_unit_id``
          linkage is introduced — that remains PF-008.
  * D5  — ``BR-PF-050``: Professional = 20 business units, Enterprise = unlimited, read
          from the existing ``core.edition_limit`` mechanism (never hard-coded).
  * D6  — opportunity-to-BU linkage is authorized but **deliberately not implemented in
          this batch**; no project or invoice table/relationship is touched.
  * D7  — ``organization_id`` is assigned on creation and immutable afterwards.
  * D8  — no reporting engine and no export formatting: export stays JSON, exactly like
          PF-005/PF-006. The minimum AC-PF-007-03 aggregation belongs to a later batch.
  * D9  — field types/lengths follow established PF conventions (see the schema module);
          no rule that the specification does not define is invented.
  * D10 — backend only; no Flutter work.
  * D11 — ``core.business_unit`` with tenant RLS and the partial unique active-code index.

EXPLICITLY DEFERRED (must not be implemented here):
  * ``business_unit -> opportunity`` (CRM) FK + opportunity tagging      -> later batch (D6)
  * ``business_unit -> project`` (PRJ) / ``-> invoice`` (FIN) FKs        -> deferred (D6)
  * ``users.business_unit_id`` / user <-> BU assignment                  -> PF-008
  * BU-manager *linkage* (a ``users`` column)                            -> PF-008
  * NTF-PF-007-* notifications                                           -> deferred
  * RPT-PF-007-01/02 reports, XLSX/PDF formatting                        -> deferred (D8)
  * Business Unit History UI / history endpoint                          -> deferred (D1)
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.core.deps import CurrentUser
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.core.rbac import has_permission
from app.models.pf import BusinessUnit, Edition, Organization, Tenant, User
from app.schemas.pf.business_unit import (
    BusinessUnitCreate,
    BusinessUnitListResponse,
    BusinessUnitResponse,
    BusinessUnitUpdate,
)
from app.services.pf.audit_service import write_audit_event

_REQ = "PF-007"

# ------------------------------------------------------- permission-grain gates
# BFS-PF-007 §12 (approved matrix incl. D2/D3, mirrored in app/db/seed.py
# BUSINESS_UNIT_PERMISSION_MATRIX). PF-009 Batch 2: the seeded matrix is authoritative
# for every role, so the gates below check the permission grain instead of the role.
_BUSINESS_UNIT_WRITE_CODES = ("business_unit.create", "business_unit.update", "business_unit.delete")
_BUSINESS_UNIT_EXPORT_CODE = "business_unit.export"


def require_business_unit_read(current: CurrentUser) -> None:
    """Business-unit read (BFS-PF-007 §12 + D3) at permission grain."""
    if not has_permission(current, "business_unit.read"):
        raise ForbiddenError("Business unit read not permitted", req_id=_REQ)


def require_business_unit_write(current: CurrentUser) -> None:
    """Business-unit create/update/delete (BFS-PF-007 §12): Tenant Admin only."""
    if not any(has_permission(current, code) for code in _BUSINESS_UNIT_WRITE_CODES):
        raise ForbiddenError("Business unit write not permitted", req_id=_REQ)


def require_business_unit_export(current: CurrentUser) -> None:
    """Business-unit export (D2): Tenant Admin only."""
    if not has_permission(current, _BUSINESS_UNIT_EXPORT_CODE):
        raise ForbiddenError("Business unit export not permitted", req_id=_REQ)


# ------------------------------------------------------------------ constants
# BFS-PF-007 §5 — allowed next states (three-state lifecycle, ARCHIVED terminal).
STATUS_TRANSITIONS: dict[str, set[str]] = {
    "ACTIVE": {"INACTIVE"},
    "INACTIVE": {"ACTIVE", "ARCHIVED"},
    "ARCHIVED": set(),
}

# D5 / BR-PF-050 — the limit is read from core.edition_limit; never hard-coded.
MAX_BUSINESS_UNITS_LIMIT_CODE = "MAX_BUSINESS_UNITS"

# BR-PF-049 basis — a business unit may only be assigned while ACTIVE. Batch 1 defines the
# domain guard only; the opportunity/project assignment call sites arrive in a later batch
# (D6) and remain outside this batch's scope.
ASSIGNABLE_STATUS = "ACTIVE"


class BusinessUnitService:
    def __init__(self, db: Session) -> None:
        self.db = db

    # ------------------------------------------------------------- helpers
    def _to_response(
        self, business_unit: BusinessUnit, *, warnings: Optional[list[str]] = None
    ) -> BusinessUnitResponse:
        return BusinessUnitResponse(
            id=business_unit.business_unit_id,
            tenant_id=business_unit.tenant_id,
            code=business_unit.business_unit_code,
            name=business_unit.business_unit_name,
            organization_id=business_unit.organization_id,
            description=business_unit.description,
            bu_manager_user_id=business_unit.bu_manager_user_id,
            cost_centre_code=business_unit.cost_centre_code,
            revenue_target_annual=business_unit.revenue_target_annual,
            start_date=business_unit.start_date,
            end_date=business_unit.end_date,
            status=business_unit.status,
            warnings=list(warnings or []),
            version_no=business_unit.version_no,
            created_on=business_unit.created_on,
            modified_on=business_unit.modified_on,
        )

    def _load(
        self, tenant_id: UUID, business_unit_id: UUID
    ) -> Optional[BusinessUnit]:
        """Tenant-scoped load of a non-deleted business unit."""
        return self.db.scalars(
            select(BusinessUnit).where(
                BusinessUnit.business_unit_id == business_unit_id,
                BusinessUnit.tenant_id == tenant_id,
                BusinessUnit.is_deleted.is_(False),
            )
        ).first()

    def _get_or_404(self, tenant_id: UUID, business_unit_id: UUID) -> BusinessUnit:
        business_unit = self._load(tenant_id, business_unit_id)
        if business_unit is None:
            # Soft-deleted and foreign-tenant rows are indistinguishable from missing
            # rows on purpose (never confirm another tenant's records — BR-PF-016).
            raise NotFoundError("Business unit not found", req_id=_REQ)
        return business_unit

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
            raise NotFoundError("Organization not found for this tenant", req_id=_REQ)
        return org

    def _resolve_manager(self, tenant_id: UUID, user_id: UUID) -> User:
        """BR-PF-048 (D4) — the BU manager must be an ACTIVE user in the same tenant.

        A foreign-tenant, soft-deleted or unknown user is reported as 404 (never confirms
        another tenant's records); a known same-tenant user that is not ACTIVE is a
        validation error. No ``users`` column is created or modified.
        """
        user = self.db.scalars(
            select(User).where(
                User.user_id == user_id,
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
            )
        ).first()
        if user is None:
            raise NotFoundError("Manager user not found for this tenant", req_id=_REQ)
        if user.account_status != "ACTIVE" or not user.is_active:
            raise ValidationAppError(
                "Business unit manager must be an ACTIVE user in the same tenant "
                "(BR-PF-048)",
                req_id="BR-PF-048",
            )
        return user

    # -------------------------------------------------------------- helpers
    def _assert_code_unique(
        self, tenant_id: UUID, code: str, *, exclude_id: Optional[UUID] = None
    ) -> None:
        """BR-PF-047 service-level pre-check (the partial unique index stays authoritative)."""
        q = select(BusinessUnit).where(
            BusinessUnit.tenant_id == tenant_id,
            BusinessUnit.business_unit_code == code,
            BusinessUnit.is_deleted.is_(False),
        )
        if exclude_id is not None:
            q = q.where(BusinessUnit.business_unit_id != exclude_id)
        if self.db.scalars(q).first() is not None:
            raise ConflictError("Business unit code already exists", req_id="BR-PF-047")

    def _max_business_units_limit(self, tenant_id: UUID) -> Optional[Decimal]:
        """BR-PF-050 — read the tenant edition's ``MAX_BUSINESS_UNITS`` limit.

        The value is read from ``core.edition_limit`` via the tenant's edition (the
        project's existing edition-limit mechanism); it is never hard-coded.
        """
        tenant = self.db.scalars(
            select(Tenant)
            .options(joinedload(Tenant.edition).joinedload(Edition.limits))
            .where(Tenant.tenant_id == tenant_id, Tenant.is_deleted.is_(False))
        ).first()
        if tenant is None or tenant.edition is None:
            return None
        for limit in tenant.edition.limits:
            if limit.limit_code.upper() == MAX_BUSINESS_UNITS_LIMIT_CODE:
                return limit.limit_value
        return None

    def _count_business_units(self, tenant_id: UUID) -> int:
        """Count non-deleted business units (soft-deleted rows never consume the quota)."""
        return int(
            self.db.scalar(
                select(func.count())
                .select_from(BusinessUnit)
                .where(
                    BusinessUnit.tenant_id == tenant_id,
                    BusinessUnit.is_deleted.is_(False),
                )
            )
            or 0
        )

    def _assert_business_unit_quota(self, tenant_id: UUID) -> None:
        limit = self._max_business_units_limit(tenant_id)
        if limit is None:
            return
        if self._count_business_units(tenant_id) >= int(limit):
            raise ValidationAppError(
                f"Maximum business units for this edition reached ({int(limit)}) "
                f"— BR-PF-050",
                req_id="BR-PF-050",
            )

    def _apply_status(self, business_unit: BusinessUnit, new_status: str) -> bool:
        """Apply the BFS-PF-007 §5 lifecycle. Returns True when the status changed."""
        new_status = new_status.upper()
        if new_status == business_unit.status:
            return False
        if new_status not in STATUS_TRANSITIONS.get(business_unit.status, set()):
            raise ValidationAppError(
                f"Invalid business unit status transition "
                f"{business_unit.status} → {new_status}",
                req_id=_REQ,
            )
        business_unit.status = new_status
        return True

    def assert_assignable(self, tenant_id: UUID, business_unit_id: UUID) -> BusinessUnit:
        """BR-PF-049 domain guard — only an ACTIVE business unit may be assigned.

        Batch 1 exposes this guard (and covers it with tests) but deliberately does NOT
        wire it to any opportunity/project path: those linkages are deferred (D6) and no
        project/opportunity table is touched by this batch.
        """
        business_unit = self._get_or_404(tenant_id, business_unit_id)
        if business_unit.status != ASSIGNABLE_STATUS:
            raise ValidationAppError(
                "Inactive or archived business unit cannot be assigned "
                "(BR-PF-049)",
                req_id="BR-PF-049",
            )
        return business_unit

    # ------------------------------------------------------------- read side
    def list_business_units(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        organization_id: Optional[UUID] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> BusinessUnitListResponse:
        """Tenant-scoped business-unit list (BFS-PF-007 §10)."""
        q = select(BusinessUnit).where(
            BusinessUnit.tenant_id == tenant_id,
            BusinessUnit.is_deleted.is_(False),
        )
        if status:
            q = q.where(BusinessUnit.status == status.upper())
        if organization_id:
            q = q.where(BusinessUnit.organization_id == organization_id)
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    BusinessUnit.business_unit_code.ilike(like),
                    BusinessUnit.business_unit_name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        order: tuple[Any, ...] = (BusinessUnit.business_unit_name.asc(),)
        if sort:
            key = sort.lstrip("-").lower()
            col_map = {
                "name": BusinessUnit.business_unit_name,
                "code": BusinessUnit.business_unit_code,
                "status": BusinessUnit.status,
                "created_on": BusinessUnit.created_on,
            }
            col = col_map.get(key)
            if col is not None:
                order = (col.desc() if sort.startswith("-") else col.asc(),)
        items = list(
            self.db.scalars(
                q.order_by(*order).offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        return BusinessUnitListResponse(
            items=[self._to_response(b) for b in items],
            page=page,
            page_size=page_size,
            total=int(total),
            warnings=[],
        )

    def get(self, tenant_id: UUID, business_unit_id: UUID) -> BusinessUnitResponse:
        return self._to_response(self._get_or_404(tenant_id, business_unit_id))

    def export_rows(self, tenant_id: UUID) -> list[dict]:
        """BFS-PF-007 §10 export (JSON only — XLSX/PDF formatting deferred, D8).

        Tenant Admin only (role gate at the API layer, D2).
        """
        items = self.list_business_units(tenant_id, page=1, page_size=500).items
        return [
            {
                "id": str(i.id),
                "code": i.code,
                "name": i.name,
                "organization_id": str(i.organization_id),
                "bu_manager_user_id": (
                    str(i.bu_manager_user_id) if i.bu_manager_user_id else None
                ),
                "cost_centre_code": i.cost_centre_code,
                "revenue_target_annual": (
                    str(i.revenue_target_annual)
                    if i.revenue_target_annual is not None
                    else None
                ),
                "start_date": i.start_date.isoformat() if i.start_date else None,
                "end_date": i.end_date.isoformat() if i.end_date else None,
                "status": i.status,
                "created_on": i.created_on.isoformat() if i.created_on else None,
            }
            for i in items
        ]

    # ------------------------------------------------------------ write side
    def create(
        self, tenant_id: UUID, payload: BusinessUnitCreate, actor_id: UUID
    ) -> BusinessUnitResponse:
        """Create a business unit (BFS-PF-007 §10)."""
        organization = self._resolve_organization(tenant_id, payload.organization_id)
        manager_id: Optional[UUID] = None
        if payload.bu_manager_user_id is not None:
            manager_id = self._resolve_manager(
                tenant_id, payload.bu_manager_user_id
            ).user_id
        self._assert_code_unique(tenant_id, payload.code)
        self._assert_business_unit_quota(tenant_id)

        business_unit = BusinessUnit(
            business_unit_id=uuid4(),
            tenant_id=tenant_id,
            organization_id=organization.organization_id,  # D7: assigned on creation
            business_unit_code=payload.code,
            business_unit_name=payload.name,
            description=payload.description,
            bu_manager_user_id=manager_id,
            cost_centre_code=payload.cost_centre_code,
            revenue_target_annual=payload.revenue_target_annual,
            start_date=payload.start_date,
            end_date=payload.end_date,
            status=payload.status.upper(),
            created_by=actor_id,
            version_no=1,
        )
        self.db.add(business_unit)
        write_audit_event(
            self.db,
            event_type="BUSINESS_UNIT_CREATED",
            event_category="BUSINESS_UNIT",
            entity_type="business_unit",
            entity_id=business_unit.business_unit_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={
                "code": business_unit.business_unit_code,
                "organization_id": str(business_unit.organization_id),
                "manager_user_id": (
                    str(business_unit.bu_manager_user_id)
                    if business_unit.bu_manager_user_id
                    else None
                ),
            },
        )
        self.db.commit()
        return self._to_response(
            self._get_or_404(tenant_id, business_unit.business_unit_id)
        )

    def update(
        self,
        tenant_id: UUID,
        business_unit_id: UUID,
        payload: BusinessUnitUpdate,
        actor_id: UUID,
        *,
        replace: bool = False,
    ) -> BusinessUnitResponse:
        """PATCH/PUT update (BFS-PF-007 §10).

        ``code`` is immutable (not accepted) and ``organization_id`` is immutable after
        creation (D7) — any requested change is rejected explicitly rather than ignored.
        """
        business_unit = self._get_or_404(tenant_id, business_unit_id)
        if business_unit.version_no != payload.version_no:
            raise ConflictError("Business unit version conflict", req_id=_REQ)

        data = (
            payload.model_dump(exclude={"version_no"})
            if replace
            else payload.model_dump(exclude_unset=True, exclude={"version_no"})
        )

        if "name" in data and data["name"] is not None:
            business_unit.business_unit_name = data["name"]
        elif replace:
            raise ValidationAppError("name is required on PUT", req_id=_REQ)

        # ---- organization_id is immutable (D7)
        requested_org = data.get("organization_id")
        if requested_org is not None and requested_org != business_unit.organization_id:
            raise ValidationAppError(
                "organization_id is assigned on creation and cannot be changed (D7)",
                req_id=_REQ,
            )

        if "description" in data:
            business_unit.description = data["description"]
        if "cost_centre_code" in data:
            business_unit.cost_centre_code = data["cost_centre_code"]
        if "revenue_target_annual" in data:
            business_unit.revenue_target_annual = data["revenue_target_annual"]
        if "start_date" in data:
            business_unit.start_date = data["start_date"]
        if "end_date" in data:
            business_unit.end_date = data["end_date"]

        # ---- manager (BR-PF-048 / D4): validate when a value is supplied
        if "bu_manager_user_id" in data:
            manager_id = data["bu_manager_user_id"]
            if manager_id is None:
                business_unit.bu_manager_user_id = None
            else:
                business_unit.bu_manager_user_id = self._resolve_manager(
                    tenant_id, manager_id
                ).user_id

        if "status" in data and data["status"] is not None:
            self._apply_status(business_unit, data["status"])

        business_unit.version_no += 1
        business_unit.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type=(
                "BUSINESS_UNIT_REPLACED" if replace else "BUSINESS_UNIT_UPDATED"
            ),
            event_category="BUSINESS_UNIT",
            entity_type="business_unit",
            entity_id=business_unit.business_unit_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"fields": sorted(data.keys()), "replace": replace},
        )
        self.db.commit()
        return self._to_response(self._get_or_404(tenant_id, business_unit_id))

    def soft_delete(
        self, tenant_id: UUID, business_unit_id: UUID, actor_id: UUID
    ) -> None:
        """Soft delete (BFS-PF-007 §10). Hard DELETE is never used."""
        business_unit = self._get_or_404(tenant_id, business_unit_id)
        business_unit.is_deleted = True
        business_unit.is_active = False
        business_unit.version_no += 1
        business_unit.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="BUSINESS_UNIT_DELETED",
            event_category="BUSINESS_UNIT",
            entity_type="business_unit",
            entity_id=business_unit.business_unit_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload={"code": business_unit.business_unit_code},
        )
        self.db.commit()
