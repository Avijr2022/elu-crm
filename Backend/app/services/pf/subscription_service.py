from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.exceptions import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.models.pf import (
    Edition,
    Subscription,
    SubscriptionHistory,
    SubscriptionUsage,
    Tenant,
    User,
)
from app.repositories.pf.edition_repository import EditionRepository
from app.schemas.pf.subscription import (
    SubscriptionCancelRequest,
    SubscriptionCreate,
    SubscriptionHistoryOut,
    SubscriptionListResponse,
    SubscriptionRenewRequest,
    SubscriptionResponse,
    SubscriptionUpdate,
    SubscriptionUpgradeRequest,
    SubscriptionUsageResponse,
)
from app.services.pf.audit_service import write_audit_event
from app.services.pf.edition_service import EditionService


CURRENT_STATUSES = {"ACTIVE", "TRIAL"}
VALID_STATUSES = {
    "TRIAL",
    "ACTIVE",
    "RENEWAL_PENDING",
    "PAST_DUE",
    "EXPIRED",
    "CANCELLED",
    "SUSPENDED",
}


class SubscriptionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.editions = EditionRepository(db)

    def _active_user_count(self, tenant_id: UUID) -> int:
        return int(
            self.db.scalar(
                select(func.count())
                .select_from(User)
                .where(
                    User.tenant_id == tenant_id,
                    User.is_deleted.is_(False),
                    User.is_active.is_(True),
                    User.account_status == "ACTIVE",
                )
            )
            or 0
        )

    def _edition_max_users(self, edition: Edition) -> Optional[int]:
        for lim in edition.limits:
            if lim.limit_code.upper() == "MAX_USERS":
                try:
                    return int(Decimal(str(lim.limit_value)))
                except Exception:
                    return None
        return None

    def _assert_seats_vs_edition(self, edition: Edition, seat_count: int) -> None:
        max_users = self._edition_max_users(edition)
        if max_users is not None and seat_count > max_users:
            raise ValidationAppError(
                f"seat_count {seat_count} exceeds edition MAX_USERS {max_users}",
                req_id="BR-PF-021",
            )

    def _assert_seats_vs_users(self, tenant_id: UUID, seat_count: int) -> None:
        used = self._active_user_count(tenant_id)
        if seat_count < used:
            raise ValidationAppError(
                f"seat_count {seat_count} below active user count {used}",
                req_id="BR-PF-027",
            )

    def _history(
        self,
        sub: Subscription,
        *,
        change_type: str,
        actor_id: UUID,
        from_status: Optional[str],
        to_status: Optional[str],
        from_edition_id: Optional[UUID] = None,
        to_edition_id: Optional[UUID] = None,
        from_seat_count: Optional[int] = None,
        to_seat_count: Optional[int] = None,
        reason: Optional[str] = None,
    ) -> None:
        self.db.add(
            SubscriptionHistory(
                id=uuid4(),
                tenant_id=sub.tenant_id,
                subscription_id=sub.subscription_id,
                change_type=change_type,
                from_status=from_status,
                to_status=to_status,
                from_edition_id=from_edition_id,
                to_edition_id=to_edition_id,
                from_seat_count=from_seat_count,
                to_seat_count=to_seat_count,
                reason=reason,
                actor_id=actor_id,
            )
        )

    def _attach_current(self, tenant: Tenant, sub: Subscription) -> None:
        if sub.subscription_status in CURRENT_STATUSES:
            tenant.current_subscription_id = sub.subscription_id

    def _to_response(self, sub: Subscription) -> SubscriptionResponse:
        tenant = self.db.get(Tenant, sub.tenant_id)
        used = self._active_user_count(sub.tenant_id)
        return SubscriptionResponse(
            id=sub.subscription_id,
            tenant_id=sub.tenant_id,
            tenant_code=tenant.tenant_code if tenant else None,
            subscription_number=sub.subscription_number,
            edition_id=sub.edition_id,
            edition_code=sub.edition.code if sub.edition else "",
            status=sub.subscription_status,
            plan_type=sub.plan_type,
            billing_cycle=sub.billing_cycle or "MONTHLY",
            seat_count=sub.seat_count or 10,
            seat_count_used=used,
            start_date=sub.start_date,
            end_date=sub.end_date,
            trial_end_date=sub.trial_end_date,
            amount=sub.amount,
            currency_code=sub.currency_code,
            payment_status=sub.payment_status,
            version_no=sub.version_no,
            cancellation_reason=sub.cancellation_reason,
        )

    def _load(self, subscription_id: UUID) -> Optional[Subscription]:
        return self.db.scalars(
            select(Subscription)
            .options(selectinload(Subscription.edition).selectinload(Edition.limits))
            .where(
                Subscription.subscription_id == subscription_id,
                Subscription.is_deleted.is_(False),
            )
        ).first()

    def _current_for_tenant(self, tenant_id: UUID) -> Optional[Subscription]:
        tenant = self.db.get(Tenant, tenant_id)
        if tenant and tenant.current_subscription_id:
            sub = self._load(tenant.current_subscription_id)
            if sub and sub.subscription_status in CURRENT_STATUSES:
                return sub
        return self.db.scalars(
            select(Subscription)
            .options(selectinload(Subscription.edition).selectinload(Edition.limits))
            .where(
                Subscription.tenant_id == tenant_id,
                Subscription.is_deleted.is_(False),
                Subscription.subscription_status.in_(tuple(CURRENT_STATUSES)),
            )
            .order_by(Subscription.created_on.desc())
        ).first()

    def list_subscriptions(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> SubscriptionListResponse:
        q = (
            select(Subscription)
            .options(selectinload(Subscription.edition))
            .where(Subscription.is_deleted.is_(False))
        )
        if status:
            q = q.where(Subscription.subscription_status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            q = q.join(Tenant, Tenant.tenant_id == Subscription.tenant_id).where(
                or_(
                    Subscription.subscription_number.ilike(like),
                    Tenant.tenant_code.ilike(like),
                    Tenant.legal_name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        items = list(
            self.db.scalars(
                q.order_by(Subscription.created_on.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return SubscriptionListResponse(
            items=[self._to_response(s) for s in items],
            page=page,
            page_size=page_size,
            total=int(total),
        )

    def get(self, subscription_id: UUID) -> SubscriptionResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        return self._to_response(sub)

    def create(self, payload: SubscriptionCreate, actor_id: UUID) -> SubscriptionResponse:
        tenant = self.db.get(Tenant, payload.tenant_id)
        if tenant is None or tenant.is_deleted:
            raise NotFoundError("Tenant not found", req_id="PF-003")
        if payload.end_date <= payload.start_date:
            raise ValidationAppError(
                "end_date must be after start_date", req_id="BR-PF-020"
            )
        status = payload.status.upper()
        if status not in {"ACTIVE", "TRIAL"}:
            raise ValidationAppError(
                "Create status must be ACTIVE or TRIAL", req_id="PF-003"
            )
        if status == "TRIAL":
            max_trial = payload.start_date + timedelta(days=30)
            if payload.end_date > max_trial:
                raise ValidationAppError(
                    "Trial duration cannot exceed 30 days", req_id="BR-PF-025"
                )

        existing = self._current_for_tenant(tenant.tenant_id)
        if existing and status in CURRENT_STATUSES:
            raise ConflictError(
                "Tenant already has an ACTIVE or TRIAL subscription",
                req_id="BR-PF-019",
            )

        edition = self.editions.get_by_code(payload.edition_code.upper())
        if edition is None:
            raise ValidationAppError("Edition not found", req_id="BR-PF-013")
        EditionService(self.db).assert_assignable(edition)
        self._assert_seats_vs_edition(edition, payload.seat_count)
        self._assert_seats_vs_users(tenant.tenant_id, payload.seat_count)

        cycle = payload.billing_cycle.upper()
        if cycle not in {"MONTHLY", "ANNUAL", "QUARTERLY"}:
            raise ValidationAppError("Invalid billing_cycle", req_id="PF-003")

        sub_no = (
            f"SUB-{datetime.now(timezone.utc).strftime('%Y%m%d')}-"
            f"{uuid4().hex[:6].upper()}"
        )
        sub = Subscription(
            subscription_id=uuid4(),
            tenant_id=tenant.tenant_id,
            edition_id=edition.id,
            subscription_number=sub_no,
            plan_type=payload.plan_type,
            billing_cycle=cycle,
            seat_count=payload.seat_count,
            start_date=payload.start_date,
            end_date=payload.end_date,
            trial_end_date=payload.end_date if status == "TRIAL" else None,
            amount=payload.amount,
            currency_code=payload.currency_code.upper(),
            payment_status="PENDING" if status == "TRIAL" else "PAID",
            subscription_status=status,
            created_by=actor_id,
            version_no=1,
        )
        self.db.add(sub)
        self.db.flush()
        tenant.edition_id = edition.id
        self._attach_current(tenant, sub)
        self._history(
            sub,
            change_type="CREATED",
            actor_id=actor_id,
            from_status=None,
            to_status=status,
            to_edition_id=edition.id,
            to_seat_count=payload.seat_count,
            reason="Created",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_CREATED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=tenant.tenant_id,
            payload={"number": sub_no, "status": status},
        )
        self.db.commit()
        return self._to_response(self._load(sub.subscription_id))  # type: ignore[arg-type]

    def update(
        self, subscription_id: UUID, payload: SubscriptionUpdate, actor_id: UUID
    ) -> SubscriptionResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != payload.version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status in {"CANCELLED", "EXPIRED"}:
            raise ValidationAppError(
                f"Cannot update subscription in status {sub.subscription_status}",
                req_id="PF-003",
            )
        from_seats = sub.seat_count
        if payload.seat_count is not None:
            self._assert_seats_vs_edition(sub.edition, payload.seat_count)
            self._assert_seats_vs_users(sub.tenant_id, payload.seat_count)
            sub.seat_count = payload.seat_count
        if payload.billing_cycle is not None:
            cycle = payload.billing_cycle.upper()
            if cycle not in {"MONTHLY", "ANNUAL", "QUARTERLY"}:
                raise ValidationAppError("Invalid billing_cycle", req_id="PF-003")
            sub.billing_cycle = cycle
        if payload.end_date is not None:
            if payload.end_date <= sub.start_date:
                raise ValidationAppError(
                    "end_date must be after start_date", req_id="BR-PF-020"
                )
            sub.end_date = payload.end_date
        if payload.amount is not None:
            sub.amount = payload.amount
        sub.version_no += 1
        sub.modified_by = actor_id
        self._history(
            sub,
            change_type="UPDATED",
            actor_id=actor_id,
            from_status=sub.subscription_status,
            to_status=sub.subscription_status,
            from_seat_count=from_seats,
            to_seat_count=sub.seat_count,
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_UPDATED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def convert_trial_to_active(
        self, subscription_id: UUID, actor_id: UUID, version_no: int
    ) -> SubscriptionResponse:
        """PATCH convenience: TRIAL → ACTIVE."""
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status != "TRIAL":
            raise ValidationAppError(
                "Only TRIAL subscriptions can be activated", req_id="PF-003"
            )
        from_status = sub.subscription_status
        sub.subscription_status = "ACTIVE"
        sub.plan_type = "Paid"
        sub.payment_status = "PAID"
        sub.version_no += 1
        sub.modified_by = actor_id
        tenant = self.db.get(Tenant, sub.tenant_id)
        if tenant:
            self._attach_current(tenant, sub)
        self._history(
            sub,
            change_type="ACTIVATED",
            actor_id=actor_id,
            from_status=from_status,
            to_status="ACTIVE",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_ACTIVATED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def renew(
        self, subscription_id: UUID, payload: SubscriptionRenewRequest, actor_id: UUID
    ) -> SubscriptionResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != payload.version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status not in {"ACTIVE", "RENEWAL_PENDING", "PAST_DUE"}:
            raise ValidationAppError(
                "Only ACTIVE/RENEWAL_PENDING/PAST_DUE can renew", req_id="PF-003"
            )
        if payload.end_date <= sub.start_date:
            raise ValidationAppError(
                "end_date must be after start_date", req_id="BR-PF-020"
            )
        from_seats = sub.seat_count
        seats = payload.seat_count if payload.seat_count is not None else sub.seat_count
        self._assert_seats_vs_edition(sub.edition, seats)
        self._assert_seats_vs_users(sub.tenant_id, seats)
        from_status = sub.subscription_status
        sub.end_date = payload.end_date
        sub.seat_count = seats
        if payload.billing_cycle:
            cycle = payload.billing_cycle.upper()
            if cycle not in {"MONTHLY", "ANNUAL", "QUARTERLY"}:
                raise ValidationAppError("Invalid billing_cycle", req_id="PF-003")
            sub.billing_cycle = cycle
        sub.subscription_status = "ACTIVE"
        sub.payment_status = "PAID"
        sub.version_no += 1
        sub.modified_by = actor_id
        self._history(
            sub,
            change_type="RENEWED",
            actor_id=actor_id,
            from_status=from_status,
            to_status="ACTIVE",
            from_seat_count=from_seats,
            to_seat_count=seats,
            reason="Renewed",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_RENEWED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def upgrade(
        self, subscription_id: UUID, payload: SubscriptionUpgradeRequest, actor_id: UUID
    ) -> SubscriptionResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != payload.version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status not in CURRENT_STATUSES:
            raise ValidationAppError(
                "Only ACTIVE/TRIAL subscriptions can upgrade", req_id="PF-003"
            )
        edition = self.editions.get_by_code(payload.edition_code.upper())
        if edition is None:
            raise ValidationAppError("Edition not found", req_id="BR-PF-013")
        EditionService(self.db).assert_assignable(edition)
        seats = payload.seat_count if payload.seat_count is not None else sub.seat_count
        used = self._active_user_count(sub.tenant_id)
        max_users = self._edition_max_users(edition)
        if max_users is not None and used > max_users:
            raise ValidationAppError(
                "Cannot downgrade/change edition: active users exceed new edition limit",
                req_id="BR-PF-023",
            )
        self._assert_seats_vs_edition(edition, seats)
        self._assert_seats_vs_users(sub.tenant_id, seats)

        from_edition = sub.edition_id
        from_seats = sub.seat_count
        from_status = sub.subscription_status
        sub.edition_id = edition.id
        sub.seat_count = seats
        sub.version_no += 1
        sub.modified_by = actor_id
        tenant = self.db.get(Tenant, sub.tenant_id)
        if tenant:
            tenant.edition_id = edition.id
            self._attach_current(tenant, sub)
        self._history(
            sub,
            change_type="UPGRADED",
            actor_id=actor_id,
            from_status=from_status,
            to_status=from_status,
            from_edition_id=from_edition,
            to_edition_id=edition.id,
            from_seat_count=from_seats,
            to_seat_count=seats,
            reason=f"Upgrade to {edition.code}",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_UPGRADED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
            payload={"edition": edition.code},
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def cancel(
        self, subscription_id: UUID, payload: SubscriptionCancelRequest, actor_id: UUID
    ) -> None:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != payload.version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status == "CANCELLED":
            raise ValidationAppError("Already cancelled", req_id="PF-003")
        from_status = sub.subscription_status
        sub.subscription_status = "CANCELLED"
        sub.cancellation_reason = payload.reason
        sub.is_deleted = True
        sub.is_active = False
        sub.version_no += 1
        sub.modified_by = actor_id
        tenant = self.db.get(Tenant, sub.tenant_id)
        if tenant:
            if tenant.current_subscription_id == sub.subscription_id:
                tenant.current_subscription_id = None
            # BFS §5 — CANCELLED cascades tenant to OFFBOARDING
            if from_status in {
                "ACTIVE",
                "TRIAL",
                "RENEWAL_PENDING",
                "PAST_DUE",
                "SUSPENDED",
            } and tenant.status not in {"CLOSED", "ARCHIVED", "CANCELLED"}:
                tenant.status = "OFFBOARDING"
        self._history(
            sub,
            change_type="CANCELLED",
            actor_id=actor_id,
            from_status=from_status,
            to_status="CANCELLED",
            reason=payload.reason,
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_CANCELLED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
            payload={"reason": payload.reason},
        )
        self.db.commit()

    def expire(
        self, subscription_id: UUID, actor_id: UUID, version_no: int
    ) -> SubscriptionResponse:
        """Mark EXPIRED and cascade tenant → SUSPENDED (BR-PF-024)."""
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status in {"EXPIRED", "CANCELLED"}:
            raise ValidationAppError(
                f"Cannot expire status {sub.subscription_status}", req_id="PF-003"
            )
        from_status = sub.subscription_status
        sub.subscription_status = "EXPIRED"
        sub.version_no += 1
        sub.modified_by = actor_id
        tenant = self.db.get(Tenant, sub.tenant_id)
        if tenant:
            if tenant.current_subscription_id == sub.subscription_id:
                tenant.current_subscription_id = None
            if tenant.status in {"ACTIVE", "TRIAL"}:
                tenant.status = "SUSPENDED"
                tenant.suspended_on = datetime.now(timezone.utc)
        self._history(
            sub,
            change_type="EXPIRED",
            actor_id=actor_id,
            from_status=from_status,
            to_status="EXPIRED",
            reason="Expired — tenant suspended (BR-PF-024)",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_EXPIRED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def reactivate(
        self, subscription_id: UUID, actor_id: UUID, version_no: int
    ) -> SubscriptionResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        if sub.version_no != version_no:
            raise ConflictError("Subscription version conflict", req_id="PF-003")
        if sub.subscription_status not in {"EXPIRED", "SUSPENDED", "PAST_DUE"}:
            raise ValidationAppError(
                "Only EXPIRED/SUSPENDED/PAST_DUE can reactivate", req_id="PF-003"
            )
        existing = self._current_for_tenant(sub.tenant_id)
        if existing and existing.subscription_id != sub.subscription_id:
            raise ConflictError(
                "Tenant already has another ACTIVE/TRIAL subscription",
                req_id="BR-PF-019",
            )
        from_status = sub.subscription_status
        sub.subscription_status = "ACTIVE"
        sub.is_deleted = False
        sub.is_active = True
        sub.payment_status = "PAID"
        sub.version_no += 1
        sub.modified_by = actor_id
        tenant = self.db.get(Tenant, sub.tenant_id)
        if tenant:
            self._attach_current(tenant, sub)
            if tenant.status == "SUSPENDED":
                tenant.status = "ACTIVE"
                tenant.suspended_on = None
        self._history(
            sub,
            change_type="REACTIVATED",
            actor_id=actor_id,
            from_status=from_status,
            to_status="ACTIVE",
        )
        write_audit_event(
            self.db,
            event_type="SUBSCRIPTION_REACTIVATED",
            event_category="SUBSCRIPTION",
            entity_type="subscription",
            entity_id=sub.subscription_id,
            actor_id=actor_id,
            tenant_id=sub.tenant_id,
        )
        self.db.commit()
        return self._to_response(self._load(subscription_id))  # type: ignore[arg-type]

    def history(self, subscription_id: UUID) -> list[SubscriptionHistoryOut]:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        rows = self.db.scalars(
            select(SubscriptionHistory)
            .where(SubscriptionHistory.subscription_id == subscription_id)
            .order_by(SubscriptionHistory.changed_on.desc())
        ).all()
        return [
            SubscriptionHistoryOut(
                id=r.id,
                change_type=r.change_type,
                from_status=r.from_status,
                to_status=r.to_status,
                from_edition_id=r.from_edition_id,
                to_edition_id=r.to_edition_id,
                from_seat_count=r.from_seat_count,
                to_seat_count=r.to_seat_count,
                reason=r.reason,
                changed_on=r.changed_on,
            )
            for r in rows
        ]

    def usage(self, subscription_id: UUID) -> SubscriptionUsageResponse:
        sub = self._load(subscription_id)
        if sub is None:
            raise NotFoundError("Subscription not found", req_id="PF-003")
        used = self._active_user_count(sub.tenant_id)
        self.db.add(
            SubscriptionUsage(
                id=uuid4(),
                tenant_id=sub.tenant_id,
                subscription_id=sub.subscription_id,
                metric_code="USERS",
                used_value=str(used),
            )
        )
        self.db.commit()
        return SubscriptionUsageResponse(
            subscription_id=sub.subscription_id,
            seat_count=sub.seat_count,
            seat_count_used=used,
            seats_remaining=max(0, sub.seat_count - used),
            edition_code=sub.edition.code if sub.edition else "",
            status=sub.subscription_status,
            metrics=[{"metric_code": "USERS", "used_value": str(used)}],
        )

    def tenant_current(self, tenant_id: UUID) -> SubscriptionResponse:
        sub = self._current_for_tenant(tenant_id)
        if sub is None:
            raise NotFoundError("No current subscription", req_id="BR-PF-019")
        tenant = self.db.get(Tenant, tenant_id)
        if tenant and tenant.current_subscription_id != sub.subscription_id:
            tenant.current_subscription_id = sub.subscription_id
            self.db.commit()
        return self._to_response(sub)

    def export_rows(self) -> list[dict]:
        listed = self.list_subscriptions(page=1, page_size=200)
        return [
            {
                "subscription_number": s.subscription_number,
                "tenant_code": s.tenant_code,
                "status": s.status,
                "edition_code": s.edition_code,
                "seat_count": s.seat_count,
            }
            for s in listed.items
        ]


def require_platform_admin(role_code: str) -> None:
    if role_code != "PLATFORM_ADMIN":
        raise ForbiddenError(
            "Platform Admin role required for subscription management",
            req_id="PF-003",
        )
