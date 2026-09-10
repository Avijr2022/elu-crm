from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.models.crm import Lead
from app.models.pf import Tenant
from app.repositories.crm.lead_repository import LeadRepository
from app.repositories.pf.user_repository import TenantRepository
from app.schemas.crm.lead import (
    LEAD_STATUSES,
    LeadCreate,
    LeadListResponse,
    LeadResponse,
    LeadUpdate,
)

QUALIFY_FROM = frozenset({"NEW", "UNDER_QUALIFICATION", "NURTURE", "ON_HOLD"})
TERMINAL_STATUSES = frozenset({"CONVERTED", "DISQUALIFIED"})


class LeadService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LeadRepository(db)
        self.tenants = TenantRepository(db)

    def list_leads(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        search: str | None = None,
    ) -> LeadListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        items, total = self.repo.list(
            tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            search=search,
        )
        return LeadListResponse(
            items=[LeadResponse.model_validate(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_lead(self, tenant_id: UUID, lead_id: UUID) -> LeadResponse:
        lead = self.repo.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-001")
        return LeadResponse.model_validate(lead)

    def create_lead(
        self, tenant_id: UUID, owner_id: UUID, payload: LeadCreate
    ) -> LeadResponse:
        status = (payload.status or "NEW").upper()
        if status not in LEAD_STATUSES:
            status = "NEW"

        lead = Lead(
            lead_id=uuid4(),
            tenant_id=tenant_id,
            lead_number=self._next_lead_number(tenant_id),
            full_name=payload.full_name.strip(),
            company_name=(payload.company_name or "").strip() or None,
            email=str(payload.email).lower() if payload.email else None,
            phone=(payload.phone or "").strip() or None,
            status=status,
            estimated_value=payload.estimated_value or Decimal("0"),
            currency_code=(payload.currency_code or "INR").upper(),
            owner_id=owner_id,
            notes=payload.notes,
        )
        return LeadResponse.model_validate(self.repo.add(lead))

    def update_lead(
        self, tenant_id: UUID, lead_id: UUID, payload: LeadUpdate
    ) -> LeadResponse:
        lead = self.repo.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-001")

        data = payload.model_dump(exclude_unset=True)
        if "full_name" in data and data["full_name"] is not None:
            lead.full_name = data["full_name"].strip()
        if "company_name" in data:
            company = data["company_name"]
            lead.company_name = company.strip() if company else None
        if "email" in data:
            lead.email = str(data["email"]).lower() if data["email"] else None
        if "phone" in data:
            phone = data["phone"]
            lead.phone = phone.strip() if phone else None
        if "status" in data and data["status"]:
            status = data["status"].upper()
            if status not in LEAD_STATUSES:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Invalid status '{data['status']}'",
                    422,
                    req_id="REQ-CRM-001",
                )
            lead.status = status
        if "estimated_value" in data and data["estimated_value"] is not None:
            lead.estimated_value = data["estimated_value"]
        if "currency_code" in data and data["currency_code"]:
            lead.currency_code = data["currency_code"].upper()
        if "notes" in data:
            lead.notes = data["notes"]

        return LeadResponse.model_validate(self.repo.save(lead))

    def qualify_lead(self, tenant_id: UUID, lead_id: UUID) -> LeadResponse:
        lead = self.repo.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-001")
        status = lead.status.upper()
        if status in TERMINAL_STATUSES:
            raise AppError(
                "VALIDATION_ERROR",
                f"Cannot qualify lead in status '{status}'",
                422,
                req_id="REQ-CRM-001",
            )
        if status not in QUALIFY_FROM:
            raise AppError(
                "VALIDATION_ERROR",
                f"Lead status '{status}' cannot transition to QUALIFIED",
                422,
                req_id="REQ-CRM-001",
            )
        lead.status = "QUALIFIED"
        return LeadResponse.model_validate(self.repo.save(lead))

    def disqualify_lead(
        self, tenant_id: UUID, lead_id: UUID, reason: str
    ) -> LeadResponse:
        lead = self.repo.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-001")
        status = lead.status.upper()
        if status in TERMINAL_STATUSES:
            raise AppError(
                "VALIDATION_ERROR",
                f"Cannot disqualify lead in status '{status}'",
                422,
                req_id="REQ-CRM-001",
            )
        lead.status = "DISQUALIFIED"
        note = f"[Disqualified] {reason.strip()}"
        lead.notes = f"{lead.notes}\n{note}".strip() if lead.notes else note
        return LeadResponse.model_validate(self.repo.save(lead))

    def delete_lead(self, tenant_id: UUID, lead_id: UUID) -> None:
        lead = self.repo.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-001")
        lead.is_deleted = True
        lead.is_active = False
        self.repo.save(lead)

    def _next_lead_number(self, tenant_id: UUID) -> str:
        from datetime import date

        tenant: Tenant | None = self.tenants.get_by_id(tenant_id)
        if tenant and tenant.tenant_name:
            letters = "".join(ch for ch in tenant.tenant_name if ch.isalpha())
            prefix = (letters[:3] or "EUP").upper()
        else:
            prefix = "EUP"
        year = date.today().year
        seq = self.repo.next_sequence(tenant_id, year)
        return f"{prefix}-LD-{year}-{seq:05d}"
