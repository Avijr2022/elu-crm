CREATE TABLE IF NOT EXISTS finance.payment_allocation (
    payment_allocation_id   UUID PRIMARY KEY,
    tenant_id               UUID NOT NULL REFERENCES core.tenant (tenant_id),
    payment_receipt_id      UUID NOT NULL REFERENCES finance.payment_receipt (payment_receipt_id),
    invoice_id              UUID NOT NULL REFERENCES finance.invoice (invoice_id),
    allocated_amount        NUMERIC(18, 2) NOT NULL,
    created_on              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active               BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    version_no              INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS ix_payment_alloc_receipt
    ON finance.payment_allocation (tenant_id, payment_receipt_id);

CREATE INDEX IF NOT EXISTS ix_payment_alloc_invoice
    ON finance.payment_allocation (tenant_id, invoice_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON finance.payment_allocation TO elu_app;

DO $alloc_rls$
DECLARE pol text;
BEGIN
  pol := $p$
    current_setting('app.platform_context', true) = 'true'
    OR tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
  $p$;
  ALTER TABLE finance.payment_allocation ENABLE ROW LEVEL SECURITY;
  ALTER TABLE finance.payment_allocation FORCE ROW LEVEL SECURITY;
  DROP POLICY IF EXISTS tenant_isolation ON finance.payment_allocation;
  EXECUTE format(
    'CREATE POLICY tenant_isolation ON finance.payment_allocation FOR ALL USING (%s) WITH CHECK (%s)',
    pol, pol
  );
END
$alloc_rls$;
