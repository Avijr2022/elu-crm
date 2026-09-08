from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.models.prj import WorkOrder
from app.repositories.crm.opportunity_repository import OpportunityRepository
from app.repositories.prj.work_order_repository import WorkOrderRepository


class HandoffService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.opps = OpportunityRepository(db)
        self.work_orders = WorkOrderRepository(db)

    def create_from_opportunity(
        self, tenant_id: UUID, opportunity_id: UUID
    ) -> WorkOrder:
        opp = self.opps.get_by_id(tenant_id, opportunity_id)
        if opp is None:
            raise NotFoundError("Opportunity not found", req_id="REQ-CRM-002")
        if opp.status != "CLOSED_WON":
            raise AppError(
                "VALIDATION_ERROR",
                "Opportunity must be CLOSED_WON for PRJ handoff",
                422,
                req_id="REQ-PRJ-001",
            )
        existing = self.work_orders.get_by_opportunity(tenant_id, opportunity_id)
        if existing is not None:
            return existing
        row = WorkOrder(
            work_order_id=uuid4(),
            tenant_id=tenant_id,
            wo_number=self._next_number(tenant_id),
            opportunity_id=opportunity_id,
            customer_id=opp.customer_id,
            status="QUEUED",
        )
        return self.work_orders.add(row)

    def _next_number(self, tenant_id: UUID) -> str:
        year = date.today().year
        seq = self.work_orders.next_sequence(tenant_id, year)
        return f"WO-{year}-{seq:06d}"
