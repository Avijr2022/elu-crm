from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.prj import WorkOrder


class WorkOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, tenant_id: UUID, work_order_id: UUID) -> WorkOrder | None:
        return self.db.scalars(
            select(WorkOrder).where(
                WorkOrder.tenant_id == tenant_id,
                WorkOrder.work_order_id == work_order_id,
                WorkOrder.is_deleted.is_(False),
            )
        ).first()

    def get_by_opportunity(self, tenant_id: UUID, opportunity_id: UUID) -> WorkOrder | None:
        return self.db.scalars(
            select(WorkOrder).where(
                WorkOrder.tenant_id == tenant_id,
                WorkOrder.opportunity_id == opportunity_id,
                WorkOrder.is_deleted.is_(False),
            )
        ).first()

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
    ) -> tuple[list[WorkOrder], int]:
        filters = [WorkOrder.tenant_id == tenant_id, WorkOrder.is_deleted.is_(False)]
        if status:
            filters.append(WorkOrder.status == status.upper())
        total = self.db.scalar(select(func.count()).select_from(WorkOrder).where(*filters)) or 0
        stmt = (
            select(WorkOrder)
            .where(*filters)
            .order_by(WorkOrder.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def list_by_sales_order(self, tenant_id: UUID, sales_order_id: UUID) -> list[WorkOrder]:
        return list(
            self.db.scalars(
                select(WorkOrder).where(
                    WorkOrder.tenant_id == tenant_id,
                    WorkOrder.sales_order_id == sales_order_id,
                    WorkOrder.is_deleted.is_(False),
                )
            ).all()
        )

    def add(self, row: WorkOrder) -> WorkOrder:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"WO-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(WorkOrder).where(
                    WorkOrder.tenant_id == tenant_id,
                    WorkOrder.wo_number.like(prefix),
                )
            )
            or 0
        ) + 1

    def link_to_sales_order(
        self, tenant_id: UUID, opportunity_id: UUID, sales_order_id: UUID
    ) -> int:
        rows = list(
            self.db.scalars(
                select(WorkOrder).where(
                    WorkOrder.tenant_id == tenant_id,
                    WorkOrder.opportunity_id == opportunity_id,
                    WorkOrder.is_deleted.is_(False),
                )
            ).all()
        )
        for row in rows:
            row.sales_order_id = sales_order_id
        self.db.flush()
        return len(rows)
