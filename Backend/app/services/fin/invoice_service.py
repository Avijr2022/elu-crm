from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.fin import Invoice, PaymentAllocation
from app.repositories.fin.invoice_repository import InvoiceRepository
from app.repositories.fin.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.fin.payment_receipt_repository import PaymentReceiptRepository
from app.repositories.sal.sales_order_repository import SalesOrderRepository
from app.schemas.fin.payment_receipt import InvoiceGenerateResponse, InvoiceResponse


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = InvoiceRepository(db)
        self.receipts = PaymentReceiptRepository(db)
        self.allocations = PaymentAllocationRepository(db)
        self.sales_orders = SalesOrderRepository(db)

    def generate_from_sales_order(
        self,
        tenant_id: UUID,
        sales_order_id: UUID,
        permissions: frozenset[str],
    ) -> InvoiceGenerateResponse:
        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-FIN-RBAC")
        so = self.sales_orders.get_by_id(tenant_id, sales_order_id)
        if so is None:
            raise NotFoundError("Sales order not found", req_id="REQ-FIN-002")
        if so.status != "CONFIRMED":
            raise AppError(
                "VALIDATION_ERROR",
                "Invoice stub requires a CONFIRMED sales order",
                422,
                req_id="REQ-FIN-003",
            )
        existing = self.repo.get_by_sales_order(tenant_id, sales_order_id)
        if existing is not None:
            so_number = so.so_number
            return InvoiceGenerateResponse(
                invoice=self._invoice_response(existing, so_number),
                allocations_created=0,
                message=f"Invoice {existing.invoice_number} already exists for {so_number}",
            )
        year = date.today().year
        seq = self.repo.next_sequence(tenant_id, year)
        invoice = Invoice(
            invoice_id=uuid4(),
            tenant_id=tenant_id,
            invoice_number=f"INV-{year}-{seq:04d}",
            customer_id=so.customer_id,
            sales_order_id=sales_order_id,
            status="DRAFT",
            invoice_date=date.today(),
            currency_code=so.currency_code,
            subtotal=so.subtotal,
            tax_total=so.tax_total,
            grand_total=so.grand_total,
        )
        self.repo.add(invoice)
        allocations_created = 0
        for receipt in self.receipts.list_for_sales_order(tenant_id, sales_order_id):
            self.allocations.add(
                PaymentAllocation(
                    payment_allocation_id=uuid4(),
                    tenant_id=tenant_id,
                    payment_receipt_id=receipt.payment_receipt_id,
                    invoice_id=invoice.invoice_id,
                    allocated_amount=receipt.amount,
                )
            )
            allocations_created += 1
        self.db.commit()
        self.db.refresh(invoice)
        return InvoiceGenerateResponse(
            invoice=self._invoice_response(invoice, so.so_number),
            allocations_created=allocations_created,
            message=f"Invoice {invoice.invoice_number} created for {so.so_number}",
        )

    def _invoice_response(self, invoice: Invoice, so_number: str | None) -> InvoiceResponse:
        return InvoiceResponse(
            invoice_id=invoice.invoice_id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            sales_order_id=invoice.sales_order_id,
            so_number=so_number,
            status=invoice.status,
            invoice_date=invoice.invoice_date,
            currency_code=invoice.currency_code,
            subtotal=invoice.subtotal,
            tax_total=invoice.tax_total,
            grand_total=invoice.grand_total,
            issued_on=invoice.issued_on,
            created_on=invoice.created_on,
        )
