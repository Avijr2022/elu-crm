-- PF-008 CORE rollback — reverses 017_users_pf008.sql (idempotent).
-- Drops core.user_invite and the PF-008 additive columns/constraints/indexes on core.users.
-- NOT applied by the application lifespan; run manually only under an approved rollback.

DROP TABLE IF EXISTS core.user_invite;

DROP INDEX IF EXISTS core.uk_user_invite_active_user;
DROP INDEX IF EXISTS core.idx_user_invite_tenant_user;

ALTER TABLE core.users DROP CONSTRAINT IF EXISTS ck_users_account_status;
ALTER TABLE core.users DROP CONSTRAINT IF EXISTS ck_users_failed_login_count;
ALTER TABLE core.users DROP CONSTRAINT IF EXISTS fk_users_branch;
ALTER TABLE core.users DROP CONSTRAINT IF EXISTS fk_users_department;
ALTER TABLE core.users DROP CONSTRAINT IF EXISTS fk_users_business_unit;

DROP INDEX IF EXISTS core.idx_users_branch;
DROP INDEX IF EXISTS core.idx_users_department;
DROP INDEX IF EXISTS core.idx_users_business_unit;
DROP INDEX IF EXISTS core.idx_users_tenant_status;

ALTER TABLE core.users DROP COLUMN IF EXISTS branch_id;
ALTER TABLE core.users DROP COLUMN IF EXISTS department_id;
ALTER TABLE core.users DROP COLUMN IF EXISTS business_unit_id;
ALTER TABLE core.users DROP COLUMN IF EXISTS failed_login_count;
ALTER TABLE core.users DROP COLUMN IF EXISTS locked_until;
ALTER TABLE core.users DROP COLUMN IF EXISTS invited_at;
ALTER TABLE core.users DROP COLUMN IF EXISTS activated_at;
ALTER TABLE core.users DROP COLUMN IF EXISTS deactivated_at;
ALTER TABLE core.users DROP COLUMN IF EXISTS password_changed_at;
ALTER TABLE core.users DROP COLUMN IF EXISTS reset_token_hash;
ALTER TABLE core.users DROP COLUMN IF EXISTS reset_token_expires_at;
ALTER TABLE core.users DROP COLUMN IF EXISTS sessions_invalid_before;
