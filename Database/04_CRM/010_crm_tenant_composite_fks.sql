-- 010 - Tenant-safe composite foreign keys for the CRM schema
-- =====================================================================
-- The original CRM DDL used single-column foreign keys
-- (customer_id -> crm.customer.customer_id). Such an FK proves only that the
-- referenced id exists *somewhere* in the parent table; it does not prove that
-- the parent row belongs to the same tenant as the child row. A child row could
-- therefore link tenant A's record to tenant B's parent, and row-level security
-- on the parent does not stop an FK lookup (the check runs as the table owner).
--
-- This migration replaces those keys with tenant-aware composite foreign keys
-- (tenant_id, <id>) and adds the unique keys the referenced side requires.
--
-- Deliberate properties:
--   * Idempotent      - each object is created only when an equivalent one is
--                       absent (matched on the referenced column set, not on a
--                       hard-coded name), so re-running is a no-op.
--   * Additive        - no row is deleted, updated or rewritten; no column is
--                       added or dropped; no index is removed.
--   * Transactional   - plain DDL only: no CONCURRENTLY, no COMMIT inside the
--                       script. The caller (app.db.migrate_crm) owns the
--                       transaction and commits once at the end.
--   * RLS untouched   - no policy is disabled, dropped or created here.
--   * Failures loud   - no EXCEPTION handler. If an existing cross-tenant row
--                       violates a new key, ALTER TABLE raises and the whole
--                       migration rolls back rather than leaving a partial
--                       constraint set.
--   * ON DELETE CASCADE on customer_tax_registration.customer_id is preserved.
--   * opportunity.customer_id / opportunity.source_lead_id stay nullable. The
--     composite keys use the default MATCH SIMPLE semantics, so a row whose key
--     contains any NULL is simply not checked - "no customer yet" and
--     "no source lead" remain valid states.
--
-- Note: crm.customer already carries uq_crm_customer_tenant_customer_id
-- (Database/04_CRM/009_crm_customer_status_history.sql), which is the unique key
-- the composite foreign keys point at. Only crm.lead and crm.activity are missing
-- their (tenant_id, id) unique keys today.

-- ---------------------------------------------------------------------------
-- 1. Referenced-side unique keys
-- ---------------------------------------------------------------------------
DO $crm_fk_unique$
DECLARE
    spec record;
BEGIN
    FOR spec IN
        SELECT *
        FROM (VALUES
            ('lead',     'lead_id',     'uq_crm_lead_tenant_lead_id'),
            ('activity', 'activity_id', 'uq_crm_activity_tenant_activity_id')
        ) AS t(table_name, key_column, constraint_name)
    LOOP
        -- An equivalent unique/primary key already covering (tenant_id, key_column)
        -- makes the constraint unnecessary, whatever its name happens to be.
        IF NOT EXISTS (
            SELECT 1
            FROM pg_constraint c
            CROSS JOIN LATERAL (
                SELECT array_agg(a.attname::text ORDER BY a.attname) AS cols
                FROM unnest(c.conkey) AS k(attnum)
                JOIN pg_attribute a
                  ON a.attrelid = c.conrelid AND a.attnum = k.attnum
            ) ck
            WHERE c.contype IN ('u', 'p')
              AND c.conrelid = format('crm.%I', spec.table_name)::regclass
              AND ck.cols = ARRAY[spec.key_column, 'tenant_id']
        ) THEN
            EXECUTE format(
                'ALTER TABLE crm.%I ADD CONSTRAINT %I UNIQUE (tenant_id, %I)',
                spec.table_name, spec.constraint_name, spec.key_column
            );
        END IF;
    END LOOP;
END
$crm_fk_unique$;

-- ---------------------------------------------------------------------------
-- 2. Composite foreign keys (single-column keys are dropped first)
-- ---------------------------------------------------------------------------
DO $crm_fk_composite$
DECLARE
    spec        record;
    stale_fk    text;
BEGIN
    FOR spec IN
        SELECT *
        FROM (VALUES
            ('customer_address',          'customer_id',    'customer', 'customer_id', false, 'fk_crm_customer_address_tenant_customer'),
            ('customer_contact',          'customer_id',    'customer', 'customer_id', false, 'fk_crm_customer_contact_tenant_customer'),
            ('customer_tax_registration', 'customer_id',    'customer', 'customer_id', true,  'fk_crm_customer_tax_registration_tenant_customer'),
            ('opportunity',               'customer_id',    'customer', 'customer_id', false, 'fk_crm_opportunity_tenant_customer'),
            ('opportunity',               'source_lead_id', 'lead',     'lead_id',     false, 'fk_crm_opportunity_tenant_source_lead'),
            ('activity_link',             'activity_id',    'activity', 'activity_id', false, 'fk_crm_activity_link_tenant_activity')
        ) AS t(child_table, child_column, parent_table, parent_column, cascade_delete, constraint_name)
    LOOP
        -- Already tenant-aware? Match the referenced column sets rather than the
        -- constraint name so a differently-named equivalent also counts.
        IF EXISTS (
            SELECT 1
            FROM pg_constraint c
            CROSS JOIN LATERAL (
                SELECT array_agg(a.attname::text ORDER BY a.attname) AS cols
                FROM unnest(c.conkey) AS k(attnum)
                JOIN pg_attribute a
                  ON a.attrelid = c.conrelid AND a.attnum = k.attnum
            ) ck
            CROSS JOIN LATERAL (
                SELECT array_agg(a.attname::text ORDER BY a.attname) AS cols
                FROM unnest(c.confkey) AS k(attnum)
                JOIN pg_attribute a
                  ON a.attrelid = c.confrelid AND a.attnum = k.attnum
            ) pk
            WHERE c.contype = 'f'
              AND c.conrelid = format('crm.%I', spec.child_table)::regclass
              AND c.confrelid = format('crm.%I', spec.parent_table)::regclass
              AND ck.cols = ARRAY[spec.child_column, 'tenant_id']
              AND pk.cols = ARRAY[spec.parent_column, 'tenant_id']
        ) THEN
            CONTINUE;
        END IF;

        -- Drop the legacy single-column key(s) for this relationship. The drop is
        -- narrowed to foreign keys on the exact column that reference the exact
        -- parent table, so unrelated constraints (core.tenant, core.users) and
        -- other relationships are never touched.
        FOR stale_fk IN
            SELECT c.conname
            FROM pg_constraint c
            CROSS JOIN LATERAL (
                SELECT array_agg(a.attname::text ORDER BY a.attname) AS cols
                FROM unnest(c.conkey) AS k(attnum)
                JOIN pg_attribute a
                  ON a.attrelid = c.conrelid AND a.attnum = k.attnum
            ) ck
            WHERE c.contype = 'f'
              AND c.conrelid = format('crm.%I', spec.child_table)::regclass
              AND c.confrelid = format('crm.%I', spec.parent_table)::regclass
              AND ck.cols = ARRAY[spec.child_column]
        LOOP
            EXECUTE format(
                'ALTER TABLE crm.%I DROP CONSTRAINT %I',
                spec.child_table, stale_fk
            );
        END LOOP;

        EXECUTE format(
            'ALTER TABLE crm.%I ADD CONSTRAINT %I '
            'FOREIGN KEY (tenant_id, %I) '
            'REFERENCES crm.%I (tenant_id, %I)%s',
            spec.child_table,
            spec.constraint_name,
            spec.child_column,
            spec.parent_table,
            spec.parent_column,
            CASE WHEN spec.cascade_delete THEN ' ON DELETE CASCADE' ELSE '' END
        );
    END LOOP;
END
$crm_fk_composite$;
