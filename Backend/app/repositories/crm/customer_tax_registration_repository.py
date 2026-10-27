from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.crm import Customer, CustomerTaxRegistration


class CustomerTaxRegistrationRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def find_active_tax_match(
        self,
        tenant_id: UUID,
        tax_type: str,
        tax_number: str,
    ) -> Customer | None:
        row = self.db.scalars(
            select(Customer)
            .join(
                CustomerTaxRegistration,
                CustomerTaxRegistration.customer_id == Customer.customer_id,
            )
            .where(
                Customer.tenant_id == tenant_id,
                Customer.is_deleted.is_(False),
                CustomerTaxRegistration.tenant_id == tenant_id,
                CustomerTaxRegistration.is_deleted.is_(False),
                CustomerTaxRegistration.is_active.is_(True),
                CustomerTaxRegistration.tax_type == tax_type,
                CustomerTaxRegistration.tax_number == tax_number,
            )
        ).first()
        return row
