from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.schemas.fin.payment_receipt import InvoiceResponse as _InvoiceBase


class InvoiceSummary(_InvoiceBase):
    """Invoice row enriched with joined labels and allocation totals (FIN v4.13)."""

    customer_name: Optional[str] = None
    allocated_total: Decimal = Decimal("0")
    balance_due: Decimal = Decimal("0")


class InvoiceAllocationResponse(BaseModel):
    payment_allocation_id: UUID
    payment_receipt_id: UUID
    receipt_number: Optional[str] = None
    allocated_amount: Decimal
    created_on: datetime

    model_config = {"from_attributes": True}


class InvoiceDetail(InvoiceSummary):
    allocations: list[InvoiceAllocationResponse] = []


class InvoiceListResponse(BaseModel):
    items: list[InvoiceSummary]
    total: int
    page: int
    page_size: int


class InvoiceIssueResponse(BaseModel):
    invoice: InvoiceSummary
    message: str
