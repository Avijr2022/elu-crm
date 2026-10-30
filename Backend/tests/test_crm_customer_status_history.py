from pathlib import Path

from sqlalchemy import ForeignKeyConstraint, UniqueConstraint

from app.db.migrate_crm import _CRM_SCRIPTS
from app.models.crm.entities import Customer, CustomerStatusHistory


def test_customer_has_tenant_scoped_composite_unique_constraint():
    constraints = Customer.__table__.constraints

    assert any(
        isinstance(constraint, UniqueConstraint)
        and constraint.name == "uq_crm_customer_tenant_customer_id"
        and tuple(column.name for column in constraint.columns)
        == ("tenant_id", "customer_id")
        for constraint in constraints
    )


def test_status_history_has_tenant_scoped_composite_customer_fk():
    constraints = CustomerStatusHistory.__table__.constraints

    assert any(
        isinstance(constraint, ForeignKeyConstraint)
        and constraint.name
        == "fk_crm_customer_status_history_tenant_customer"
        and tuple(column.name for column in constraint.columns)
        == ("tenant_id", "customer_id")
        and tuple(element.target_fullname for element in constraint.elements)
        == ("crm.customer.tenant_id", "crm.customer.customer_id")
        for constraint in constraints
    )


def test_status_history_has_required_columns():
    table = CustomerStatusHistory.__table__

    expected = {
        "customer_status_history_id",
        "tenant_id",
        "customer_id",
        "from_status",
        "to_status",
        "reason",
        "actor_id",
        "changed_on",
    }
    assert expected.issubset(table.columns.keys())

    for name in expected - {"customer_status_history_id"}:
        assert table.columns[name].nullable is False, name


def test_status_history_migration_is_registered():
    assert "009_crm_customer_status_history.sql" in _CRM_SCRIPTS
    assert _CRM_SCRIPTS.index("009_crm_customer_status_history.sql") == (
        _CRM_SCRIPTS.index("008_crm_customer_tax_registration.sql") + 1
    )


def test_status_history_migration_defines_composite_constraints():
    migration_path = (
        Path(__file__).resolve().parents[2]
        / "Database"
        / "04_CRM"
        / "009_crm_customer_status_history.sql"
    )
    sql = migration_path.read_text(encoding="utf-8")

    unique_position = sql.index(
        "UNIQUE (tenant_id, customer_id)"
    )
    table_position = sql.index(
        "CREATE TABLE IF NOT EXISTS crm.customer_status_history"
    )
    fk_position = sql.index(
        "FOREIGN KEY (tenant_id, customer_id)"
    )
    reference_position = sql.index(
        "REFERENCES crm.customer (tenant_id, customer_id)"
    )

    assert unique_position < table_position < fk_position < reference_position
    assert "uq_crm_customer_tenant_customer_id" in sql
    assert "fk_crm_customer_status_history_tenant_customer" in sql
    assert "ix_cust_status_hist_tenant_customer" in sql
