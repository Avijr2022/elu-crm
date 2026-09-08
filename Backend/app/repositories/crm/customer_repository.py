from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.crm import Customer


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        search: str | None = None,
        status: str | None = None,
    ) -> tuple[list[Customer], int]:
        filters = [Customer.tenant_id == tenant_id, Customer.is_deleted.is_(False)]
        if search:
            like = f"%{search.strip()}%"
            filters.append(
                or_(Customer.legal_name.ilike(like), Customer.customer_number.ilike(like))
            )
        if status:
            filters.append(Customer.status == status.upper())
        total = self.db.scalar(select(func.count()).select_from(Customer).where(*filters)) or 0
        stmt = (
            select(Customer)
            .where(*filters)
            .order_by(Customer.created_on.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), int(total)

    def get_by_id(self, tenant_id: UUID, customer_id: UUID) -> Customer | None:
        return self.db.scalars(
            select(Customer).where(
                Customer.tenant_id == tenant_id,
                Customer.customer_id == customer_id,
                Customer.is_deleted.is_(False),
            )
        ).first()

    def next_sequence(self, tenant_id: UUID, year: int) -> int:
        prefix = f"%-CUS-{year}-%"
        return int(
            self.db.scalar(
                select(func.count()).select_from(Customer).where(
                    Customer.tenant_id == tenant_id, Customer.customer_number.like(prefix)
                )
            )
            or 0
        ) + 1

    def add(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def save(self, customer: Customer) -> Customer:
        customer.modified_on = datetime.now(timezone.utc)
        customer.version_no = int(customer.version_no or 1) + 1
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
