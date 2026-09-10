from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

QUOTATION_STATUSES = frozenset({"DRAFT", "SUBMITTED", "APPROVED", "SENT", "ACCEPTED", "REJECTED", "CANCELLED"})


class QuotationCreate(BaseModel):
    customer_id: Optional[UUID] = None
    opportunity_id: Optional[UUID] = None
    currency_code: str = Field(default="INR", max_length=3)
    valid_until: Optional[date] = None
    notes: Optional[str] = None


class QuotationResponse(BaseModel):
    quotation_id: UUID
    quotation_number: str
    opportunity_id: Optional[UUID]
    customer_id: Optional[UUID]
    owner_id: Optional[UUID]
    status: str
    currency_code: str
    subtotal: Decimal
    discount_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    valid_until: Optional[date]
    version_no_doc: int
    is_current: bool
    notes: Optional[str]
    created_on: datetime
    sales_order_id: Optional[UUID] = None
    so_number: Optional[str] = None

    model_config = {"from_attributes": True}


class QuotationListResponse(BaseModel):
    items: list[QuotationResponse]
    total: int
    page: int
    page_size: int


class QuotationLineCreate(BaseModel):
    product_code: Optional[str] = Field(default=None, max_length=40)
    description: str = Field(min_length=1, max_length=500)
    qty: Decimal = Field(default=Decimal("1"), gt=0)
    unit_price: Decimal = Field(default=Decimal("0"), ge=0)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    tax_code: Optional[str] = Field(default="GST18", max_length=20)


class QuotationLineUpdate(BaseModel):
    product_code: Optional[str] = Field(default=None, max_length=40)
    description: Optional[str] = Field(default=None, min_length=1, max_length=500)
    qty: Optional[Decimal] = Field(default=None, gt=0)
    unit_price: Optional[Decimal] = Field(default=None, ge=0)
    discount_pct: Optional[Decimal] = Field(default=None, ge=0, le=100)
    tax_code: Optional[str] = Field(default=None, max_length=20)


class QuotationLineResponse(BaseModel):
    quotation_line_id: UUID
    quotation_id: UUID
    line_no: int
    product_code: Optional[str]
    description: str
    qty: Decimal
    unit_price: Decimal
    discount_pct: Decimal
    tax_code: Optional[str]
    line_total: Decimal

    model_config = {"from_attributes": True}


class QuotationDetailResponse(QuotationResponse):
    lines: list[QuotationLineResponse]


class QuotationStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=40)
    reason: Optional[str] = Field(default=None, max_length=500)


class QuotationCustomerResponseCreate(BaseModel):
    response_type: str = Field(pattern=r"^(?i)(ACCEPTED|REJECTED)$")
    comment: Optional[str] = Field(default=None, max_length=500)


class QuotationStatusHistoryResponse(BaseModel):
    quotation_status_history_id: UUID
    from_status: str
    to_status: str
    actor_id: Optional[UUID]
    reason: Optional[str]
    changed_on: datetime

    model_config = {"from_attributes": True}


STATUS_TRANSITIONS: dict[str, frozenset[str]] = {
    "DRAFT": frozenset({"SUBMITTED", "CANCELLED"}),
    "SUBMITTED": frozenset({"APPROVED", "REJECTED", "CANCELLED"}),
    "APPROVED": frozenset({"SENT", "CANCELLED"}),
    "REJECTED": frozenset({"DRAFT"}),
    "SENT": frozenset({"ACCEPTED", "REJECTED"}),
}


class QuotationExportResponse(BaseModel):
    quotation_id: UUID
    quotation_number: str
    format: str = "pdf"
    status: str = "stub"
    message: str


class SalesOrderConvertResponse(BaseModel):
    sales_order_id: UUID
    so_number: str
    quotation_id: UUID
    status: str = "DRAFT"
    message: str
