-- 019_audit_pf010.sql — PF-010 Audit & Compliance CORE DDL (idempotent).
--
-- AC-PF-010-02: audit.audit_event is append-only. A BEFORE UPDATE trigger rejects
--   every mutation attempt (including from the owner role). DELETE is deliberately
--   NOT trigger-blocked: AC-PF-010-03 requires a retention purge. Instead the app
--   role loses UPDATE/DELETE at the privilege level, so only the owner role may
--   purge (the callable purge service in Backend/app/services/pf/audit_service.py
--   runs under owner_role()).
-- AC-PF-010-03: the purge filters on created_on, so index it.
--
-- Applied by Backend/app/db/migrate_pf010.py, after 012_rls_pf003a.sql (which
-- creates role elu_app).

CREATE OR REPLACE FUNCTION audit.reject_audit_event_update()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    RAISE EXCEPTION 'audit.audit_event is append-only (AC-PF-010-02): UPDATE not permitted'
        USING ERRCODE = 'restrict_violation';
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_event_append_only ON audit.audit_event;
CREATE TRIGGER trg_audit_event_append_only
    BEFORE UPDATE ON audit.audit_event
    FOR EACH ROW
    EXECUTE FUNCTION audit.reject_audit_event_update();

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'elu_app') THEN
        REVOKE UPDATE, DELETE ON audit.audit_event FROM elu_app;
    END IF;
END;
$$;

CREATE INDEX IF NOT EXISTS idx_audit_event_created_on
    ON audit.audit_event(created_on);
