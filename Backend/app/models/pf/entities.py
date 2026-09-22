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
    branding: Mapped[Optional["TenantBranding"]] = relationship(
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
    """Tenant organization profile (ELU-BFS-PF-004 / ELU-DDD-PF §5)."""

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
    legal_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    short_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    organization_type: Mapped[str] = mapped_column(String(50), nullable=False)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cin: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    date_of_incorporation: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gstin: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pan: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tan: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    tax_registration_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    is_root: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    level: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    default_currency_code: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="INR"
    )
    fiscal_year_start_month: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("4")
    )
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant_address.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default="ACTIVE")
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="organizations")


class Branch(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant branch profile (ELU-BFS-PF-005 §7/§9 / ELU-DDD-PF §5).

    Groundwork scope only. Deferred: ``users.branch_id`` and branch-head
    assignment/validation (PF-008, BR-PF-038 / AC-PF-005-04), department linkage
    (PF-006), project -> branch linkage (BR-PF-037). ``branch_head_user_id`` is
    therefore a plain nullable column with no FK and no validation.
    """

    __tablename__ = "branch"
    __table_args__ = (
        UniqueConstraint("tenant_id", "branch_code", name="uk_branch_tenant_code"),
        {"schema": "core"},
    )

    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.organization.organization_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    parent_branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.branch.branch_id", ondelete="RESTRICT"),
        nullable=True,
    )
    branch_code: Mapped[str] = mapped_column(String(30), nullable=False)
    branch_name: Mapped[str] = mapped_column(String(200), nullable=False)
    branch_type: Mapped[str] = mapped_column(String(32), nullable=False)
    branch_head_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    email: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    branch_address_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        # ``use_alter`` breaks the branch <-> branch_address create_all FK cycle:
        # this constraint is emitted as a separate ALTER after both tables exist.
        ForeignKey(
            "core.branch_address.branch_address_id",
            ondelete="SET NULL",
            use_alter=True,
            name="fk_branch_address",
        ),
        nullable=True,
        index=True,
    )
    timezone_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    working_hours: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="DRAFT"
    )
    opened_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    closed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class BranchAddress(Base, TimestampMixin, SoftDeleteMixin):
    """Branch address (ELU-BFS-PF-005 §9 / ELU-DDD-PF §5). One row per branch."""

    __tablename__ = "branch_address"
    __table_args__ = (
        UniqueConstraint("branch_id", name="uk_branch_address_branch"),
        {"schema": "core"},
    )

    branch_address_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("core.tenant.tenant_id"), nullable=False, index=True
    )
    branch_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.branch.branch_id", ondelete="CASCADE"),
        nullable=False,
    )
    address_line_1: Mapped[str] = mapped_column(String(255), nullable=False)
    address_line_2: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country_code: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default="IN"
    )
    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(9, 6), nullable=True)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class Department(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant department profile and hierarchy (ELU-BFS-PF-006 §7/§9 / ELU-DDD-PF §5).

    Batch 2 scope: ORM representation of ``core.department`` only. Deferred:
    ``users.department_id`` and the department -> users linkage (PF-008), department-head
    assignment/validation (BR-PF-043 -> PF-008), the hierarchy depth rule (BR-PF-041) and
    the circular-parent rule (BR-PF-042) — both service-layer concerns — and the
    NTF-PF-006-* / RPT-PF-006-* scopes.

    ``department_head_user_id`` is therefore a plain nullable UUID column with **no FK and
    no relationship** to ``User``. No persisted ``level``/``path`` columns (C-N2 — hierarchy
    information is derived at read time) and no ``department_type`` value restriction
    (C-N1 — the approved specification defines no value list).

    Indexes are owned by the PF-006 DDL (partial, soft-delete aware); this model therefore
    does not declare ``index=True``. The department-code uniqueness is declared here only
    because the DDL expects to replace this hard constraint with its soft-delete aware
    partial unique index ``uk_department_tenant_code_active`` (BR-PF-040), mirroring PF-005.
    """

    __tablename__ = "department"
    __table_args__ = (
        UniqueConstraint("tenant_id", "department_code", name="uk_department_tenant_code"),
        {"schema": "core"},
    )

    department_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id", name="fk_department_tenant"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "core.organization.organization_id",
            ondelete="RESTRICT",
            name="fk_department_organization",
        ),
        nullable=False,
    )
    parent_department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.department.department_id", ondelete="RESTRICT", name="fk_department_parent"),
        nullable=True,
    )
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.branch.branch_id", ondelete="SET NULL", name="fk_department_branch"),
        nullable=True,
    )
    department_code: Mapped[str] = mapped_column(String(30), nullable=False)
    department_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    department_type: Mapped[str] = mapped_column(String(32), nullable=False)
    department_head_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    cost_centre_code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE"
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


