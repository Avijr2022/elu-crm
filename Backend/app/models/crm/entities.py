import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Lead(Base):
    __tablename__ = "lead"
    __table_args__ = (
        UniqueConstraint("tenant_id", "lead_number", name="uk_lead_tenant_number"),
        {"schema": "crm"},
    )

    lead_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id"),
        nullable=False,
        index=True,
    )
    lead_number: Mapped[str] = mapped_column(String(40), nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    phone: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default="NEW", index=True
    )
    estimated_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="INR"
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.users.user_id"), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    version_no: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )


class Opportunity(Base):
    __tablename__ = "opportunity"
    __table_args__ = (
        UniqueConstraint("tenant_id", "opportunity_number", name="uk_opp_tenant_number"),
        {"schema": "crm"},
    )

    opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id"),
        nullable=False,
        index=True,
    )
    opportunity_number: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    company_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    stage: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default="QUALIFICATION", index=True
    )
    status: Mapped[str] = mapped_column(
        String(40), nullable=False, server_default="OPEN", index=True
    )
    opportunity_value: Mapped[Decimal] = mapped_column(
        Numeric(18, 2), nullable=False, server_default=text("0")
    )
    currency_code: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="INR"
    )
    probability: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("10")
    )
    expected_close_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    source_lead_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.lead.lead_id"), nullable=True, index=True
    )
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.users.user_id"), nullable=True
    )
    loss_reason: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    version_no: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
