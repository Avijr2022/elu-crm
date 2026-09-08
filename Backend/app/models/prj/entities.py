import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class WorkOrder(Base):
    __tablename__ = "work_order"
    __table_args__ = (
        UniqueConstraint("tenant_id", "wo_number", name="uk_wo_tenant_number"),
        {"schema": "projects"},
    )

    work_order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    wo_number: Mapped[str] = mapped_column(String(40), nullable=False)
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.opportunity.opportunity_id"), nullable=True
    )
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=True
    )
    sales_order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sales.sales_order.sales_order_id"), nullable=True
    )
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="QUEUED")
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))
