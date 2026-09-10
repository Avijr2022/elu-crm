from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.crm import Customer, Opportunity
from app.models.sal import SalesOrder


class SalesOrderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_quotation(self, tenant_id: UUID, quotation_id: UUID) -> SalesOrder | None:
        return self.db.scalars(
            select(SalesOrder).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.quotation_id == quotation_id,
                SalesOrder.is_deleted.is_(False),
            )
        ).first()

    def get_by_id(self, tenant_id: UUID, sales_order_id: UUID) -> SalesOrder | None:
        return self.db.scalars(
            select(SalesOrder).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.sales_order_id == sales_order_id,
                SalesOrder.is_deleted.is_(False),
            )
        ).first()

    def add(self, row: SalesOrder) -> SalesOrder:
        self.db.add(row)
        self.db.flush()
        return row

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        opportunity_id: UUID | None = None,
        customer_id: UUID | None = None,
    ) -> tuple[list[tuple[SalesOrder, str | None, str | None]], int]:
        filters = [SalesOrder.tenant_id == tenant_id, SalesOrder.is_deleted.is_(False)]
        if status:
            filters.append(SalesOrder.status == status.upper())
        if opportunity_id is not None:
            filters.append(SalesOrder.opportunity_id == opportunity_id)
        if customer_id is not None:
            filters.append(SalesOrder.customer_id == customer_id)
        total = self.db.scalar(select(func.count()).select_from(SalesOrder).where(*filters)) or 0
        stmt = (
            select(SalesOrder, Opportunity.name, Customer.legal_name)
            .outerjoin(
                Opportunity,
                (SalesOrder.opportunity_id == Opportunity.opportunity_id)
                & (Opportunity.tenant_id == tenant_id)
                & Opportunity.is_deleted.is_(False),
            )
            .outerjoin(
                Customer,
                (SalesOrder.customer_id == Customer.customer_id)
                & (Customer.tenant_id == tenant_id)
                & Customer.is_deleted.is_(False),
            )
            .where(*filters)
            .order_by(SalesOrder.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        rows = self.db.execute(stmt).all()
        return [(row[0], row[1], row[2]) for row in rows], int(total)

    def map_by_quotation_ids(
        self, tenant_id: UUID, quotation_ids: list[UUID]
    ) -> dict[UUID, SalesOrder]:
        if not quotation_ids:
            return {}
        rows = list(
            self.db.scalars(
                select(SalesOrder).where(
                    SalesOrder.tenant_id == tenant_id,
                    SalesOrder.quotation_id.in_(quotation_ids),
                    SalesOrder.is_deleted.is_(False),
                )
            ).all()
        )
        return {row.quotation_id: row for row in rows}

    def map_numbers_by_ids(self, tenant_id: UUID, sales_order_ids: list[UUID]) -> dict[UUID, str]:
        if not sales_order_ids:
            return {}
        rows = self.db.execute(
            select(SalesOrder.sales_order_id, SalesOrder.so_number).where(
                SalesOrder.tenant_id == tenant_id,
                SalesOrder.sales_order_id.in_(sales_order_ids),
                SalesOrder.is_deleted.is_(False),
            )
        ).all()
        return {row[0]: row[1] for row in rows}

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"SO-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(SalesOrder).where(
                    SalesOrder.tenant_id == tenant_id,
                    SalesOrder.so_number.like(prefix),
                )
            )
            or 0
        ) + 1
