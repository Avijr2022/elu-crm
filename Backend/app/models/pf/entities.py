import uuid
from datetime import date, datetime
from typing import Optional

from decimal import Decimal

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
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TimestampMixin:
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    modified_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now(), nullable=True
    )


class SoftDeleteMixin:
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("1"))


class Edition(Base, TimestampMixin):
    """Platform-global edition catalogue (ELU-DDD-PF §3.1). No tenant_id / no RLS."""

    __tablename__ = "edition"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version_no: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("1")
    )
    status: Mapped[str] = mapped_column(
        String(32), nullable=False, server_default="DRAFT"
    )
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    list_price_monthly: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    list_price_annual: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    currency_code: Mapped[Optional[str]] = mapped_column(
        String(3), nullable=True, server_default="INR"
    )
    display_order: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True, server_default=text("0")
    )
    published_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    published_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    end_of_sale_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    features: Mapped[list["EditionFeature"]] = relationship(
        back_populates="edition", cascade="all, delete-orphan"
    )
    limits: Mapped[list["EditionLimit"]] = relationship(
        back_populates="edition", cascade="all, delete-orphan"
    )
    versions: Mapped[list["EditionVersion"]] = relationship(
        back_populates="edition"
    )


class FeatureCatalogue(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "feature_catalogue"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    feature_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    feature_name: Mapped[str] = mapped_column(String(150), nullable=False)
    module_domain: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class EditionFeature(Base, TimestampMixin):
    __tablename__ = "edition_feature"
    __table_args__ = (
        UniqueConstraint("edition_id", "feature_code", name="uk_edition_feature"),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    edition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    feature_code: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("core.feature_catalogue.feature_code"),
        nullable=False,
    )
    is_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    is_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    edition: Mapped["Edition"] = relationship(back_populates="features")


class EditionLimit(Base, TimestampMixin):
    __tablename__ = "edition_limit"
    __table_args__ = (
        UniqueConstraint("edition_id", "limit_code", name="uk_edition_limit"),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    edition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.edition.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    limit_code: Mapped[str] = mapped_column(String(64), nullable=False)
    limit_name: Mapped[str] = mapped_column(String(150), nullable=False)
    limit_value: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)
    limit_unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    is_hard_limit: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    grace_percent: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, server_default=text("0")
    )

    edition: Mapped["Edition"] = relationship(back_populates="limits")


class EditionVersion(Base):
    __tablename__ = "edition_version"
    __table_args__ = (
        UniqueConstraint("edition_id", "version_no", name="uk_edition_version"),
        {"schema": "core"},
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    edition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.edition.id"),
        nullable=False,
        index=True,
    )
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    snapshot_json: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    edition: Mapped["Edition"] = relationship(back_populates="versions")


