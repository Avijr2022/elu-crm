from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.models.sal import QuotationCustomerResponse


class QuotationCustomerResponseRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        response_type: str,
        recorded_by: UUID | None,
        comment: str | None,
    ) -> QuotationCustomerResponse:
        row = QuotationCustomerResponse(
            quotation_customer_response_id=uuid4(),
            tenant_id=tenant_id,
            quotation_id=quotation_id,
            response_type=response_type,
            recorded_by=recorded_by,
            comment=comment,
        )
        self.db.add(row)
        self.db.flush()
        return row
