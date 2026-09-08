from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, ForbiddenError, ConflictError, ValidationAppError
from app.models.crm import Customer
from app.models.sal import SalesOrder
from app.repositories.fin.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.fin.payment_receipt_repository import PaymentReceiptRepository
from app.schemas.fin.payment_receipt import (
    PaymentAllocationResponse,
    PaymentReceiptDetailResponse,
    PaymentReceiptListResponse,
    PaymentReceiptResponse,
)


class PaymentReceiptService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PaymentReceiptRepository(db)
        self.allocations = PaymentAllocationRepository(db)

    def list_payment_receipts(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        sales_order_id: UUID | None = None,
    ) -> PaymentReceiptListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        rows, total = self.repo.list(
            tenant_id, page=page, page_size=page_size, sales_order_id=sales_order_id
        )
        return PaymentReceiptListResponse(
            items=[
                PaymentReceiptResponse(
                    **PaymentReceiptResponse.model_validate(receipt).model_dump(
                        exclude={"customer_name", "so_number"}
                    ),
                    customer_name=customer_name,
                    so_number=so_number,
                )
                for receipt, customer_name, so_number in rows
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_payment_receipt(
        self, tenant_id: UUID, payment_receipt_id: UUID
    ) -> PaymentReceiptDetailResponse:
        receipt = self.repo.get_by_id(tenant_id, payment_receipt_id)
        if receipt is None:
            raise NotFoundError("Payment receipt not found", req_id="REQ-FIN-001")
        customer_name = None
        so_number = None
        if receipt.customer_id is not None:
            customer_name = self.db.scalar(
                select(Customer.legal_name).where(
                    Customer.tenant_id == tenant_id,
                    Customer.customer_id == receipt.customer_id,
                    Customer.is_deleted.is_(False),
                )
            )
        if receipt.sales_order_id is not None:
            so_number = self.db.scalar(
                select(SalesOrder.so_number).where(
                    SalesOrder.tenant_id == tenant_id,
                    SalesOrder.sales_order_id == receipt.sales_order_id,
                    SalesOrder.is_deleted.is_(False),
                )
            )
        alloc_rows = self.allocations.list_for_receipt(tenant_id, payment_receipt_id)
        data = PaymentReceiptResponse.model_validate(receipt).model_dump(
            exclude={"customer_name", "so_number"}
        )
        data["customer_name"] = customer_name
        data["so_number"] = so_number
        return PaymentReceiptDetailResponse(
            **data,
            allocations=[PaymentAllocationResponse.model_validate(a) for a in alloc_rows],
        )

    def allocate_to_invoice(self, tenant_id: UUID, payment_receipt_id: UUID, invoice_id: UUID, permissions: frozenset[str], allocated_amount: float | None = None):
        from app.repositories.fin.invoice_repository import InvoiceRepository
        from app.models.fin import PaymentAllocation
        from uuid import uuid4
        from decimal import Decimal

        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-FIN-RBAC")

        receipt = self.repo.get_by_id(tenant_id, payment_receipt_id)
        if receipt is None:
            raise NotFoundError("Payment receipt not found", req_id="REQ-FIN-001")

        invoice = InvoiceRepository(self.db).get_by_id(tenant_id, invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found", req_id="REQ-FIN-004")

        # Calculate remaining unallocated amount on the receipt
        alloc_rows = self.allocations.list_for_receipt(tenant_id, payment_receipt_id)
        existing_total = sum((a.allocated_amount for a in alloc_rows), Decimal(0))
        remaining = receipt.amount - existing_total

        # Determine amount to allocate: full remaining if not specified
        if allocated_amount is None:
            amount_to_allocate = remaining
        else:
            try:
                amount_to_allocate = Decimal(str(allocated_amount))
            except Exception:
                raise ValidationAppError("Invalid allocated_amount", req_id="REQ-FIN-002")
            if amount_to_allocate <= 0:
                raise ValidationAppError("Allocated amount must be positive", req_id="REQ-FIN-002")
            if amount_to_allocate > remaining:
                raise ConflictError("Allocated amount exceeds remaining receipt balance", req_id="REQ-FIN-003")

        if amount_to_allocate <= 0:
            raise ConflictError("No remaining balance to allocate", req_id="REQ-FIN-005")

        allocation = self.allocations.add(
            PaymentAllocation(
                payment_allocation_id=uuid4(),
                tenant_id=tenant_id,
                payment_receipt_id=payment_receipt_id,
                invoice_id=invoice_id,
                allocated_amount=amount_to_allocate,
            )
        )
        self.db.commit()
        return allocation
