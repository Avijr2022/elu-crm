-- 019_audit_pf010_rollback.sql — reverses 019_audit_pf010.sql (idempotent).
-- Drops the PF-010 append-only guard and restores the pre-PF-010 app-role grants.

DROP TRIGGER IF EXISTS trg_audit_event_append_only ON audit.audit_event;
DROP FUNCTION IF EXISTS audit.reject_audit_event_update();

DROP INDEX IF EXISTS audit.idx_audit_event_created_on;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'elu_app') THEN
        GRANT UPDATE, DELETE ON audit.audit_event TO elu_app;
    END IF;
END;
$$;
