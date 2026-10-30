"""TD-PF-003-01 — expire TRIAL subscriptions whose trial_end_date is due (UTC)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal
from app.models.pf import Subscription
from app.services.pf.subscription_service import SubscriptionService

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TrialExpiryJobResult:
    processed: int
    failed: int


def utc_today() -> date:
    return datetime.now(timezone.utc).date()


def due_trial_subscription_rows(
    db: Session, as_of_utc_date: date
) -> list[tuple]:
    """Return (subscription_id, version_no) for due non-deleted TRIAL rows."""
    stmt = (
        select(Subscription.subscription_id, Subscription.version_no)
        .where(
            Subscription.is_deleted.is_(False),
            Subscription.subscription_status == "TRIAL",
            Subscription.trial_end_date.isnot(None),
            Subscription.trial_end_date <= as_of_utc_date,
        )
        .order_by(Subscription.trial_end_date, Subscription.subscription_id)
    )
    return list(db.execute(stmt).all())


def run_expire_due_trial_subscriptions(
    *,
    as_of_utc_date: date | None = None,
    db: Session | None = None,
) -> TrialExpiryJobResult:
    """Expire all due TRIAL subscriptions using SubscriptionService.expire()."""
    as_of = as_of_utc_date or utc_today()
    owns_session = db is None
    session = db or SessionLocal()
    processed = 0
    failed = 0
    try:
        bind_rls_context(session, platform=True)
        due_rows = due_trial_subscription_rows(session, as_of)
        svc = SubscriptionService(session)
        for subscription_id, version_no in due_rows:
            try:
                svc.expire(subscription_id, None, version_no)
                processed += 1
            except Exception:
                session.rollback()
                failed += 1
                logger.exception(
                    "trial expiry failed subscription_id=%s version_no=%s",
                    subscription_id,
                    version_no,
                )
        logger.info(
            "trial subscription expiry job finished as_of=%s processed=%s failed=%s",
            as_of.isoformat(),
            processed,
            failed,
        )
        return TrialExpiryJobResult(processed=processed, failed=failed)
    finally:
        if owns_session:
            clear_rls_context(session)
            session.close()
