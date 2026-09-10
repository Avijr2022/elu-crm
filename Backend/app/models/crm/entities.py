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
    customer_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=True, index=True
    )

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


class Customer(Base):
    __tablename__ = "customer"
    __table_args__ = (
        UniqueConstraint("tenant_id", "customer_number", name="uk_cust_tenant_number"),
        {"schema": "crm"},
    )

    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    customer_number: Mapped[str] = mapped_column(String(40), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(250), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    customer_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACCOUNT")
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="PROSPECT", index=True)
    owner_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.users.user_id"), nullable=True
    )
    source_opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class CustomerContact(Base):
    __tablename__ = "customer_contact"
    __table_args__ = {"schema": "crm"}

    customer_contact_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    job_title: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone_mobile: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    phone_work: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    contact_role: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_decision_maker: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class CustomerAddress(Base):
    __tablename__ = "customer_address"
    __table_args__ = {"schema": "crm"}

    customer_address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("crm.customer.customer_id"), nullable=False, index=True
    )
    address_type: Mapped[str] = mapped_column(String(20), nullable=False, server_default="REGISTERED")
    address_line1: Mapped[str] = mapped_column(String(250), nullable=False)
    address_line2: Mapped[Optional[str]] = mapped_column(String(250), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_default_billing: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_default_shipping: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Activity(Base):
    __tablename__ = "activity"
    __table_args__ = {"schema": "crm"}

    activity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True)
    activity_type_code: Mapped[str] = mapped_column(String(40), nullable=False, server_default="NOTE")
    outcome_code: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    subject: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), nullable=False, server_default="COMPLETED")
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("core.users.user_id"), nullable=False)
    due_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    modified_on: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class ActivityLink(Base):
    __tablename__ = "activity_link"
    __table_args__ = (
        UniqueConstraint("activity_id", "entity_type", "entity_id", name="uk_activity_entity"),
        {"schema": "crm"},
    )

    activity_link_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True)
    activity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("crm.activity.activity_id"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(40), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)


class ActivityType(Base):
    __tablename__ = "activity_type"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uk_activity_type_tenant_code"),
        {"schema": "crm"},
    )

    activity_type_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))


class ActivityOutcome(Base):
    __tablename__ = "activity_outcome"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "activity_type_code", "code", name="uk_activity_outcome_tenant_type_code"
        ),
        {"schema": "crm"},
    )

    activity_outcome_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    activity_type_code: Mapped[str] = mapped_column(String(40), nullable=False)
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    is_positive: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))


class OpportunityStage(Base):
    __tablename__ = "opportunity_stage"
    __table_args__ = (
        UniqueConstraint("tenant_id", "code", name="uk_opportunity_stage_tenant_code"),
        {"schema": "crm"},
    )

    opportunity_stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(40), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    sequence_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    default_probability: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    is_closed: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
