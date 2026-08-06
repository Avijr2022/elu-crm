"""PF-003 subscription DDL applicator (idempotent)."""

from sqlalchemy import text
from sqlalchemy.orm import Session


def apply_pf003_ddl(db: Session) -> None:
    stmts = [
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS billing_cycle VARCHAR(20) DEFAULT 'MONTHLY'",
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS seat_count INTEGER DEFAULT 10",
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS trial_end_date DATE",
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS cancellation_reason VARCHAR(500)",
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS created_by UUID",
        "ALTER TABLE core.subscription ADD COLUMN IF NOT EXISTS modified_by UUID",
        "UPDATE core.subscription SET billing_cycle = 'MONTHLY' WHERE billing_cycle IS NULL",
        "UPDATE core.subscription SET seat_count = 10 WHERE seat_count IS NULL OR seat_count < 1",
        "UPDATE core.subscription SET trial_end_date = end_date WHERE subscription_status = 'TRIAL' AND trial_end_date IS NULL",
        "ALTER TABLE core.subscription ALTER COLUMN billing_cycle SET DEFAULT 'MONTHLY'",
        "ALTER TABLE core.subscription ALTER COLUMN seat_count SET DEFAULT 10",
        "ALTER TABLE core.subscription ALTER COLUMN billing_cycle SET NOT NULL",
        "ALTER TABLE core.subscription ALTER COLUMN seat_count SET NOT NULL",
        "ALTER TABLE core.tenant ADD COLUMN IF NOT EXISTS current_subscription_id UUID",
        """
UPDATE core.tenant t
SET current_subscription_id = NULL
WHERE current_subscription_id IS NOT NULL
  AND NOT EXISTS (
    SELECT 1 FROM core.subscription s
    WHERE s.subscription_id = t.current_subscription_id
  )
""",
        """
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_subscription_status') THEN
    ALTER TABLE core.subscription
      ADD CONSTRAINT ck_subscription_status
      CHECK (subscription_status IN (
        'TRIAL','ACTIVE','RENEWAL_PENDING','PAST_DUE','EXPIRED','CANCELLED','SUSPENDED'
      ));
  END IF;
END
$ck$;
""",
        """
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_subscription_billing_cycle') THEN
    ALTER TABLE core.subscription
      ADD CONSTRAINT ck_subscription_billing_cycle
      CHECK (billing_cycle IN ('MONTHLY','ANNUAL','QUARTERLY'));
  END IF;
END
$ck$;
""",
        """
DO $ck$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'ck_subscription_seat_count') THEN
    ALTER TABLE core.subscription
      ADD CONSTRAINT ck_subscription_seat_count
      CHECK (seat_count >= 1);
  END IF;
END
$ck$;
""",
        """
DO $fk$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint WHERE conname = 'fk_tenant_current_subscription'
  ) THEN
    ALTER TABLE core.tenant
      ADD CONSTRAINT fk_tenant_current_subscription
      FOREIGN KEY (current_subscription_id)
      REFERENCES core.subscription(subscription_id)
      ON DELETE SET NULL;
  END IF;
END
$fk$;
""",
        """
WITH ranked AS (
  SELECT subscription_id,
         ROW_NUMBER() OVER (
           PARTITION BY tenant_id ORDER BY created_on DESC
         ) AS rn
  FROM core.subscription
  WHERE is_deleted = false
    AND subscription_status IN ('ACTIVE','TRIAL')
)
UPDATE core.subscription s
SET subscription_status = 'EXPIRED',
    is_active = false
FROM ranked r
WHERE s.subscription_id = r.subscription_id
  AND r.rn > 1
""",
        """
CREATE UNIQUE INDEX IF NOT EXISTS uk_subscription_one_current
  ON core.subscription (tenant_id)
  WHERE is_deleted = false
    AND subscription_status IN ('ACTIVE','TRIAL')
""",
        "CREATE INDEX IF NOT EXISTS idx_subscription_tenant_status ON core.subscription(tenant_id, subscription_status)",
        "CREATE INDEX IF NOT EXISTS idx_subscription_edition_id ON core.subscription(edition_id)",
        """
CREATE TABLE IF NOT EXISTS core.subscription_history (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id),
    subscription_id UUID NOT NULL REFERENCES core.subscription(subscription_id) ON DELETE CASCADE,
    change_type VARCHAR(32) NOT NULL,
    from_status VARCHAR(32),
    to_status VARCHAR(32),
    from_edition_id UUID,
    to_edition_id UUID,
    from_seat_count INTEGER,
    to_seat_count INTEGER,
    reason VARCHAR(500),
    actor_id UUID,
    changed_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
""",
        """
CREATE TABLE IF NOT EXISTS core.subscription_usage (
    id UUID PRIMARY KEY,
    tenant_id UUID NOT NULL REFERENCES core.tenant(tenant_id),
    subscription_id UUID NOT NULL REFERENCES core.subscription(subscription_id) ON DELETE CASCADE,
    metric_code VARCHAR(32) NOT NULL,
    used_value VARCHAR(30) NOT NULL,
    measured_on TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
""",
        "CREATE INDEX IF NOT EXISTS idx_subscription_history_sub ON core.subscription_history(subscription_id)",
        "CREATE INDEX IF NOT EXISTS idx_subscription_usage_sub ON core.subscription_usage(subscription_id)",
        """
UPDATE core.tenant t
SET current_subscription_id = s.subscription_id
FROM (
  SELECT DISTINCT ON (tenant_id) subscription_id, tenant_id
  FROM core.subscription
  WHERE is_deleted = false
    AND subscription_status IN ('ACTIVE','TRIAL')
  ORDER BY tenant_id, created_on DESC
) s
WHERE t.tenant_id = s.tenant_id
  AND t.current_subscription_id IS NULL
""",
    ]
    for stmt in stmts:
        db.execute(text(stmt))
    db.commit()
