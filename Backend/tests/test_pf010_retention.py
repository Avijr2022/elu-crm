"""PF-010 AC-PF-010-03 — audit retention purge.

Retention is exposed as a callable operation; the scheduled trigger JOB-PF-010-01
is deferred (see the PF-010 AC-03 retention decision record). Sessions are created
inside each test so importing this module never touches the database.
"""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import text

from app.db.migrate_pf010 import apply_pf010_ddl
from app.db.rls_context import owner_role
from app.db.session import SessionLocal
from app.services.pf.audit_service import (
    AUDIT_RETENTION_DAYS_BY_EDITION,
    purge_expired_audit_events,
    retention_days_for_edition,
)

_INSERT_SQL = text(
    "INSERT INTO audit.audit_event "
    "(id, tenant_id, event_type, event_category, entity_type, created_on, payload_json) "
    "VALUES (:id, :tenant_id, :event_type, 'TEST', 'pf010_retention', :created_on, '{}')"
)


def test_pf010_retention_window_by_edition():
    assert retention_days_for_edition("community") == 90
    assert retention_days_for_edition(" Professional ") == 365
    assert retention_days_for_edition("Enterprise") == 2555
    assert set(AUDIT_RETENTION_DAYS_BY_EDITION) == {
        "COMMUNITY",
        "PROFESSIONAL",
        "ENTERPRISE",
    }
    with pytest.raises(ValueError):
        retention_days_for_edition("NOT_AN_EDITION")


def test_pf010_purge_removes_only_expired_events():
    db = SessionLocal()
    tenant_id = uuid4()
    marker = f"PF010R{uuid4().hex[:12]}"
    now = datetime.now(timezone.utc)
    try:
        apply_pf010_ddl(db)
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                _INSERT_SQL,
                {
                    "id": str(uuid4()),
                    "tenant_id": str(tenant_id),
                    "event_type": f"{marker}_EXPIRED",
                    "created_on": now - timedelta(days=400),
                },
            )
            db.execute(
                _INSERT_SQL,
                {
                    "id": str(uuid4()),
                    "tenant_id": str(tenant_id),
                    "event_type": f"{marker}_FRESH",
                    "created_on": now - timedelta(days=1),
                },
            )
            db.commit()

        removed = purge_expired_audit_events(db, retention_days=365, tenant_id=tenant_id)
        db.commit()

        assert removed == 1
        with owner_role():
            db.execute(text("RESET ROLE"))
            remaining = (
                db.execute(
                    text(
                        "SELECT event_type FROM audit.audit_event WHERE event_type LIKE :p "
                        "ORDER BY created_on"
                    ),
                    {"p": marker + "%"},
                )
                .scalars()
                .all()
            )
        assert remaining == [f"{marker}_FRESH"]
    finally:
        db.rollback()
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text("DELETE FROM audit.audit_event WHERE event_type LIKE :p"),
                {"p": marker + "%"},
            )
        db.commit()
        db.close()


def test_pf010_purge_is_tenant_scoped():
    db = SessionLocal()
    tenant_a = uuid4()
    tenant_b = uuid4()
    marker = f"PF010S{uuid4().hex[:12]}"
    expired = datetime.now(timezone.utc) - timedelta(days=400)
    try:
        apply_pf010_ddl(db)
        with owner_role():
            db.execute(text("RESET ROLE"))
            for suffix, tenant in (("A", tenant_a), ("B", tenant_b)):
                db.execute(
                    _INSERT_SQL,
                    {
                        "id": str(uuid4()),
                        "tenant_id": str(tenant),
                        "event_type": f"{marker}_{suffix}",
                        "created_on": expired,
                    },
                )
            db.commit()

        removed = purge_expired_audit_events(db, retention_days=365, tenant_id=tenant_a)
        db.commit()

        assert removed == 1
        with owner_role():
            db.execute(text("RESET ROLE"))
            survivors = (
                db.execute(
                    text("SELECT tenant_id FROM audit.audit_event WHERE event_type LIKE :p"),
                    {"p": marker + "%"},
                )
                .scalars()
                .all()
            )
        assert [str(t) for t in survivors] == [str(tenant_b)]
    finally:
        db.rollback()
        with owner_role():
            db.execute(text("RESET ROLE"))
            db.execute(
                text("DELETE FROM audit.audit_event WHERE event_type LIKE :p"),
                {"p": marker + "%"},
            )
        db.commit()
        db.close()
