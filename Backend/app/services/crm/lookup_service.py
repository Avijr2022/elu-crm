from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.deps import CurrentUser
from app.core.exceptions import AppError, ForbiddenError
from app.models.crm import ActivityType, ActivityOutcome, OpportunityStage
from app.repositories.crm.lookup_repository import LookupRepository
from app.schemas.crm.activity import ACTIVITY_STATUSES
from app.schemas.crm.lead import LEAD_STATUSES
from app.schemas.crm.lookup import (
    ActivityTypeCreate,
    ActivityTypeListResponse,
    ActivityTypeResponse,
    ActivityTypeUpdate,
    ActivityOutcomeListResponse,
    ActivityOutcomeResponse,
    ActivityOutcomeCreate,
    ActivityOutcomeUpdate,
    CrmLookupsResponse,
    OpportunityStageListResponse,
    OpportunityStageCreate,
    OpportunityStageReorder,
    OpportunityStageResponse,
    OpportunityStageUpdate,
)
from app.schemas.crm.opportunity import OPPORTUNITY_STATUSES, PIPELINE_STAGES, STAGE_PROBABILITY

DEFAULT_ACTIVITY_TYPES: tuple[tuple[str, str], ...] = (
    ("NOTE", "Note"),
    ("CALL", "Call"),
    ("MEETING", "Meeting"),
    ("EMAIL", "Email"),
    ("TASK", "Task"),
    ("SYSTEM", "System"),
)

DEFAULT_STAGES: tuple[tuple[str, str, int, int, bool], ...] = tuple(
    (
        code,
        code.replace("_", " ").title(),
        i + 1,
        STAGE_PROBABILITY.get(code, 0),
        False,
    )
    for i, code in enumerate(PIPELINE_STAGES)
)

DEFAULT_OUTCOMES: tuple[tuple[str, str, str, bool], ...] = (
    ("CALL", "INTERESTED", "Interested", True),
    ("CALL", "NOT_INTERESTED", "Not Interested", False),
    ("CALL", "CALLBACK", "Callback Requested", False),
    ("CALL", "NO_ANSWER", "No Answer", False),
    ("MEETING", "REQUIREMENTS_CAPTURED", "Requirements Captured", True),
    ("MEETING", "RESCHEDULED", "Rescheduled", False),
    ("MEETING", "CANCELLED", "Cancelled", False),
    ("TASK", "DONE", "Done", True),
    ("TASK", "DEFERRED", "Deferred", False),
)

OUTCOME_REQUIRED_TYPES = frozenset({"CALL", "MEETING", "TASK"})


