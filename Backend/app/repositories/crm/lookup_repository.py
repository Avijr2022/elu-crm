from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import ActivityType, ActivityOutcome, OpportunityStage


class LookupRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_activity_types(self, tenant_id: UUID, *, active_only: bool = True) -> list[ActivityType]:
        filters = [
            ActivityType.tenant_id == tenant_id,
            ActivityType.is_deleted.is_(False),
        ]
        if active_only:
            filters.append(ActivityType.is_active.is_(True))
        stmt = select(ActivityType).where(*filters).order_by(ActivityType.code)
        return list(self.db.scalars(stmt).all())

    def get_activity_type_by_code(self, tenant_id: UUID, code: str) -> ActivityType | None:
        stmt = select(ActivityType).where(
            ActivityType.tenant_id == tenant_id,
            ActivityType.code == code.upper(),
            ActivityType.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_activity_type_by_id(
        self, tenant_id: UUID, activity_type_id: UUID
    ) -> ActivityType | None:
        stmt = select(ActivityType).where(
            ActivityType.tenant_id == tenant_id,
            ActivityType.activity_type_id == activity_type_id,
            ActivityType.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def add_activity_type(self, row: ActivityType) -> ActivityType:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def save_activity_type(self, row: ActivityType) -> ActivityType:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def list_opportunity_stages(self, tenant_id: UUID, *, active_only: bool = True) -> list[OpportunityStage]:
        filters = [
            OpportunityStage.tenant_id == tenant_id,
            OpportunityStage.is_deleted.is_(False),
        ]
        if active_only:
            filters.append(OpportunityStage.is_active.is_(True))
        stmt = (
            select(OpportunityStage)
            .where(*filters)
            .order_by(OpportunityStage.sequence_no, OpportunityStage.code)
        )
        return list(self.db.scalars(stmt).all())

    def get_opportunity_stage_by_id(
        self, tenant_id: UUID, stage_id: UUID
    ) -> OpportunityStage | None:
        stmt = select(OpportunityStage).where(
            OpportunityStage.tenant_id == tenant_id,
            OpportunityStage.opportunity_stage_id == stage_id,
            OpportunityStage.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_opportunity_stage_by_code(
        self, tenant_id: UUID, code: str
    ) -> OpportunityStage | None:
        stmt = select(OpportunityStage).where(
            OpportunityStage.tenant_id == tenant_id,
            OpportunityStage.code == code.upper(),
            OpportunityStage.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def save_opportunity_stage(self, row: OpportunityStage) -> OpportunityStage:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def reorder_opportunity_stages(
        self, tenant_id: UUID, stage_ids: list[UUID]
    ) -> list[OpportunityStage]:
        rows = self.list_opportunity_stages(tenant_id, active_only=False)
        by_id = {s.opportunity_stage_id: s for s in rows}
        if len(stage_ids) != len(by_id):
            missing = set(stage_ids) - set(by_id)
            if missing:
                raise ValueError("Unknown stage id in reorder payload")
        for seq, stage_id in enumerate(stage_ids, start=1):
            row = by_id.get(stage_id)
            if row is None:
                continue
            row.sequence_no = seq
            self.db.add(row)
        self.db.commit()
        return self.list_opportunity_stages(tenant_id, active_only=False)

    def list_activity_outcomes(
        self,
        tenant_id: UUID,
        *,
        activity_type_code: str | None = None,
        active_only: bool = True,
    ) -> list[ActivityOutcome]:
        filters = [
            ActivityOutcome.tenant_id == tenant_id,
            ActivityOutcome.is_deleted.is_(False),
        ]
        if active_only:
            filters.append(ActivityOutcome.is_active.is_(True))
        if activity_type_code:
            filters.append(ActivityOutcome.activity_type_code == activity_type_code.upper())
        stmt = (
            select(ActivityOutcome)
            .where(*filters)
            .order_by(ActivityOutcome.activity_type_code, ActivityOutcome.code)
        )
        return list(self.db.scalars(stmt).all())

    def get_activity_outcome_by_id(
        self, tenant_id: UUID, outcome_id: UUID
    ) -> ActivityOutcome | None:
        stmt = select(ActivityOutcome).where(
            ActivityOutcome.tenant_id == tenant_id,
            ActivityOutcome.activity_outcome_id == outcome_id,
            ActivityOutcome.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_activity_outcome_by_code(
        self, tenant_id: UUID, activity_type_code: str, code: str
    ) -> ActivityOutcome | None:
        stmt = select(ActivityOutcome).where(
            ActivityOutcome.tenant_id == tenant_id,
            ActivityOutcome.activity_type_code == activity_type_code.upper(),
            ActivityOutcome.code == code.upper(),
            ActivityOutcome.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def save_activity_outcome(self, row: ActivityOutcome) -> ActivityOutcome:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def seed_defaults(
        self,
        tenant_id: UUID,
        activity_types: tuple[tuple[str, str], ...],
        stages: tuple[tuple[str, str, int, int, bool], ...],
        outcomes: tuple[tuple[str, str, str, bool], ...] = (),
    ) -> None:
        for code, name in activity_types:
            if self.get_activity_type_by_code(tenant_id, code):
                continue
            self.db.add(
                ActivityType(
                    activity_type_id=uuid4(),
                    tenant_id=tenant_id,
                    code=code.upper(),
                    name=name,
                )
            )
        existing_stages = {
            s.code for s in self.list_opportunity_stages(tenant_id, active_only=False)
        }
        for code, name, seq, prob, is_closed in stages:
            if code in existing_stages:
                continue
            self.db.add(
                OpportunityStage(
                    opportunity_stage_id=uuid4(),
                    tenant_id=tenant_id,
                    code=code.upper(),
                    name=name,
                    sequence_no=seq,
                    default_probability=prob,
                    is_closed=is_closed,
                )
            )
        existing_outcomes = {
            (o.activity_type_code, o.code)
            for o in self.list_activity_outcomes(tenant_id, active_only=False)
        }
        for type_code, code, name, is_positive in outcomes:
            key = (type_code.upper(), code.upper())
            if key in existing_outcomes:
                continue
            self.db.add(
                ActivityOutcome(
                    activity_outcome_id=uuid4(),
                    tenant_id=tenant_id,
                    activity_type_code=type_code.upper(),
                    code=code.upper(),
                    name=name,
                    is_positive=is_positive,
                )
            )
        self.db.commit()
