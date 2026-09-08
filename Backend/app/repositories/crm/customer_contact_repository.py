from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import CustomerAddress, CustomerContact


class CustomerContactRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_customer(self, tenant_id: UUID, customer_id: UUID) -> list[CustomerContact]:
        return list(
            self.db.scalars(
                select(CustomerContact).where(
                    CustomerContact.tenant_id == tenant_id,
                    CustomerContact.customer_id == customer_id,
                    CustomerContact.is_deleted.is_(False),
                )
            ).all()
        )

    def add(self, row: CustomerContact) -> CustomerContact:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row


class CustomerAddressRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_for_customer(self, tenant_id: UUID, customer_id: UUID) -> list[CustomerAddress]:
        return list(
            self.db.scalars(
                select(CustomerAddress).where(
                    CustomerAddress.tenant_id == tenant_id,
                    CustomerAddress.customer_id == customer_id,
                    CustomerAddress.is_deleted.is_(False),
                )
            ).all()
        )

    def add(self, row: CustomerAddress) -> CustomerAddress:
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row

    def touch(self, row: CustomerAddress) -> CustomerAddress:
        row.modified_on = datetime.now(timezone.utc)
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return row