class BusinessUnit(Base, TimestampMixin, SoftDeleteMixin):
    """Tenant business unit profile (ELU-BFS-PF-007 §7/§9 / ELU-DDD-PF §5).

    Batch 1 scope: ORM representation of ``core.business_unit`` only. Deferred: the
    ``business_unit -> opportunity`` (CRM), ``-> project`` (PRJ) and ``-> invoice`` (FIN)
    relationships (D6 — a later controlled PF-007 batch), ``users.business_unit_id``
    (PF-008), notifications (``NTF-PF-007-*``), reports / XLSX-PDF export formatting (D8)
    and any history API (D1).

    ``bu_manager_user_id`` is a plain nullable UUID column with **no FK and no
    relationship** to ``User`` (D4) — ``BR-PF-048`` (ACTIVE same-tenant user) is enforced
    at the API/service layer, and no ``users`` column is introduced or modified.

    ``organization_id`` is assigned on creation and immutable afterwards (D7). The code
    uniqueness is declared here only because the DDL replaces this hard constraint with
    the soft-delete aware partial unique index ``uk_business_unit_tenant_code_active``
    (BR-PF-047 / D11), mirroring PF-005/PF-006.
    """

    __tablename__ = "business_unit"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "business_unit_code", name="uk_business_unit_tenant_code"
        ),
        {"schema": "core"},
    )

    business_unit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id", name="fk_business_unit_tenant"),
        nullable=False,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "core.organization.organization_id",
            ondelete="RESTRICT",
            name="fk_business_unit_organization",
        ),
        nullable=False,
    )
    business_unit_code: Mapped[str] = mapped_column(String(30), nullable=False)
    business_unit_name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bu_manager_user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    cost_centre_code: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    revenue_target_annual: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(18, 2), nullable=True
    )
    start_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE"
    )
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    modified_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


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


class UserRole(Base, TimestampMixin):
    """PF-009 M2M user<->role assignment (``core.user_role``).

    Transitional foundation (PF-009 Batch 1): ``core.users.role_id`` remains the
    authoritative single role for released behaviour and is NOT removed here, so
    this table is populated from it by the idempotent backfill in
    ``app.db.migrate_pf009`` and kept consistent going forward. Multi-role JWT/
    auth resolution is a later authorised batch.
    """

    __tablename__ = "user_role"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uk_user_role"),
        {"schema": "core"},
    )

    user_role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id"),
        nullable=False,
        index=True,
    )
    role_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.role.role_id"),
        nullable=False,
        index=True,
    )
    is_primary: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("true")
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

    # --- PF-008 CORE additions (see Documentation/PF008_CORE_IMPLEMENTATION_MAP.md) ---
    # Linkage to the released PF-005 / PF-006 / PF-007 structures (D9). Nullable with
    # ON DELETE SET NULL, mirroring ELU-BFS-PF-008 §8 (branch/department -> users).
    branch_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.branch.branch_id", ondelete="SET NULL", name="fk_users_branch"),
        nullable=True,
    )
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "core.department.department_id",
            ondelete="SET NULL",
            name="fk_users_department",
        ),
        nullable=True,
    )
    business_unit_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "core.business_unit.business_unit_id",
            ondelete="SET NULL",
            name="fk_users_business_unit",
        ),
        nullable=True,
    )
    # Authentication / lifecycle (BR-PF-054, BR-PF-055, BR-PF-057).
    failed_login_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0")
    )
    locked_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    invited_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    deactivated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    password_changed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reset_token_hash: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reset_token_expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sessions_invalid_before: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
    organization: Mapped["Organization"] = relationship()
    role: Mapped["Role"] = relationship()


class UserInvite(Base, TimestampMixin, SoftDeleteMixin):
    """Pending PF-008 user invitation (ELU-BFS-PF-008 §5/§7; D2).

    One ACTIVE invitation per user (partial unique index ``uk_user_invite_active_user``).
    The token itself is never stored — only its SHA-256 hash (D5). Invitations expire after
    72 hours (BR-PF-054); expiry is evaluated lazily by the service (D6), no scheduler.
    """

    __tablename__ = "user_invite"
    __table_args__ = {"schema": "core"}

    invite_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "core.tenant.tenant_id", ondelete="CASCADE", name="fk_user_invite_tenant"
        ),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.users.user_id", ondelete="CASCADE", name="fk_user_invite_user"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="ACTIVE"
    )
    expires_on: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    used_on: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


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


class TenantBranding(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tenant_branding"
    __table_args__ = {"schema": "core"}

    branding_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("core.tenant.tenant_id"),
        nullable=False,
        unique=True,
    )
    logo_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    primary_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    secondary_color: Mapped[Optional[str]] = mapped_column(String(16), nullable=True)
    favicon_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    tenant: Mapped["Tenant"] = relationship(back_populates="branding")
