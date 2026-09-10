from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.repositories.prj.work_order_repository import WorkOrderRepository
from app.repositories.sal.sales_order_repository import SalesOrderRepository
from app.schemas.prj.work_order import WorkOrderListResponse, WorkOrderResponse


class WorkOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = WorkOrderRepository(db)
        self.sales_orders = SalesOrderRepository(db)

    def _to_response(self, tenant_id: UUID, row, so_numbers: dict[UUID, str]) -> WorkOrderResponse:
        so_number = None
        if row.sales_order_id is not None:
            so_number = so_numbers.get(row.sales_order_id)
        return WorkOrderResponse(
            work_order_id=row.work_order_id,
            wo_number=row.wo_number,
            opportunity_id=row.opportunity_id,
            customer_id=row.customer_id,
            sales_order_id=row.sales_order_id,
            so_number=so_number,
            status=row.status,
            created_on=row.created_on,
        )

    def list_work_orders(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
    ) -> WorkOrderListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        items, total = self.repo.list(
            tenant_id, page=page, page_size=page_size, status=status
        )
        so_ids = [i.sales_order_id for i in items if i.sales_order_id is not None]
        so_numbers = self.sales_orders.map_numbers_by_ids(tenant_id, so_ids)
        return WorkOrderListResponse(
            items=[self._to_response(tenant_id, i, so_numbers) for i in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_work_order(self, tenant_id: UUID, work_order_id: UUID) -> WorkOrderResponse:
        row = self.repo.get_by_id(tenant_id, work_order_id)
        if row is None:
            raise NotFoundError("Work order not found", req_id="REQ-PRJ-002")
        so_numbers = {}
        if row.sales_order_id is not None:
            so_numbers = self.sales_orders.map_numbers_by_ids(
                tenant_id, [row.sales_order_id]
            )
        return self._to_response(tenant_id, row, so_numbers)