class AuditEvent(Base):
    """ELU-DDD-PF §8 — tenant_id NULL for platform-global edition events."""

    __tablename__ = "audit_event"
    __table_args__ = {"schema": "audit"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    event_category: Mapped[str] = mapped_column(String(64), nullable=False)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    actor_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    ip_address: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    payload_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Tenant(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant root. Physical PK `tenant_id` retained for child FK graph; API exposes DDD `id`/`code`."""

    __tablename__ = "tenant"
    __table_args__ = {"schema": "core"}

    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    tenant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    legal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    trade_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    edition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.edition.id"), nullable=False
    )
    organization_type: Mapped[str] = mapped_column(String(50), nullable=False)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, server_default="DRAFT")
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    provision_source: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    activation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    activated_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    suspended_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    remarks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    current_subscription_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.subscription.subscription_id", use_alter=True, name="fk_tenant_current_sub"),
        nullable=True,
    )

    edition: Mapped["Edition"] = relationship()
    organizations: Mapped[list["Organization"]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(back_populates="tenant")
    settings: Mapped[Optional["TenantSettings"]] = relationship(
        back_populates="tenant", uselist=False
    )
    contacts: Mapped[list["TenantContact"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )
    addresses: Mapped[list["TenantAddress"]] = relationship(
        back_populates="tenant", cascade="all, delete-orphan"
    )


class TenantContact(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenant_contact"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    contact_type: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    mobile: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="contacts")


class TenantAddress(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenant_address"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    address_type: Mapped[str] = mapped_column(String(32), nullable=False)
    line1: Mapped[str] = mapped_column(String(255), nullable=False)
    line2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(
        String(100), nullable=False, server_default="India"
    )
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="addresses")


class TenantStatusHistory(Base):
    __tablename__ = "tenant_status_history"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    to_status: Mapped[str] = mapped_column(String(32), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    changed_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class IdempotencyKey(Base):
    __tablename__ = "idempotency_key"
    __table_args__ = {"schema": "core"}

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    request_path: Mapped[str] = mapped_column(String(255), nullable=False)
    response_status: Mapped[int] = mapped_column(Integer, nullable=False)
    response_body: Mapped[str] = mapped_column(Text, nullable=False)
    created_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class Organization(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "organization"
    __table_args__ = (
        UniqueConstraint("tenant_id", "organization_code", name="uk_org_tenant_code"),
        {"schema": "core"},
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    parent_organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.organization.organization_id"), nullable=True
    )
    organization_code: Mapped[str] = mapped_column(String(30), nullable=False)
    organization_name: Mapped[str] = mapped_column(String(200), nullable=False)
    organization_type: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")

    tenant: Mapped["Tenant"] = relationship(back_populates="organizations")


class Role(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "role"
    __table_args__ = (
        UniqueConstraint("tenant_id", "role_code", name="uk_role_tenant_code"),
        {"schema": "core"},
    )

    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=True, index=True
    )
    role_code: Mapped[str] = mapped_column(String(50), nullable=False)
    role_name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))


class Permission(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "permission"
    __table_args__ = {"schema": "core"}

    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    permission_code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    permission_name: Mapped[str] = mapped_column(String(150), nullable=False)
    module_code: Mapped[str] = mapped_column(String(30), nullable=False)


class RolePermission(Base):
    __tablename__ = "role_permission"
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uk_role_permission"),
        {"schema": "core"},
    )

    role_permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.role.role_id"), nullable=False
    )
    permission_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.permission.permission_id"), nullable=False
    )


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uk_users_tenant_email"),
        {"schema": "core"},
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.organization.organization_id"), nullable=False
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.role.role_id"), nullable=False
    )
    employee_code: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    display_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    designation: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    account_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE"
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    organization: Mapped["Organization"] = relationship()
    role: Mapped["Role"] = relationship()


class Subscription(Base, TimestampMixin, SoftDeleteMixin):
    """Subscription root. Physical PK `subscription_id`; API exposes DDD `id`/`status`."""

    __tablename__ = "subscription"
    __table_args__ = {"schema": "core"}

    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    edition_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.edition.id"), nullable=False
    )
    subscription_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(30), nullable=False)
    billing_cycle: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="MONTHLY"
    )
    seat_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("10"))
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    trial_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    amount: Mapped[str] = mapped_column(String(30), nullable=False, server_default="0")
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False, server_default="INR")
    payment_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="PAID"
    )
    subscription_status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE"
    )
    cancellation_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    edition: Mapped["Edition"] = relationship()
    history: Mapped[list["SubscriptionHistory"]] = relationship(
        back_populates="subscription", cascade="all, delete-orphan"
    )


class SubscriptionHistory(Base):
    __tablename__ = "subscription_history"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.subscription.subscription_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    change_type: Mapped[str] = mapped_column(String(32), nullable=False)
    from_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    to_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    from_edition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    to_edition_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    from_seat_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    to_seat_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    changed_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    subscription: Mapped["Subscription"] = relationship(back_populates="history")


class SubscriptionUsage(Base):
    __tablename__ = "subscription_usage"
    __table_args__ = {"schema": "core"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    subscription_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.subscription.subscription_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    metric_code: Mapped[str] = mapped_column(String(32), nullable=False)
    used_value: Mapped[str] = mapped_column(String(30), nullable=False)
    measured_on: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class TenantSettings(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenant_settings"
    __table_args__ = {"schema": "core"}

    setting_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id"),
        nullable=False,
        unique=True,
    )
    financial_year_start: Mapped[date] = mapped_column(Date, nullable=False)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(100), nullable=False)
    date_format: Mapped[str] = mapped_column(String(30), nullable=False)
    time_format: Mapped[str] = mapped_column(String(20), nullable=False, server_default="24 Hour")
    default_language: Mapped[str] = mapped_column(String(20), nullable=False)
    notification_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )
    workflow_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="settings")
