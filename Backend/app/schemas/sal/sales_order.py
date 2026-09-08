from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class SalesOrderLineResponse(BaseModel):
    sales_order_line_id: UUID
    sales_order_id: UUID
    line_no: int
    product_code: Optional[str]
    description: str
    qty: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_code: Optional[str]
    line_total: Decimal

    model_config = {"from_attributes": True}


class SalesOrderResponse(BaseModel):
    sales_order_id: UUID
    so_number: str
    quotation_id: UUID
    opportunity_id: Optional[UUID]
    customer_id: Optional[UUID]
    opportunity_name: Optional[str] = None
    customer_name: Optional[str] = None
    status: str
    currency_code: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    confirmed_on: Optional[datetime]
    created_on: datetime

    model_config = {"from_attributes": True}


class SalesOrderDetailResponse(SalesOrderResponse):
    lines: list[SalesOrderLineResponse]
    work_orders: list["LinkedWorkOrderResponse"] = []
    payment_stubs: list["PaymentStubResponse"] = []


class LinkedWorkOrderResponse(BaseModel):
    work_order_id: UUID
    wo_number: str
    status: str

    model_config = {"from_attributes": True}


class PaymentStubResponse(BaseModel):
    payment_stub_id: UUID
    payment_status: str
    amount: Decimal
    currency_code: str
    recorded_on: datetime
    payment_receipt_id: Optional[UUID] = None
    receipt_number: Optional[str] = None

    model_config = {"from_attributes": True}


class SalesOrderListResponse(BaseModel):
    items: list[SalesOrderResponse]
    total: int
    page: int
    page_size: int


class SalesOrderConfirmResponse(BaseModel):
    sales_order_id: UUID
    so_number: str
    status: str
    work_orders_linked: int
    message: str


class SalesOrderPaymentStubResponse(BaseModel):
    payment_stub_id: UUID
    payment_receipt_id: UUID
    receipt_number: str
    sales_order_id: UUID
    so_number: str
    payment_status: str
    amount: Decimal
    currency_code: str
    recorded_on: datetime
    message: str
