"""PF-010 AC-PF-010-02 — audit.audit_event is append-only.

The migration is idempotent and runs on every application startup, so these tests
apply it directly instead of depending on a running app / TestClient lifespan.
Sessions are created inside each test (see Backend/tests/conftest.py) so importing
this module never touches the database.
"""

import pytest
from sqlalchemy import text

from app.db.migrate_pf010 import apply_pf010_ddl
from app.db.rls_context import owner_role
from app.db.session import SessionLocal

_TRIGGER_SQL = text(
    "SELECT count(*) FROM pg_trigger t "
    "JOIN pg_class c ON c.oid = t.tgrelid "
    "JOIN pg_namespace n ON n.oid = c.relnamespace "
    "WHERE n.nspname = 'audit' AND c.relname = 'audit_event' "
    "AND t.tgname = 'trg_audit_event_append_only' AND NOT t.tgisinternal"
)


def _insert_event(db) -> str:
    with owner_role():
        db.execute(text("RESET ROLE"))
        event_id = db.execute(
            text(
                "INSERT INTO audit.audit_event "
                "(id, event_type, event_category, entity_type, payload_json) "
                "VALUES (gen_random_uuid(), 'PF010_TEST', 'TEST', 'pf010_test', '{}') "
                "RETURNING id"
            )
        ).scalar()
        db.commit()
    return str(event_id)


def test_pf010_ddl_is_idempotent_and_installs_trigger():
    db = SessionLocal()
    try:
        apply_pf010_ddl(db)
        apply_pf010_ddl(db)
        assert db.execute(_TRIGGER_SQL).scalar() == 1
    finally:
        db.close()


def test_pf010_direct_update_is_rejected():
    """The BEFORE UPDATE trigger rejects mutation even for the table owner."""
    db = SessionLocal()
    event_id = None
    try:
        apply_pf010_ddl(db)
        event_id = _insert_event(db)
        with pytest.raises(Exception) as excinfo:
            with owner_role():
                db.execute(text("RESET ROLE"))
                db.execute(
                    text(
                        "UPDATE audit.audit_event SET event_type = 'PF010_MUTATED' "
                        "WHERE id = :i"
                    ),
                    {"i": event_id},
                )
        db.rollback()
        assert "append-only" in str(excinfo.value)
        with owner_role():
            db.execute(text("RESET ROLE"))
            stored = db.execute(
                text("SELECT event_type FROM audit.audit_event WHERE id = :i"),
                {"i": event_id},
            ).scalar()
        assert stored == "PF010_TEST"
    finally:
        db.rollback()
        if event_id is not None:
            with owner_role():
                db.execute(text("RESET ROLE"))
                db.execute(
                    text("DELETE FROM audit.audit_event WHERE id = :i"),
                    {"i": event_id},
                )
            db.commit()
        db.close()


def test_pf010_app_role_cannot_update_or_delete():
    db = SessionLocal()
    try:
        apply_pf010_ddl(db)
        role_exists = db.execute(
            text("SELECT count(*) FROM pg_roles WHERE rolname = 'elu_app'")
        ).scalar()
        assert role_exists == 1
        can_update = db.execute(
            text("SELECT has_table_privilege('elu_app', 'audit.audit_event', 'UPDATE')")
        ).scalar()
        can_delete = db.execute(
            text("SELECT has_table_privilege('elu_app', 'audit.audit_event', 'DELETE')")
        ).scalar()
        can_insert = db.execute(
            text("SELECT has_table_privilege('elu_app', 'audit.audit_event', 'INSERT')")
        ).scalar()
        assert (can_update, can_delete) == (False, False)
        assert can_insert is True
    finally:
        db.close()


def test_pf010_owner_delete_remains_available_for_retention():
    """AC-PF-010-03 needs a purge path: DELETE is privilege-controlled, not triggered."""
    db = SessionLocal()
    event_id = _insert_event(db)
    try:
        with owner_role():
            db.execute(text("RESET ROLE"))
            deleted = db.execute(
                text("DELETE FROM audit.audit_event WHERE id = :i"),
                {"i": event_id},
            ).rowcount
            db.commit()
        assert deleted == 1
    finally:
        db.close()
