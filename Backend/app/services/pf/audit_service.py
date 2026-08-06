import json
import logging
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

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
