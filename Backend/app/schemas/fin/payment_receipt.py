from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class PaymentAllocationResponse(BaseModel):
    payment_allocation_id: UUID
    payment_receipt_id: UUID
    invoice_id: UUID
    allocated_amount: Decimal
    created_on: datetime

    model_config = {"from_attributes": True}


class PaymentReceiptResponse(BaseModel):
    payment_receipt_id: UUID
    receipt_number: str
    customer_id: Optional[UUID]
    customer_name: Optional[str] = None
    sales_order_id: Optional[UUID]
    so_number: Optional[str] = None
    amount: Decimal
    currency_code: str
    received_on: datetime
    status: str
    method: str
    created_on: datetime

    model_config = {"from_attributes": True}


class PaymentReceiptDetailResponse(PaymentReceiptResponse):
    allocations: list[PaymentAllocationResponse] = []


class PaymentReceiptListResponse(BaseModel):
    items: list[PaymentReceiptResponse]
    total: int
    page: int
    page_size: int


class InvoiceResponse(BaseModel):
    invoice_id: UUID
    invoice_number: str
    customer_id: Optional[UUID]
    sales_order_id: Optional[UUID]
    so_number: Optional[str] = None
    status: str
    invoice_date: date
    currency_code: str
    subtotal: Decimal
    tax_total: Decimal
    grand_total: Decimal
    issued_on: Optional[datetime]
    created_on: datetime

    model_config = {"from_attributes": True}


class InvoiceGenerateResponse(BaseModel):
    invoice: InvoiceResponse
    allocations_created: int
    message: str
