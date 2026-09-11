from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.models.crm import Customer
from app.models.fin import Invoice, PaymentAllocation
from app.repositories.fin.invoice_repository import InvoiceRepository
from app.repositories.fin.payment_allocation_repository import PaymentAllocationRepository
from app.repositories.fin.payment_receipt_repository import PaymentReceiptRepository
from app.repositories.sal.sales_order_repository import SalesOrderRepository
from app.schemas.fin.invoice import (
    InvoiceAllocationResponse,
    InvoiceDetail,
    InvoiceIssueResponse,
    InvoiceListResponse,
    InvoiceSummary,
)
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

    # ---- FIN v4.13: invoice list / detail / issue -------------------------------

    def _customer_name(self, tenant_id: UUID, customer_id: UUID | None) -> str | None:
        if customer_id is None:
            return None
        return self.db.scalar(
            select(Customer.legal_name).where(
                Customer.tenant_id == tenant_id,
                Customer.customer_id == customer_id,
                Customer.is_deleted.is_(False),
            )
        )

    def _so_number(self, tenant_id: UUID, sales_order_id: UUID | None) -> str | None:
        if sales_order_id is None:
            return None
        sales_order = self.sales_orders.get_by_id(tenant_id, sales_order_id)
        return sales_order.so_number if sales_order else None

    @staticmethod
    def _summary(
        invoice: Invoice,
        *,
        customer_name: str | None,
        so_number: str | None,
        allocated_total: Decimal,
    ) -> InvoiceSummary:
        base = InvoiceResponse.model_validate(invoice).model_dump()
        base["so_number"] = so_number
        base["customer_name"] = customer_name
        base["allocated_total"] = allocated_total
        base["balance_due"] = (invoice.grand_total or Decimal("0")) - allocated_total
        return InvoiceSummary(**base)

    def list_invoices(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        customer_id: UUID | None = None,
        sales_order_id: UUID | None = None,
    ) -> InvoiceListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        rows, total = self.repo.list_invoices(
            tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            customer_id=customer_id,
            sales_order_id=sales_order_id,
        )
        totals = self.allocations.allocated_totals_for_invoices(
            tenant_id, [invoice.invoice_id for invoice, _, _ in rows]
        )
        return InvoiceListResponse(
            items=[
                self._summary(
                    invoice,
                    customer_name=customer_name,
                    so_number=so_number,
                    allocated_total=totals.get(invoice.invoice_id, Decimal("0")),
                )
                for invoice, customer_name, so_number in rows
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_invoice(self, tenant_id: UUID, invoice_id: UUID) -> InvoiceDetail:
        invoice = self.repo.get_by_id(tenant_id, invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found", req_id="REQ-FIN-004")
        allocation_rows = self.allocations.list_for_invoice(tenant_id, invoice_id)
        allocated_total = sum((a.allocated_amount for a, _ in allocation_rows), Decimal("0"))
        summary = self._summary(
            invoice,
            customer_name=self._customer_name(tenant_id, invoice.customer_id),
            so_number=self._so_number(tenant_id, invoice.sales_order_id),
            allocated_total=allocated_total,
        )
        return InvoiceDetail(
            **summary.model_dump(),
            allocations=[
                InvoiceAllocationResponse(
                    payment_allocation_id=allocation.payment_allocation_id,
                    payment_receipt_id=allocation.payment_receipt_id,
                    receipt_number=receipt_number,
                    allocated_amount=allocation.allocated_amount,
                    created_on=allocation.created_on,
                )
                for allocation, receipt_number in allocation_rows
            ],
        )

    def issue_invoice(self, tenant_id: UUID, invoice_id: UUID) -> InvoiceIssueResponse:
        invoice = self.repo.get_by_id(tenant_id, invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found", req_id="REQ-FIN-004")
        if invoice.status == "ISSUED":
            raise ConflictError(
                f"Invoice {invoice.invoice_number} is already issued", req_id="REQ-FIN-006"
            )
        if invoice.status == "CANCELLED":
            raise ValidationAppError(
                "A cancelled invoice cannot be issued", req_id="REQ-FIN-007"
            )
        if invoice.status != "DRAFT":
            raise ValidationAppError(
                f"Only DRAFT invoices can be issued (current: {invoice.status})",
                req_id="REQ-FIN-007",
            )
        invoice.status = "ISSUED"
        invoice.issued_on = datetime.now(timezone.utc)
        invoice.version_no = (invoice.version_no or 1) + 1
        self.db.commit()
        self.db.refresh(invoice)
        allocation_rows = self.allocations.list_for_invoice(tenant_id, invoice_id)
        allocated_total = sum((a.allocated_amount for a, _ in allocation_rows), Decimal("0"))
        return InvoiceIssueResponse(
            invoice=self._summary(
                invoice,
                customer_name=self._customer_name(tenant_id, invoice.customer_id),
                so_number=self._so_number(tenant_id, invoice.sales_order_id),
                allocated_total=allocated_total,
            ),
            message=f"Invoice {invoice.invoice_number} issued",
        )
