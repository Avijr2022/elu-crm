from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.crm import Customer, Opportunity
from app.models.fin import PaymentReceipt
from app.models.sal import SalesOrderPaymentStub
from app.repositories.fin.payment_receipt_repository import PaymentReceiptRepository
from app.repositories.prj.work_order_repository import WorkOrderRepository
from app.repositories.sal.sales_order_line_repository import SalesOrderLineRepository
from app.repositories.sal.sales_order_payment_stub_repository import SalesOrderPaymentStubRepository
from app.repositories.sal.sales_order_repository import SalesOrderRepository
from app.schemas.sal.sales_order import (
    LinkedWorkOrderResponse,
    PaymentStubResponse,
    SalesOrderConfirmResponse,
    SalesOrderDetailResponse,
    SalesOrderLineResponse,
    SalesOrderListResponse,
    SalesOrderPaymentStubResponse,
    SalesOrderResponse,
)


class SalesOrderService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = SalesOrderRepository(db)
        self.lines = SalesOrderLineRepository(db)
        self.work_orders = WorkOrderRepository(db)
        self.payment_stubs = SalesOrderPaymentStubRepository(db)
        self.payment_receipts = PaymentReceiptRepository(db)

    def _so_response(
        self,
        row,
        *,
        opportunity_name: str | None = None,
        customer_name: str | None = None,
    ) -> SalesOrderResponse:
        payload = SalesOrderResponse.model_validate(row).model_dump()
        payload["opportunity_name"] = opportunity_name
        payload["customer_name"] = customer_name
        return SalesOrderResponse(**payload)

    def _stub_responses(self, stub_rows: list[SalesOrderPaymentStub]) -> list[PaymentStubResponse]:
        receipt_ids = [s.payment_receipt_id for s in stub_rows if s.payment_receipt_id is not None]
        receipt_numbers: dict[UUID, str] = {}
        if receipt_ids:
            rows = self.db.execute(
                select(PaymentReceipt.payment_receipt_id, PaymentReceipt.receipt_number).where(
                    PaymentReceipt.payment_receipt_id.in_(receipt_ids),
                    PaymentReceipt.is_deleted.is_(False),
                )
            ).all()
            receipt_numbers = {row[0]: row[1] for row in rows}
        return [
            PaymentStubResponse(
                payment_stub_id=stub.payment_stub_id,
                payment_status=stub.payment_status,
                amount=stub.amount,
                currency_code=stub.currency_code,
                recorded_on=stub.recorded_on,
                payment_receipt_id=stub.payment_receipt_id,
                receipt_number=(
                    receipt_numbers.get(stub.payment_receipt_id)
                    if stub.payment_receipt_id is not None
                    else None
                ),
            )
            for stub in stub_rows
        ]

    def list_sales_orders(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        opportunity_id: UUID | None = None,
        customer_id: UUID | None = None,
    ) -> SalesOrderListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        items, total = self.repo.list(
            tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            opportunity_id=opportunity_id,
            customer_id=customer_id,
        )
        return SalesOrderListResponse(
            items=[
                self._so_response(row, opportunity_name=opp_name, customer_name=cust_name)
                for row, opp_name, cust_name in items
            ],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_sales_order(self, tenant_id: UUID, sales_order_id: UUID) -> SalesOrderDetailResponse:
        row = self.repo.get_by_id(tenant_id, sales_order_id)
        if row is None:
            raise NotFoundError("Sales order not found", req_id="REQ-SAL-008")
        line_rows = self.lines.list_for_order(tenant_id, sales_order_id)
        wo_rows = self.work_orders.list_by_sales_order(tenant_id, sales_order_id)
        stub_rows = self.payment_stubs.list_for_order(tenant_id, sales_order_id)
        opp_name = None
        cust_name = None
        if row.opportunity_id is not None:
            opp_name = self.db.scalar(
                select(Opportunity.name).where(
                    Opportunity.tenant_id == tenant_id,
                    Opportunity.opportunity_id == row.opportunity_id,
                    Opportunity.is_deleted.is_(False),
                )
            )
        if row.customer_id is not None:
            cust_name = self.db.scalar(
                select(Customer.legal_name).where(
                    Customer.tenant_id == tenant_id,
                    Customer.customer_id == row.customer_id,
                    Customer.is_deleted.is_(False),
                )
            )
        return SalesOrderDetailResponse(
            **self._so_response(row, opportunity_name=opp_name, customer_name=cust_name).model_dump(),
            lines=[SalesOrderLineResponse.model_validate(l) for l in line_rows],
            work_orders=[LinkedWorkOrderResponse.model_validate(w) for w in wo_rows],
            payment_stubs=self._stub_responses(stub_rows),
        )

    def confirm_sales_order(
        self,
        tenant_id: UUID,
        sales_order_id: UUID,
        permissions: frozenset[str],
    ) -> SalesOrderConfirmResponse:
        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-SAL-RBAC")
        row = self.repo.get_by_id(tenant_id, sales_order_id)
        if row is None:
            raise NotFoundError("Sales order not found", req_id="REQ-SAL-008")
        if row.status != "DRAFT":
            raise AppError(
                "VALIDATION_ERROR",
                "Only DRAFT sales orders can be confirmed",
                422,
                req_id="REQ-SAL-009",
            )
        row.status = "CONFIRMED"
        row.confirmed_on = datetime.now(timezone.utc)
        linked = 0
        if row.opportunity_id is not None:
            linked = self.work_orders.link_to_sales_order(
                tenant_id, row.opportunity_id, sales_order_id
            )
        self.db.commit()
        self.db.refresh(row)
        return SalesOrderConfirmResponse(
            sales_order_id=row.sales_order_id,
            so_number=row.so_number,
            status=row.status,
            work_orders_linked=linked,
            message=f"Sales order {row.so_number} confirmed",
        )

    def record_payment_stub(
        self,
        tenant_id: UUID,
        sales_order_id: UUID,
        permissions: frozenset[str],
        *,
        actor_id: UUID | None = None,
    ) -> SalesOrderPaymentStubResponse:
        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-SAL-RBAC")
        row = self.repo.get_by_id(tenant_id, sales_order_id)
        if row is None:
            raise NotFoundError("Sales order not found", req_id="REQ-SAL-008")
        if row.status != "CONFIRMED":
            raise AppError(
                "VALIDATION_ERROR",
                "Payment stub requires a CONFIRMED sales order",
                422,
                req_id="REQ-SAL-010",
            )
        now = datetime.now(timezone.utc)
        year = now.year
        seq = self.payment_receipts.next_sequence(tenant_id, year)
        receipt_number = f"PR-{year}-{seq:04d}"
        receipt = PaymentReceipt(
            payment_receipt_id=uuid4(),
            tenant_id=tenant_id,
            receipt_number=receipt_number,
            customer_id=row.customer_id,
            sales_order_id=sales_order_id,
            amount=row.grand_total,
            currency_code=row.currency_code,
            received_on=now,
            status="RECORDED",
            method="STUB",
        )
        self.payment_receipts.add(receipt)
        stub = SalesOrderPaymentStub(
            payment_stub_id=uuid4(),
            tenant_id=tenant_id,
            sales_order_id=sales_order_id,
            payment_status="RECORDED_STUB",
            amount=row.grand_total,
            currency_code=row.currency_code,
            recorded_by=actor_id,
            payment_receipt_id=receipt.payment_receipt_id,
        )
        self.payment_stubs.add(stub)
        self.db.commit()
        self.db.refresh(stub)
        return SalesOrderPaymentStubResponse(
            payment_stub_id=stub.payment_stub_id,
            payment_receipt_id=receipt.payment_receipt_id,
            receipt_number=receipt.receipt_number,
            sales_order_id=row.sales_order_id,
            so_number=row.so_number,
            payment_status=stub.payment_status,
            amount=stub.amount,
            currency_code=stub.currency_code,
            recorded_on=stub.recorded_on,
            message=f"Payment receipt {receipt.receipt_number} recorded for {row.so_number}",
        )
