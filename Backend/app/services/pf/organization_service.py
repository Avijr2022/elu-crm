"""PF-004 Organization Management service (ELU-BFS-PF-004)."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationAppError
from app.models.pf import AuditEvent, Organization, TenantAddress
from app.schemas.pf.organization import (
    OrganizationCreate,
    OrganizationHierarchyNode,
    OrganizationHistoryItem,
    OrganizationHistoryResponse,
    OrganizationListResponse,
    OrganizationResponse,
    OrganizationUpdate,
)
from app.services.pf.audit_service import write_audit_event


_TAX_KEYS = ("gstin", "pan", "tan")

# HD-03: exported tax identifiers are masked; the value chosen matches the existing
# audit-payload convention (``_mask_tax_payload`` replaces GSTIN/PAN/TAN with ***).
MASKED_TAX_VALUE = "***"


def _mask_tax_value(value: Any) -> Any:
    """Return the masking token for a present tax identifier, else the value as-is."""
    return MASKED_TAX_VALUE if value else value


def _mask_tax_payload(payload: Optional[dict[str, Any]]) -> Optional[dict[str, Any]]:
    if not payload:
        return payload
    out = dict(payload)
    for k in _TAX_KEYS:
        if out.get(k):
            out[k] = "***"
    return out


def require_org_read(role_code: str) -> None:
    if role_code not in {"PLATFORM_ADMIN", "TENANT_ADMIN", "FINANCE_USER", "SALES_MANAGER"}:
        raise ForbiddenError("Organization read not permitted", req_id="PF-004")


def require_org_write(role_code: str) -> None:
    # BFS-PF-004 §12: Platform Admin is read-only; Tenant Admin mutates.
    if role_code != "TENANT_ADMIN":
        raise ForbiddenError("Organization write not permitted", req_id="PF-004")


# HD-02: organization export is permitted for Tenant Admin and Finance User only.
_ORG_EXPORT_ROLES = frozenset({"TENANT_ADMIN", "FINANCE_USER"})


def require_org_export(role_code: str) -> None:
    """Organization export matrix (BFS-PF-004 §12 / HD-02).

    Implemented as an explicit role gate rather than ``require_permission`` because
    ``app.core.rbac.has_permission`` grants PLATFORM_ADMIN a universal bypass, which
    would contradict the read-only Platform Admin rule. Runtime permission-grain
    enforcement for the PF surface remains deferred to PF-009 (HD-01).
    """
    if role_code not in _ORG_EXPORT_ROLES:
        raise ForbiddenError("Organization export not permitted", req_id="PF-004")


class OrganizationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _to_response(self, org: Organization) -> OrganizationResponse:
        return OrganizationResponse(
            id=org.organization_id,
            tenant_id=org.tenant_id,
            code=org.organization_code,
            name=org.organization_name,
            legal_name=org.legal_name,
            short_name=org.short_name,
            organization_type=org.organization_type,
            parent_organization_id=org.parent_organization_id,
            is_root=bool(org.is_root),
            level=int(org.level or 0),
            gstin=org.gstin,
            pan=org.pan,
            tan=org.tan,
            cin=org.cin,
            registration_number=org.registration_number,
            tax_registration_type=org.tax_registration_type,
            date_of_incorporation=org.date_of_incorporation,
            default_currency_code=org.default_currency_code or "INR",
            fiscal_year_start_month=int(org.fiscal_year_start_month or 4),
            email=org.email,
            phone=org.phone,
            website=org.website,
            address_id=org.address_id,
            status=org.status,
            version_no=org.version_no,
            created_on=org.created_on,
            modified_on=org.modified_on,
        )

    def _load(self, tenant_id: UUID, org_id: UUID) -> Optional[Organization]:
        return self.db.scalars(
            select(Organization).where(
                Organization.organization_id == org_id,
                Organization.tenant_id == tenant_id,
                Organization.is_deleted.is_(False),
            )
        ).first()

    def _resolve_address_id(
        self, tenant_id: UUID, address_id: Optional[UUID]
    ) -> Optional[UUID]:
        if address_id is None:
            return None
        addr = self.db.scalars(
            select(TenantAddress).where(
                TenantAddress.id == address_id,
                TenantAddress.tenant_id == tenant_id,
                TenantAddress.is_deleted.is_(False),
            )
        ).first()
        if addr is None:
            raise ValidationAppError(
                "address_id not found for this tenant", req_id="PF-004"
            )
        return address_id

    def _apply_status(self, org: Organization, new_status: str) -> None:
        new_status = new_status.upper()
        allowed = {
            "DRAFT": {"ACTIVE"},
            "ACTIVE": {"INACTIVE", "MERGED"},
            "INACTIVE": {"ACTIVE", "ARCHIVED"},
            "MERGED": set(),
            "ARCHIVED": set(),
        }
        if new_status != org.status and new_status not in allowed.get(org.status, set()):
            raise ValidationAppError(
                f"Invalid organization status transition {org.status} → {new_status}",
                req_id="PF-004",
            )
        org.status = new_status

    def list_orgs(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
    ) -> OrganizationListResponse:
        q = select(Organization).where(
            Organization.tenant_id == tenant_id,
            Organization.is_deleted.is_(False),
        )
        if status:
            q = q.where(Organization.status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Organization.organization_code.ilike(like),
                    Organization.organization_name.ilike(like),
                    Organization.legal_name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        order = Organization.is_root.desc(), Organization.organization_name.asc()
        if sort:
            key = sort.lstrip("-").lower()
            col_map = {
                "name": Organization.organization_name,
                "code": Organization.organization_code,
                "status": Organization.status,
                "created_on": Organization.created_on,
            }
            col = col_map.get(key)
            if col is not None:
                order = (col.desc() if sort.startswith("-") else col.asc(),)
        items = list(
            self.db.scalars(
                q.order_by(*order)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return OrganizationListResponse(
            items=[self._to_response(o) for o in items],
            page=page,
            page_size=page_size,
            total=int(total),
        )

    def get(self, tenant_id: UUID, org_id: UUID) -> OrganizationResponse:
        org = self._load(tenant_id, org_id)
        if org is None:
            raise NotFoundError("Organization not found", req_id="PF-004")
        return self._to_response(org)

    def get_root(self, tenant_id: UUID) -> OrganizationResponse:
        org = self.db.scalars(
            select(Organization).where(
                Organization.tenant_id == tenant_id,
                Organization.is_root.is_(True),
                Organization.is_deleted.is_(False),
            )
        ).first()
        if org is None:
            raise NotFoundError("Root organization not found", req_id="BR-PF-028")
        return self._to_response(org)

    def create(
        self, tenant_id: UUID, payload: OrganizationCreate, actor_id: UUID
    ) -> OrganizationResponse:
        # v1: additional orgs are children only (exactly one ROOT — BR-PF-028)
        if payload.parent_organization_id is None:
            raise ValidationAppError(
                "Creating a second ROOT is not allowed; provide parent_organization_id "
                "(BR-PF-028). Multi-org roots deferred to Enterprise v2.",
                req_id="BR-PF-028",
            )
        parent = self._load(tenant_id, payload.parent_organization_id)
        if parent is None:
            raise NotFoundError("Parent organization not found", req_id="PF-004")

        exists = self.db.scalars(
            select(Organization).where(
                Organization.tenant_id == tenant_id,
                Organization.organization_code == payload.code,
                Organization.is_deleted.is_(False),
            )
        ).first()
        if exists:
            raise ConflictError("Organization code already exists", req_id="BR-PF-029")

        org = Organization(
            organization_id=uuid4(),
            tenant_id=tenant_id,
            parent_organization_id=parent.organization_id,
            organization_code=payload.code,
            organization_name=payload.name,
            legal_name=payload.legal_name or payload.name,
            short_name=payload.short_name,
            organization_type=payload.organization_type,
            registration_number=payload.registration_number,
            cin=payload.cin,
            date_of_incorporation=payload.date_of_incorporation,
            gstin=payload.gstin,
            pan=payload.pan,
            tan=payload.tan,
            tax_registration_type=payload.tax_registration_type,
            is_root=False,
            level=int(parent.level or 0) + 1,
            default_currency_code=payload.default_currency_code.upper(),
            fiscal_year_start_month=payload.fiscal_year_start_month,
            email=str(payload.email).lower() if payload.email else None,
            phone=payload.phone,
            website=payload.website,
            address_id=self._resolve_address_id(tenant_id, payload.address_id),
            status=payload.status.upper(),
            created_by=actor_id,
            version_no=1,
        )
        self.db.add(org)
        write_audit_event(
            self.db,
            event_type="ORGANIZATION_CREATED",
            event_category="ORGANIZATION",
            entity_type="organization",
            entity_id=org.organization_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload=_mask_tax_payload(
                {
                    "code": org.organization_code,
                    "parent_id": str(parent.organization_id),
                    "gstin": org.gstin,
                    "pan": org.pan,
                }
            ),
        )
        self.db.commit()
        return self._to_response(self._load(tenant_id, org.organization_id))  # type: ignore[arg-type]

    def update(
        self,
        tenant_id: UUID,
        org_id: UUID,
        payload: OrganizationUpdate,
        actor_id: UUID,
        *,
        replace: bool = False,
    ) -> OrganizationResponse:
        org = self._load(tenant_id, org_id)
        if org is None:
            raise NotFoundError("Organization not found", req_id="PF-004")
        if org.version_no != payload.version_no:
            raise ConflictError("Organization version conflict", req_id="PF-004")

        data = (
            payload.model_dump(exclude={"version_no"})
            if replace
            else payload.model_dump(exclude_unset=True, exclude={"version_no"})
        )
        if "name" in data and data["name"] is not None:
            org.organization_name = data["name"]
        elif replace:
            raise ValidationAppError("name is required on PUT", req_id="PF-004")
        if "legal_name" in data:
            org.legal_name = data["legal_name"]
        if "short_name" in data:
            org.short_name = data["short_name"]
        if "organization_type" in data and data["organization_type"] is not None:
            org.organization_type = data["organization_type"]
        if "email" in data:
            org.email = str(data["email"]).lower() if data["email"] else None
        if "phone" in data:
            org.phone = data["phone"]
        if "website" in data:
            org.website = data["website"]
        if "gstin" in data:
            org.gstin = data["gstin"]
        if "pan" in data:
            org.pan = data["pan"]
        if "tan" in data:
            org.tan = data["tan"]
        if "cin" in data:
            org.cin = data["cin"]
        if "registration_number" in data:
            org.registration_number = data["registration_number"]
        if "tax_registration_type" in data:
            org.tax_registration_type = data["tax_registration_type"]
        if "date_of_incorporation" in data:
            org.date_of_incorporation = data["date_of_incorporation"]
        if "default_currency_code" in data and data["default_currency_code"]:
            org.default_currency_code = data["default_currency_code"].upper()
        if "fiscal_year_start_month" in data and data["fiscal_year_start_month"] is not None:
            month = int(data["fiscal_year_start_month"])
            if month < 1 or month > 12:
                raise ValidationAppError(
                    "fiscal_year_start_month must be 1–12", req_id="BR-PF-033"
                )
            org.fiscal_year_start_month = month
        if "address_id" in data:
            org.address_id = self._resolve_address_id(tenant_id, data["address_id"])
        if "status" in data and data["status"] is not None:
            self._apply_status(org, data["status"])

        org.version_no += 1
        org.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="ORGANIZATION_REPLACED" if replace else "ORGANIZATION_UPDATED",
            event_category="ORGANIZATION",
            entity_type="organization",
            entity_id=org.organization_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
            payload=_mask_tax_payload({"fields": list(data.keys()), "replace": replace}),
        )
        self.db.commit()
        return self._to_response(self._load(tenant_id, org_id))  # type: ignore[arg-type]

    def history(
        self, tenant_id: UUID, org_id: UUID, *, limit: int = 50
    ) -> OrganizationHistoryResponse:
        org = self._load(tenant_id, org_id)
        if org is None:
            raise NotFoundError("Organization not found", req_id="PF-004")
        rows = list(
            self.db.scalars(
                select(AuditEvent)
                .where(
                    AuditEvent.entity_type == "organization",
                    AuditEvent.entity_id == org_id,
                    or_(
                        AuditEvent.tenant_id == tenant_id,
                        AuditEvent.tenant_id.is_(None),
                    ),
                )
                .order_by(AuditEvent.created_on.desc())
                .limit(limit)
            ).all()
        )
        return OrganizationHistoryResponse(
            items=[
                OrganizationHistoryItem(
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

    def soft_delete(self, tenant_id: UUID, org_id: UUID, actor_id: UUID) -> None:
        org = self._load(tenant_id, org_id)
        if org is None:
            raise NotFoundError("Organization not found", req_id="PF-004")
        if org.is_root:
            raise ValidationAppError(
                "ROOT organization cannot be deleted (BR-PF-031)", req_id="BR-PF-031"
            )
        org.is_deleted = True
        org.is_active = False
        org.version_no += 1
        org.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="ORGANIZATION_DELETED",
            event_category="ORGANIZATION",
            entity_type="organization",
            entity_id=org.organization_id,
            actor_id=actor_id,
            tenant_id=tenant_id,
        )
        self.db.commit()

    def hierarchy(self, tenant_id: UUID, org_id: Optional[UUID] = None) -> OrganizationHierarchyNode:
        orgs = list(
            self.db.scalars(
                select(Organization).where(
                    Organization.tenant_id == tenant_id,
                    Organization.is_deleted.is_(False),
                )
            ).all()
        )
        if not orgs:
            raise NotFoundError("No organizations found", req_id="PF-004")

        by_id = {o.organization_id: o for o in orgs}
        children_map: dict[Optional[UUID], list[Organization]] = {}
        for o in orgs:
            children_map.setdefault(o.parent_organization_id, []).append(o)

        root_id = org_id
        if root_id is None:
            root = next((o for o in orgs if o.is_root), orgs[0])
            root_id = root.organization_id
        if root_id not in by_id:
            raise NotFoundError("Organization not found", req_id="PF-004")

        def build(oid: UUID) -> OrganizationHierarchyNode:
            o = by_id[oid]
            kids = sorted(
                children_map.get(oid, []),
                key=lambda x: x.organization_name,
            )
            return OrganizationHierarchyNode(
                id=o.organization_id,
                code=o.organization_code,
                name=o.organization_name,
                is_root=bool(o.is_root),
                level=int(o.level or 0),
                status=o.status,
                children=[build(c.organization_id) for c in kids],
            )

        return build(root_id)

    def export_rows(self, tenant_id: UUID) -> list[dict]:
        items = self.list_orgs(tenant_id, page=1, page_size=500).items
        return [
            {
                "id": str(i.id),
                "code": i.code,
                "name": i.name,
                "legal_name": i.legal_name,
                "is_root": i.is_root,
                "status": i.status,
                "gstin": _mask_tax_value(i.gstin),
                "pan": _mask_tax_value(i.pan),
                "currency": i.default_currency_code,
                "fy_start_month": i.fiscal_year_start_month,
            }
            for i in items
        ]
