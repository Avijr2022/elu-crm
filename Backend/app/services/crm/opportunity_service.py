from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.crm import Lead, Opportunity
from app.models.pf import Tenant
from app.repositories.crm.lead_repository import LeadRepository
from app.repositories.crm.lookup_repository import LookupRepository
from app.repositories.crm.opportunity_repository import OpportunityRepository
from app.repositories.pf.user_repository import TenantRepository
from app.services.crm.activity_service import ActivityService
from app.services.crm.customer_service import CustomerService
from app.schemas.crm.opportunity import (
    OPPORTUNITY_STATUSES,
    PIPELINE_STAGES,
    STAGE_PROBABILITY,
    OpportunityCreate,
    OpportunityListResponse,
    OpportunityResponse,
    OpportunityUpdate,
    PipelineResponse,
    PipelineStageBucket,
    StageUpdate,
)


class OpportunityService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = OpportunityRepository(db)
        self.leads = LeadRepository(db)
        self.tenants = TenantRepository(db)
        self.lookups = LookupRepository(db)

    def _pipeline_stage_codes(self, tenant_id: UUID) -> list[str]:
        rows = self.lookups.list_opportunity_stages(tenant_id, active_only=True)
        if rows:
            return [s.code for s in rows]
        return list(PIPELINE_STAGES)

    def _stage_probability(self, tenant_id: UUID, code: str) -> int:
        row = next(
            (
                s
                for s in self.lookups.list_opportunity_stages(tenant_id, active_only=False)
                if s.code == code
            ),
            None,
        )
        if row is not None:
            return row.default_probability
        return STAGE_PROBABILITY.get(code, 0)

    def list_opportunities(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        stage: str | None = None,
        status: str | None = None,
        search: str | None = None,
        customer_id: UUID | None = None,
    ) -> OpportunityListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        items, total = self.repo.list(
            tenant_id,
            page=page,
            page_size=page_size,
            stage=stage,
            status=status,
            search=search,
            customer_id=customer_id,
        )
        return OpportunityListResponse(
            items=[self._to_response(i) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_opportunity(self, tenant_id: UUID, opportunity_id: UUID) -> OpportunityResponse:
        opp = self.repo.get_by_id(tenant_id, opportunity_id)
        if opp is None:
            raise NotFoundError("Opportunity not found", req_id="REQ-CRM-013")
        return self._to_response(opp)

    def create_opportunity(
        self, tenant_id: UUID, owner_id: UUID, payload: OpportunityCreate
    ) -> OpportunityResponse:
        stage = (payload.stage or "QUALIFICATION").upper()
        if stage not in PIPELINE_STAGES:
            stage = "QUALIFICATION"
        status = (payload.status or "OPEN").upper()
        if status not in OPPORTUNITY_STATUSES:
            status = "OPEN"

        if payload.source_lead_id:
            lead = self.leads.get_by_id(tenant_id, payload.source_lead_id)
            if lead is None:
                raise NotFoundError("Source lead not found", req_id="REQ-CRM-013")

        opp = Opportunity(
            opportunity_id=uuid4(),
            tenant_id=tenant_id,
            opportunity_number=self._next_number(tenant_id),
            name=payload.name.strip(),
            company_name=(payload.company_name or "").strip() or None,
            stage=stage,
            status=status,
            opportunity_value=payload.opportunity_value or Decimal("0"),
            currency_code=(payload.currency_code or "INR").upper(),
            probability=STAGE_PROBABILITY.get(stage, 10),
            expected_close_date=payload.expected_close_date,
            source_lead_id=payload.source_lead_id,
            owner_id=owner_id,
            notes=payload.notes,
        )
        return self._to_response(self.repo.add(opp))

    def update_opportunity(
        self,
        tenant_id: UUID,
        opportunity_id: UUID,
        payload: OpportunityUpdate,
        *,
        actor_id: UUID | None = None,
        can_approve: bool = False,
    ) -> OpportunityResponse:
        opp = self.repo.get_by_id(tenant_id, opportunity_id)
        if opp is None:
            raise NotFoundError("Opportunity not found", req_id="REQ-CRM-013")
        if opp.status == "CLOSED_WON":
            raise AppError(
                "VALIDATION_ERROR",
                "Closed won opportunities cannot be edited",
                422,
                req_id="REQ-CRM-013",
            )

        data = payload.model_dump(exclude_unset=True)
        if "name" in data and data["name"] is not None:
            opp.name = data["name"].strip()
        if "company_name" in data:
            company = data["company_name"]
            opp.company_name = company.strip() if company else None
        if "opportunity_value" in data and data["opportunity_value"] is not None:
            opp.opportunity_value = data["opportunity_value"]
        if "currency_code" in data and data["currency_code"]:
            opp.currency_code = data["currency_code"].upper()
        if "expected_close_date" in data:
            opp.expected_close_date = data["expected_close_date"]
        if "notes" in data:
            opp.notes = data["notes"]
        if "loss_reason" in data:
            opp.loss_reason = data["loss_reason"]
        if "status" in data and data["status"]:
            status = data["status"].upper()
            if status not in OPPORTUNITY_STATUSES:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Invalid status '{data['status']}'",
                    422,
                    req_id="REQ-CRM-013",
                )
            if status == "CLOSED_WON" and opp.status != "CLOSED_WON":
                if not can_approve:
                    raise ForbiddenError(
                        "opportunity.approve permission required to close won",
                        req_id="REQ-CRM-RBAC",
                    )
                owner = actor_id or opp.owner_id
                if owner is None:
                    raise AppError(
                        "VALIDATION_ERROR",
                        "Opportunity owner required to close won",
                        422,
                        req_id="REQ-CRM-013",
                    )
                customer = CustomerService(self.db).create_from_opportunity(
                    tenant_id, owner, opp
                )
                opp.customer_id = customer.customer_id
                ActivityService(self.db).log_system_event(
                    tenant_id,
                    owner,
                    entity_type="OPPORTUNITY",
                    entity_id=opp.opportunity_id,
                    subject="Closed Won",
                    description=f"Customer {customer.customer_number} created",
                )
            elif status == "CLOSED_LOST" and opp.status != "CLOSED_LOST" and actor_id:
                ActivityService(self.db).log_system_event(
                    tenant_id,
                    actor_id,
                    entity_type="OPPORTUNITY",
                    entity_id=opp.opportunity_id,
                    subject="Closed Lost",
                    description=data.get("loss_reason") or opp.loss_reason,
                )
            opp.status = status
        if "stage" in data and data["stage"]:
            # Prefer dedicated stage endpoint for gated advances; allow direct set only if same
            stage = data["stage"].upper()
            valid_stages = self._pipeline_stage_codes(tenant_id)
            if stage not in valid_stages:
                raise AppError(
                    "VALIDATION_ERROR",
                    f"Invalid stage '{data['stage']}'",
                    422,
                    req_id="REQ-CRM-014",
                )
            opp.stage = stage
            opp.probability = self._stage_probability(tenant_id, stage)

        return self._to_response(self.repo.save(opp))

    def advance_stage(
        self, tenant_id: UUID, opportunity_id: UUID, payload: StageUpdate
    ) -> OpportunityResponse:
        opp = self.repo.get_by_id(tenant_id, opportunity_id)
        if opp is None:
            raise NotFoundError("Opportunity not found", req_id="REQ-CRM-014")
        if opp.status not in {"OPEN", "REOPENED"}:
            raise AppError(
                "VALIDATION_ERROR",
                f"Cannot advance stage when status is {opp.status}",
                422,
                req_id="REQ-CRM-014",
            )

        target = payload.stage.upper()
        pipeline = self._pipeline_stage_codes(tenant_id)
        if target not in pipeline:
            raise AppError(
                "VALIDATION_ERROR",
                f"Invalid stage '{payload.stage}'",
                422,
                req_id="REQ-CRM-014",
            )

        current_idx = pipeline.index(opp.stage) if opp.stage in pipeline else -1
        target_idx = pipeline.index(target)
        if target_idx != current_idx + 1:
            raise AppError(
                "VALIDATION_ERROR",
                "Stage skip not allowed; advance one stage at a time (BR-CRM-024)",
                422,
                req_id="REQ-CRM-023",
            )

        # Gate: QUALIFICATION → TECHNICAL_EVAL requires value > 0
        if opp.stage == "QUALIFICATION" and target == "TECHNICAL_EVAL":
            if Decimal(opp.opportunity_value or 0) <= 0:
                raise AppError(
                    "VALIDATION_ERROR",
                    "opportunity_value must be > 0 to leave QUALIFICATION (BR-CRM-022)",
                    422,
                    req_id="REQ-CRM-014",
                )

        opp.stage = target
        opp.probability = self._stage_probability(tenant_id, target)
        return self._to_response(self.repo.save(opp))

    def pipeline(self, tenant_id: UUID) -> PipelineResponse:
        items = self.repo.list_open_pipeline(tenant_id)
        stage_codes = self._pipeline_stage_codes(tenant_id)
        by_stage: dict[str, list[Opportunity]] = {s: [] for s in stage_codes}
        for item in items:
            by_stage.setdefault(item.stage, []).append(item)

        buckets: list[PipelineStageBucket] = []
        for stage in stage_codes:
            stage_items = by_stage.get(stage, [])
            responses = [self._to_response(i) for i in stage_items]
            total_value = sum((r.opportunity_value for r in responses), Decimal("0"))
            weighted = sum((r.weighted_value for r in responses), Decimal("0"))
            buckets.append(
                PipelineStageBucket(
                    stage=stage,
                    count=len(responses),
                    total_value=total_value,
                    weighted_value=weighted,
                    items=responses,
                )
            )
        return PipelineResponse(stages=buckets)

    def delete_opportunity(self, tenant_id: UUID, opportunity_id: UUID) -> None:
        opp = self.repo.get_by_id(tenant_id, opportunity_id)
        if opp is None:
            raise NotFoundError("Opportunity not found", req_id="REQ-CRM-013")
        opp.is_deleted = True
        opp.is_active = False
        self.repo.save(opp)

    def convert_from_lead(
        self, tenant_id: UUID, owner_id: UUID, lead_id: UUID
    ) -> OpportunityResponse:
        lead = self.leads.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-002")
        if lead.status == "CONVERTED":
            raise AppError(
                "CONFLICT",
                "Lead is already converted",
                409,
                req_id="REQ-CRM-002",
            )
        if lead.status == "DISQUALIFIED":
            raise AppError(
                "VALIDATION_ERROR",
                "Disqualified leads cannot be converted",
                422,
                req_id="REQ-CRM-002",
            )

        name = f"{lead.company_name or lead.full_name} Opportunity"
        payload = OpportunityCreate(
            name=name[:250],
            company_name=lead.company_name,
            opportunity_value=lead.estimated_value or Decimal("0"),
            currency_code=lead.currency_code or "INR",
            source_lead_id=lead.lead_id,
            notes=f"Converted from lead {lead.lead_number}",
        )
        opp = self.create_opportunity(tenant_id, owner_id, payload)
        lead.status = "CONVERTED"
        self.leads.save(lead)
        return opp

    def _to_response(self, opp: Opportunity) -> OpportunityResponse:
        base = OpportunityResponse.model_validate(opp)
        weighted = (Decimal(opp.opportunity_value or 0) * Decimal(opp.probability or 0)) / Decimal(
            100
        )
        return base.model_copy(update={"weighted_value": weighted.quantize(Decimal("0.01"))})

    def _next_number(self, tenant_id: UUID) -> str:
        tenant: Tenant | None = self.tenants.get_by_id(tenant_id)
        if tenant and tenant.tenant_name:
            letters = "".join(ch for ch in tenant.tenant_name if ch.isalpha())
            prefix = (letters[:3] or "EUP").upper()
        else:
            prefix = "EUP"
        year = date.today().year
        seq = self.repo.next_sequence(tenant_id, year)
        return f"{prefix}-OPP-{year}-{seq:05d}"
