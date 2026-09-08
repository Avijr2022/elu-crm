import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PaymentReceipt(Base):
    __tablename__ = "payment_receipt"
    __table_args__ = (
        UniqueConstraint("tenant_id", "receipt_number", name="uk_receipt_tenant_number"),
        {"schema": "finance"},
    )

    payment_receipt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    receipt_number: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=True
    )
    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales.sales_order.sales_order_id"), nullable=True
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False)
    received_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="RECORDED")
    method: Mapped[str] = mapped_column(String(40), nullable=False, server_default="STUB")
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Invoice(Base):
    __tablename__ = "invoice"
    __table_args__ = (
        UniqueConstraint("tenant_id", "invoice_number", name="uk_invoice_tenant_number"),
        {"schema": "finance"},
    )

    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    invoice_number: Mapped[str] = mapped_column(String(40), nullable=False)
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=True
    )
    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales.sales_order.sales_order_id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="DRAFT")
    invoice_date: Mapped[date] = mapped_column(Date, nullable=False, server_default=func.current_date())
    currency_code: Mapped[str] = mapped_column(String(3), nullable=False, server_default="INR")
    subtotal: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text("0"))
    tax_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text("0"))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False, server_default=text("0"))
    issued_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class PaymentAllocation(Base):
    __tablename__ = "payment_allocation"
    __table_args__ = {"schema": "finance"}

    payment_allocation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    payment_receipt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("finance.payment_receipt.payment_receipt_id"), nullable=False
    )
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("finance.invoice.invoice_id"), nullable=False
    )
    allocated_amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
