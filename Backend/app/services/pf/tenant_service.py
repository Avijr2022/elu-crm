import json
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.db.seed import provision_tenant_roles
from app.models.pf import (
    IdempotencyKey,
    Organization,
    Subscription,
    Tenant,
    TenantAddress,
    TenantContact,
    TenantSettings,
    TenantStatusHistory,
)
from app.repositories.pf.edition_repository import EditionRepository
from app.schemas.pf.tenant import (
    TenantAddressOut,
    TenantContactOut,
    TenantCreate,
    TenantListResponse,
    TenantResponse,
    TenantSuspendRequest,
    TenantUpdate,
)
from app.services.pf.audit_service import write_audit_event
from app.services.pf.edition_service import EditionService


class TenantService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.editions = EditionRepository(db)

    def _to_response(self, tenant: Tenant) -> TenantResponse:
        org = tenant.organizations[0] if tenant.organizations else None
        sub = self.db.scalars(
            select(Subscription)
            .where(
                Subscription.tenant_id == tenant.tenant_id,
                Subscription.is_deleted.is_(False),
            )
            .order_by(Subscription.created_on.desc())
        ).first()
        return TenantResponse(
            id=tenant.tenant_id,
            code=tenant.tenant_code,
            legal_name=tenant.legal_name,
            trade_name=tenant.trade_name or tenant.tenant_name,
            status=tenant.status,
            edition_code=tenant.edition.code if tenant.edition else "",
            edition_id=tenant.edition_id,
            email=tenant.email,
            mobile=tenant.mobile,
            industry=tenant.industry,
            company_size=tenant.company_size,
            version_no=tenant.version_no,
            activated_on=tenant.activated_on,
            suspended_on=tenant.suspended_on,
            contacts=[
                TenantContactOut(
                    id=c.id,
                    contact_type=c.contact_type,
                    name=c.name,
                    email=c.email,
                    mobile=c.mobile,
                    is_primary=c.is_primary,
                )
                for c in tenant.contacts
                if not c.is_deleted
            ],
            addresses=[
                TenantAddressOut(
                    id=a.id,
                    address_type=a.address_type,
                    line1=a.line1,
                    line2=a.line2,
                    city=a.city,
                    state=a.state,
                    country=a.country,
                    postal_code=a.postal_code,
                )
                for a in tenant.addresses
                if not a.is_deleted
            ],
            organization_code=org.organization_code if org else None,
            subscription_number=sub.subscription_number if sub else None,
            subscription_status=sub.subscription_status if sub else None,
        )

    def _load(self, tenant_id: UUID) -> Optional[Tenant]:
        return self.db.scalars(
            select(Tenant)
            .options(
                selectinload(Tenant.edition),
                selectinload(Tenant.contacts),
                selectinload(Tenant.addresses),
                selectinload(Tenant.organizations),
                selectinload(Tenant.settings),
            )
            .where(Tenant.tenant_id == tenant_id, Tenant.is_deleted.is_(False))
        ).first()

    def _history(
        self, tenant: Tenant, to_status: str, actor_id: UUID, reason: Optional[str]
    ) -> None:
        self.db.add(
            TenantStatusHistory(
                id=uuid4(),
                tenant_id=tenant.tenant_id,
                from_status=tenant.status,
                to_status=to_status,
                reason=reason,
                actor_id=actor_id,
            )
        )

    def list_tenants(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> TenantListResponse:
        q = (
            select(Tenant)
            .options(
                selectinload(Tenant.edition),
                selectinload(Tenant.contacts),
                selectinload(Tenant.addresses),
                selectinload(Tenant.organizations),
            )
            .where(Tenant.is_deleted.is_(False))
        )
        if status:
            q = q.where(Tenant.status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Tenant.tenant_code.ilike(like),
                    Tenant.legal_name.ilike(like),
                    Tenant.tenant_name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        items = list(
            self.db.scalars(
                q.order_by(Tenant.created_on.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return TenantListResponse(
            items=[self._to_response(t) for t in items],
            page=page,
            page_size=page_size,
            total=int(total),
        )

    def get_tenant(self, tenant_id: UUID) -> TenantResponse:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        return self._to_response(tenant)

    def create(
        self, payload: TenantCreate, actor_id: UUID, *, idempotency_key: Optional[str] = None
    ) -> tuple[TenantResponse, int]:
        if idempotency_key:
            existing = self.db.get(IdempotencyKey, idempotency_key)
            if existing:
                body = json.loads(existing.response_body)
                return TenantResponse.model_validate(body), existing.response_status

        if self.db.scalars(
            select(Tenant).where(Tenant.tenant_code == payload.code)
        ).first():
            raise ConflictError("Tenant code already exists", req_id="BR-PF-009")

        if self.db.scalars(
            select(Tenant).where(
                func.lower(Tenant.legal_name) == payload.legal_name.lower(),
                Tenant.is_deleted.is_(False),
            )
        ).first():
            raise ConflictError("legal_name already exists", req_id="BR-PF-010")

        edition = self.editions.get_by_code(payload.edition_code.upper())
        if edition is None:
            raise ValidationAppError("Edition not found", req_id="BR-PF-013")
        EditionService(self.db).assert_assignable(edition)

        if payload.primary_contact.contact_type != "PRIMARY":
            raise ValidationAppError(
                "primary_contact.contact_type must be PRIMARY", req_id="BR-PF-011"
            )
        if payload.registered_address.address_type != "REGISTERED":
            raise ValidationAppError(
                "registered_address.address_type must be REGISTERED",
                req_id="BR-PF-012",
            )

        settings = get_settings()
        tenant = Tenant(
            tenant_id=uuid4(),
            tenant_code=payload.code,
            tenant_name=payload.trade_name or payload.legal_name,
            trade_name=payload.trade_name or payload.legal_name,
            legal_name=payload.legal_name,
            edition_id=edition.id,
            organization_type=payload.organization_type,
            email=str(payload.email).lower(),
            mobile=payload.mobile,
            industry=payload.industry,
            company_size=payload.company_size,
            provision_source="MANUAL",
            status="PENDING_ACTIVATION",
            created_by=actor_id,
            version_no=1,
        )
        tenant.contacts.append(
            TenantContact(
                id=uuid4(),
                contact_type="PRIMARY",
                name=payload.primary_contact.name,
                email=str(payload.primary_contact.email).lower(),
                mobile=payload.primary_contact.mobile,
                is_primary=True,
                created_by=actor_id,
            )
        )
        addr = payload.registered_address
        tenant.addresses.append(
            TenantAddress(
                id=uuid4(),
                address_type="REGISTERED",
                line1=addr.line1,
                line2=addr.line2,
                city=addr.city,
                state=addr.state,
                country=addr.country,
                postal_code=addr.postal_code,
                created_by=actor_id,
            )
        )
        self.db.add(tenant)
        self.db.flush()

        org = Organization(
            organization_id=uuid4(),
            tenant_id=tenant.tenant_id,
            organization_code="HO001",
            organization_name=f"{tenant.trade_name} Head Office",
            legal_name=tenant.legal_name,
            organization_type="ROOT",
            email=tenant.email,
            phone=tenant.mobile,
            status="ACTIVE",
            is_root=True,
            level=0,
            default_currency_code=settings.default_currency,
            fiscal_year_start_month=settings.default_fy_start_month,
            created_by=actor_id,
        )
        self.db.add(org)

        fy_start = date(
            date.today().year if date.today().month >= 4 else date.today().year - 1,
            settings.default_fy_start_month,
            settings.default_fy_start_day,
        )
        self.db.add(
            TenantSettings(
                setting_id=uuid4(),
                tenant_id=tenant.tenant_id,
                financial_year_start=fy_start,
                currency_code=settings.default_currency,
                time_zone=settings.default_timezone,
                date_format=settings.default_date_format,
                default_language=settings.default_language,
            )
        )

        sub_no = f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"
        self.db.add(
            Subscription(
                subscription_id=uuid4(),
                tenant_id=tenant.tenant_id,
                edition_id=edition.id,
                subscription_number=sub_no,
                plan_type="Trial",
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                amount="0",
                currency_code="INR",
                payment_status="PENDING",
                subscription_status="TRIAL",
            )
        )

        self._history(tenant, "PENDING_ACTIVATION", actor_id, "Registered")
        write_audit_event(
            self.db,
            event_type="TENANT_CREATED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
            payload={"code": tenant.tenant_code, "status": tenant.status},
        )
        self.db.flush()
        resp = self._to_response(self._load(tenant.tenant_id))  # type: ignore[arg-type]
        if idempotency_key:
            self.db.add(
                IdempotencyKey(
                    key=idempotency_key,
                    tenant_id=tenant.tenant_id,
                    request_path="/POST /platform/tenants",
                    response_status=201,
                    response_body=resp.model_dump_json(),
                )
            )
        self.db.commit()
        return resp, 201

    def update(
        self, tenant_id: UUID, payload: TenantUpdate, actor_id: UUID
    ) -> TenantResponse:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        if tenant.version_no != payload.version_no:
            raise ConflictError("Tenant version conflict", req_id="PF-002")
        if payload.legal_name is not None:
            tenant.legal_name = payload.legal_name
        if payload.trade_name is not None:
            tenant.trade_name = payload.trade_name
            tenant.tenant_name = payload.trade_name
        if payload.email is not None:
            tenant.email = str(payload.email).lower()
        if payload.mobile is not None:
            tenant.mobile = payload.mobile
        if payload.industry is not None:
            tenant.industry = payload.industry
        if payload.company_size is not None:
            tenant.company_size = payload.company_size
        if payload.website is not None:
            tenant.website = payload.website
        tenant.version_no += 1
        tenant.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="TENANT_UPDATED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
            payload={"code": tenant.tenant_code},
        )
        self.db.commit()
        return self._to_response(self._load(tenant_id))  # type: ignore[arg-type]

    def approve(self, tenant_id: UUID, actor_id: UUID, version_no: int) -> TenantResponse:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        if tenant.version_no != version_no:
            raise ConflictError("Tenant version conflict", req_id="PF-002")
        if tenant.status != "PENDING_ACTIVATION":
            raise ValidationAppError(
                "Only PENDING_ACTIVATION tenants can be approved", req_id="REQ-PF-005"
            )
        self._history(tenant, "ACTIVE", actor_id, "Approved / activated (platform)")
        tenant.status = "ACTIVE"
        tenant.activated_on = datetime.now(timezone.utc)
        tenant.activation_date = date.today()
        tenant.version_no += 1
        tenant.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="TENANT_APPROVED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
        )
        provision_tenant_roles(self.db, tenant.tenant_id)
        self.db.commit()
        return self._to_response(self._load(tenant_id))  # type: ignore[arg-type]

    def suspend(
        self, tenant_id: UUID, payload: TenantSuspendRequest, actor_id: UUID
    ) -> TenantResponse:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        if tenant.version_no != payload.version_no:
            raise ConflictError("Tenant version conflict", req_id="PF-002")
        if tenant.status not in {"ACTIVE", "TRIAL"}:
            raise ValidationAppError(
                "Only ACTIVE/TRIAL tenants can be suspended", req_id="REQ-PF-006"
            )
        self._history(tenant, "SUSPENDED", actor_id, payload.reason)
        tenant.status = "SUSPENDED"
        tenant.suspended_on = datetime.now(timezone.utc)
        tenant.version_no += 1
        tenant.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="TENANT_SUSPENDED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
            payload={"reason": payload.reason},
        )
        self.db.commit()
        return self._to_response(self._load(tenant_id))  # type: ignore[arg-type]

    def reactivate(
        self, tenant_id: UUID, actor_id: UUID, version_no: int
    ) -> TenantResponse:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        if tenant.version_no != version_no:
            raise ConflictError("Tenant version conflict", req_id="PF-002")
        if tenant.status != "SUSPENDED":
            raise ValidationAppError(
                "Only SUSPENDED tenants can be reactivated", req_id="PF-002"
            )
        self._history(tenant, "ACTIVE", actor_id, "Reactivated")
        tenant.status = "ACTIVE"
        tenant.suspended_on = None
        tenant.version_no += 1
        tenant.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="TENANT_REACTIVATED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
        )
        self.db.commit()
        return self._to_response(self._load(tenant_id))  # type: ignore[arg-type]

    def soft_delete(self, tenant_id: UUID, actor_id: UUID) -> None:
        tenant = self._load(tenant_id)
        if tenant is None:
            raise NotFoundError("Tenant not found", req_id="PF-002")
        self._history(tenant, "CLOSED", actor_id, "Soft close")
        tenant.status = "CLOSED"
        tenant.is_deleted = True
        tenant.is_active = False
        tenant.version_no += 1
        tenant.modified_by = actor_id
        write_audit_event(
            self.db,
            event_type="TENANT_DELETED",
            event_category="TENANT",
            entity_type="tenant",
            entity_id=tenant.tenant_id,
            actor_id=actor_id,
        )
        self.db.commit()

    def export_rows(self) -> list[dict]:
        listed = self.list_tenants(page=1, page_size=100)
        return [
            {
                "code": t.code,
                "legal_name": t.legal_name,
                "status": t.status,
                "edition_code": t.edition_code,
            }
            for t in listed.items
        ]


def require_platform_admin(role_code: str) -> None:
    if role_code != "PLATFORM_ADMIN":
        raise ForbiddenError(
            "Platform Admin role required for tenant management",
            req_id="PF-002",
        )
