CREATE TABLE IF NOT EXISTS sales.quotation_line (
    quotation_line_id UUID PRIMARY KEY,
    tenant_id         UUID NOT NULL REFERENCES core.tenant (tenant_id),
    quotation_id      UUID NOT NULL REFERENCES sales.quotation (quotation_id),
    line_no           INTEGER NOT NULL,
    product_code      VARCHAR(40),
    description       VARCHAR(500) NOT NULL,
    qty               NUMERIC(18, 4) NOT NULL DEFAULT 1,
    unit_price        NUMERIC(18, 2) NOT NULL DEFAULT 0,
    discount_pct      NUMERIC(5, 2) NOT NULL DEFAULT 0,
    tax_code          VARCHAR(20),
    line_total        NUMERIC(18, 2) NOT NULL DEFAULT 0,
    created_on        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    modified_on       TIMESTAMPTZ,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    is_deleted        BOOLEAN NOT NULL DEFAULT FALSE,
    version_no        INTEGER NOT NULL DEFAULT 1,
    CONSTRAINT uk_quotation_line_no UNIQUE (tenant_id, quotation_id, line_no)
);

CREATE INDEX IF NOT EXISTS ix_quotation_line_header
    ON sales.quotation_line (tenant_id, quotation_id);

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA sales TO elu_app;