class CrmLookupService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = LookupRepository(db)

    def ensure_tenant_defaults(self, tenant_id: UUID) -> None:
        self.repo.seed_defaults(
            tenant_id, DEFAULT_ACTIVITY_TYPES, DEFAULT_STAGES, DEFAULT_OUTCOMES
        )

    def get_lookups(self, tenant_id: UUID) -> CrmLookupsResponse:
        self.ensure_tenant_defaults(tenant_id)
        activity_rows = self.repo.list_activity_types(tenant_id)
        stage_rows = self.repo.list_opportunity_stages(tenant_id)
        outcome_rows = self.repo.list_activity_outcomes(tenant_id)
        return CrmLookupsResponse(
            pipeline_stages=[s.code for s in stage_rows] or list(PIPELINE_STAGES),
            opportunity_statuses=list(OPPORTUNITY_STATUSES),
            lead_statuses=list(LEAD_STATUSES),
            activity_types=[a.code for a in activity_rows]
            or [c for c, _ in DEFAULT_ACTIVITY_TYPES],
            activity_statuses=list(ACTIVITY_STATUSES),
            activity_outcomes=[o.code for o in outcome_rows],
            activity_type_details=[
                ActivityTypeResponse.model_validate(a) for a in activity_rows
            ],
            activity_outcome_details=[
                ActivityOutcomeResponse.model_validate(o) for o in outcome_rows
            ],
            pipeline_stage_details=[
                OpportunityStageResponse.model_validate(s) for s in stage_rows
            ],
        )

    def list_activity_types(
        self, tenant_id: UUID, *, include_inactive: bool = False
    ) -> ActivityTypeListResponse:
        self.ensure_tenant_defaults(tenant_id)
        rows = self.repo.list_activity_types(
            tenant_id, active_only=not include_inactive
        )
        return ActivityTypeListResponse(
            items=[ActivityTypeResponse.model_validate(r) for r in rows]
        )

    def create_activity_type(
        self, tenant_id: UUID, current: CurrentUser, payload: ActivityTypeCreate
    ) -> ActivityTypeResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Activity type admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        code = payload.code.strip().upper()
        if self.repo.get_activity_type_by_code(tenant_id, code):
            raise AppError(
                "VALIDATION_ERROR",
                f"Activity type '{code}' already exists",
                422,
                req_id="REQ-CRM-004",
            )
        row = ActivityType(
            activity_type_id=uuid4(),
            tenant_id=tenant_id,
            code=code,
            name=payload.name.strip(),
        )
        saved = self.repo.add_activity_type(row)
        return ActivityTypeResponse.model_validate(saved)

    def update_activity_type(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        activity_type_id: UUID,
        payload: ActivityTypeUpdate,
    ) -> ActivityTypeResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Activity type admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        row = self.repo.get_activity_type_by_id(tenant_id, activity_type_id)
        if row is None:
            raise AppError("NOT_FOUND", "Activity type not found", 404, req_id="REQ-CRM-004")
        data = payload.model_dump(exclude_unset=True)
        if "is_active" in data and data["is_active"] is not None:
            row.is_active = data["is_active"]
        if "name" in data and data["name"]:
            row.name = data["name"].strip()
        saved = self.repo.save_activity_type(row)
        return ActivityTypeResponse.model_validate(saved)

    def list_activity_outcomes(
        self,
        tenant_id: UUID,
        *,
        activity_type_code: str | None = None,
        include_inactive: bool = False,
    ) -> ActivityOutcomeListResponse:
        self.ensure_tenant_defaults(tenant_id)
        rows = self.repo.list_activity_outcomes(
            tenant_id,
            activity_type_code=activity_type_code,
            active_only=not include_inactive,
        )
        return ActivityOutcomeListResponse(
            items=[ActivityOutcomeResponse.model_validate(r) for r in rows]
        )

    def create_activity_outcome(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        payload: ActivityOutcomeCreate,
    ) -> ActivityOutcomeResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Activity outcome admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        type_code = payload.activity_type_code.strip().upper()
        code = payload.code.strip().upper()
        if self.repo.get_activity_outcome_by_code(tenant_id, type_code, code):
            raise AppError(
                "VALIDATION_ERROR",
                f"Outcome '{code}' already exists for {type_code}",
                422,
                req_id="REQ-CRM-004",
            )
        row = ActivityOutcome(
            activity_outcome_id=uuid4(),
            tenant_id=tenant_id,
            activity_type_code=type_code,
            code=code,
            name=payload.name.strip(),
            is_positive=payload.is_positive,
        )
        saved = self.repo.save_activity_outcome(row)
        return ActivityOutcomeResponse.model_validate(saved)

    def update_activity_outcome(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        outcome_id: UUID,
        payload: ActivityOutcomeUpdate,
    ) -> ActivityOutcomeResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Activity outcome admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        row = self.repo.get_activity_outcome_by_id(tenant_id, outcome_id)
        if row is None:
            raise AppError("NOT_FOUND", "Activity outcome not found", 404, req_id="REQ-CRM-004")
        data = payload.model_dump(exclude_unset=True)
        if "is_active" in data and data["is_active"] is not None:
            row.is_active = data["is_active"]
        if "name" in data and data["name"]:
            row.name = data["name"].strip()
        if "is_positive" in data and data["is_positive"] is not None:
            row.is_positive = data["is_positive"]
        saved = self.repo.save_activity_outcome(row)
        return ActivityOutcomeResponse.model_validate(saved)

    def list_opportunity_stages(
        self, tenant_id: UUID, *, include_inactive: bool = False
    ) -> OpportunityStageListResponse:
        self.ensure_tenant_defaults(tenant_id)
        rows = self.repo.list_opportunity_stages(
            tenant_id, active_only=not include_inactive
        )
        return OpportunityStageListResponse(
            items=[OpportunityStageResponse.model_validate(r) for r in rows]
        )

    def create_opportunity_stage(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        payload: OpportunityStageCreate,
    ) -> OpportunityStageResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Stage admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        self.ensure_tenant_defaults(tenant_id)
        code = payload.code.strip().upper()
        if self.repo.get_opportunity_stage_by_code(tenant_id, code):
            raise AppError(
                "VALIDATION_ERROR",
                f"Pipeline stage '{code}' already exists",
                422,
                req_id="REQ-CRM-002",
            )
        existing = self.repo.list_opportunity_stages(tenant_id, active_only=False)
        next_seq = max((s.sequence_no for s in existing), default=0) + 1
        row = OpportunityStage(
            opportunity_stage_id=uuid4(),
            tenant_id=tenant_id,
            code=code,
            name=payload.name.strip(),
            sequence_no=next_seq,
            default_probability=payload.default_probability,
            is_closed=payload.is_closed,
        )
        saved = self.repo.save_opportunity_stage(row)
        return OpportunityStageResponse.model_validate(saved)

    def update_opportunity_stage(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        stage_id: UUID,
        payload: OpportunityStageUpdate,
    ) -> OpportunityStageResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Stage admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        row = self.repo.get_opportunity_stage_by_id(tenant_id, stage_id)
        if row is None:
            raise AppError("NOT_FOUND", "Opportunity stage not found", 404, req_id="REQ-CRM-002")
        data = payload.model_dump(exclude_unset=True)
        if "is_active" in data and data["is_active"] is not None:
            row.is_active = data["is_active"]
        if "name" in data and data["name"]:
            row.name = data["name"].strip()
        if "sequence_no" in data and data["sequence_no"] is not None:
            row.sequence_no = data["sequence_no"]
        saved = self.repo.save_opportunity_stage(row)
        return OpportunityStageResponse.model_validate(saved)

    def reorder_opportunity_stages(
        self,
        tenant_id: UUID,
        current: CurrentUser,
        payload: OpportunityStageReorder,
    ) -> OpportunityStageListResponse:
        if current.role_code not in ("TENANT_ADMIN", "PLATFORM_ADMIN", "SALES_MANAGER"):
            raise ForbiddenError(
                "Stage admin requires manager role", req_id="REQ-CRM-RBAC"
            )
        self.ensure_tenant_defaults(tenant_id)
        existing = self.repo.list_opportunity_stages(tenant_id, active_only=False)
        existing_ids = {s.opportunity_stage_id for s in existing}
        if set(payload.stage_ids) != existing_ids:
            raise AppError(
                "VALIDATION_ERROR",
                "Reorder must include every tenant stage exactly once",
                422,
                req_id="REQ-CRM-002",
            )
        try:
            rows = self.repo.reorder_opportunity_stages(tenant_id, payload.stage_ids)
        except ValueError as exc:
            raise AppError("VALIDATION_ERROR", str(exc), 422, req_id="REQ-CRM-002") from exc
        active = [r for r in rows if r.is_active]
        return OpportunityStageListResponse(
            items=[OpportunityStageResponse.model_validate(r) for r in active]
        )
