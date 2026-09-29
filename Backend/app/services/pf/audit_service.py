import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import delete, text
from sqlalchemy.orm import Session

from app.db.rls_context import owner_role
from app.models.pf import AuditEvent

logger = logging.getLogger("elinkup.audit")


def write_audit_event(
    db: Session,
    *,
    event_type: str,
    event_category: str,
    entity_type: str,
    entity_id: Optional[UUID],
    actor_id: Optional[UUID] = None,
    actor_email: Optional[str] = None,
    tenant_id: Optional[UUID] = None,
    payload: Optional[dict[str, Any]] = None,
) -> AuditEvent:
    """Persist audit.audit_event and emit structured log (ELU-CON / BFS §15)."""
    event = AuditEvent(
        id=uuid4(),
        tenant_id=tenant_id,
        event_type=event_type,
        event_category=event_category,
        actor_id=actor_id,
        actor_email=actor_email,
        entity_type=entity_type,
        entity_id=entity_id,
        payload_json=json.dumps(payload or {}, default=str),
    )
    db.add(event)
    logger.info(
        "audit event_type=%s entity=%s/%s actor=%s",
        event_type,
        entity_type,
        entity_id,
        actor_id,
    )
    return event


# --- PF-010 Audit & Compliance: retention (AC-PF-010-03) ---------------------

# Audit retention windows per edition, in days (ELU-EDM-001).
AUDIT_RETENTION_DAYS_BY_EDITION: dict[str, int] = {
    "COMMUNITY": 90,
    "PROFESSIONAL": 365,
    "ENTERPRISE": 2555,  # 7 years
}


def retention_days_for_edition(edition_code: str) -> int:
    """Return the audit-retention window in days for an edition code (ELU-EDM-001)."""
    key = (edition_code or "").strip().upper()
    if key not in AUDIT_RETENTION_DAYS_BY_EDITION:
        raise ValueError(f"unknown edition code for audit retention: {edition_code!r}")
    return AUDIT_RETENTION_DAYS_BY_EDITION[key]


def purge_expired_audit_events(
    db: Session,
    *,
    retention_days: int,
    tenant_id: Optional[UUID] = None,
    now: Optional[datetime] = None,
) -> int:
    """Delete audit events older than the retention window; return rows removed.

    AC-PF-010-03 CORE: retention is exposed as a callable operation. The scheduled
    trigger (JOB-PF-010-01) is deferred, so callers invoke this explicitly.

    Deletion runs under the owner role because elu_app holds no DELETE on
    audit.audit_event (019_audit_pf010.sql). The BEFORE UPDATE trigger on the same
    table keeps rows append-only for every role, so this retention path is the
    only way rows leave the table.

    The caller owns the transaction; this function does not commit. Elevation is
    explicit: owner_role() only re-binds the session role on the next transaction
    begin, and the caller's session is usually already inside one (where
    after_begin pinned SET LOCAL ROLE elu_app). Statements the caller issues after
    this call run as the login role until the next transaction begins.
    """
    if retention_days < 0:
        raise ValueError("retention_days must not be negative")
    cutoff = (now or datetime.now(timezone.utc)) - timedelta(days=retention_days)
    stmt = delete(AuditEvent).where(AuditEvent.created_on < cutoff)
    if tenant_id is not None:
        stmt = stmt.where(AuditEvent.tenant_id == tenant_id)
    with owner_role():
        db.execute(text("RESET ROLE"))
        result = db.execute(stmt)
    removed = int(result.rowcount or 0)
    logger.info(
        "audit retention purge removed=%s cutoff=%s tenant=%s",
        removed,
        cutoff.isoformat(),
        tenant_id,
    )
    return removed
