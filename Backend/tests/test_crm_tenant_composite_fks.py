"""Tenant-safe composite foreign keys in the CRM schema (migration 010).

Covers ``Database/04_CRM/010_crm_tenant_composite_fks.sql``:

* same-tenant relationships are accepted;
* cross-tenant customer, lead and activity references are rejected by the
  database itself (not only by application code);
* nullable opportunity references stay optional;
* ``customer_tax_registration`` still cascades on customer delete;
* the migration is idempotent (re-running it is a no-op).

All row mutations run inside ``platform_session()``, which never commits, so the
temporary tenants and rows are rolled back when the session closes. The module is
marked ``db_write`` because the autouse fixture applies DDL (which commits).
"""

import uuid
from datetime import date

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError

from app.db.migrate_crm import apply_crm_ddl
from app.models.crm import (
    Activity,
    ActivityLink,
    Customer,
    CustomerAddress,
    CustomerContact,
    CustomerTaxRegistration,
    Lead,
    Opportunity,
)
from app.models.pf import Edition, Tenant
from tests.conftest import platform_admin_select, platform_session

pytestmark = pytest.mark.db_write

#: Composite keys this migration must install, as
#: ``child table -> (constraint name, ON DELETE CASCADE?)``.
EXPECTED_FKS = {
    "crm.customer_address": ("fk_crm_customer_address_tenant_customer", False),
    "crm.customer_contact": ("fk_crm_customer_contact_tenant_customer", False),
    "crm.customer_tax_registration": (
        "fk_crm_customer_tax_registration_tenant_customer",
        True,
    ),
    "crm.opportunity": None,  # two composite keys: customer + source lead
    "crm.activity_link": ("fk_crm_activity_link_tenant_activity", False),
}

#: Legacy single-column keys that must no longer exist.
LEGACY_SINGLE_COLUMN_FKS = (
    "customer_address_customer_id_fkey",
    "customer_contact_customer_id_fkey",
    "customer_tax_registration_customer_id_fkey",
    "opportunity_customer_id_fkey",
    "opportunity_source_lead_id_fkey",
    "activity_link_activity_id_fkey",
)


@pytest.fixture(scope="module", autouse=True)
def _apply_migration():
    """Apply the CRM DDL once so the composite keys exist for every test."""
    with platform_session() as db:
        apply_crm_ddl(db)


# --------------------------------------------------------------------- helpers


def _edition_id(db):
    edition = db.scalars(select(Edition).order_by(Edition.code)).first()
    assert edition is not None, "no edition seeded - cannot create a temporary tenant"
    return edition.id


def _tenant(db, edition_id, tag: str) -> Tenant:
    tenant = Tenant(
        tenant_code=f"FK{tag}"[:32],
        tenant_name=f"FK {tag}",
        legal_name=f"FK {tag} Ltd",
        edition_id=edition_id,
        organization_type="Pvt Ltd",
        email=f"fk-{tag.lower()}@example.test",
        mobile="+9190" + str(uuid.uuid4().int)[:8],
        status="ACTIVE",
        activation_date=date.today(),
        is_active=True,
        is_deleted=False,
    )
    db.add(tenant)
    db.flush()
    return tenant


def _tag() -> str:
    return uuid.uuid4().hex[:8].upper()


def _customer(db, tenant: Tenant) -> Customer:
    row = Customer(
        tenant_id=tenant.tenant_id,
        customer_number=f"CUS-{uuid.uuid4().hex[:12]}",
        legal_name=f"Customer {uuid.uuid4().hex[:6]}",
        status="ACTIVE",
    )
    db.add(row)
    db.flush()
    return row


def _lead(db, tenant: Tenant) -> Lead:
    row = Lead(
        tenant_id=tenant.tenant_id,
        lead_number=f"LEAD-{uuid.uuid4().hex[:12]}",
        full_name=f"Lead {uuid.uuid4().hex[:6]}",
        status="NEW",
    )
    db.add(row)
    db.flush()
    return row


def _activity(db, tenant: Tenant, owner_id) -> Activity:
    row = Activity(
        tenant_id=tenant.tenant_id,
        subject=f"Activity {uuid.uuid4().hex[:6]}",
        owner_id=owner_id,
        status="COMPLETED",
    )
    db.add(row)
    db.flush()
    return row


def _owner_id(db):
    user = db.scalars(platform_admin_select()).first()
    assert user is not None, "seeded platform admin missing"
    return user.user_id


def _customer_address(db, tenant: Tenant, customer: Customer) -> CustomerAddress:
    return CustomerAddress(
        tenant_id=tenant.tenant_id,
        customer_id=customer.customer_id,
        address_line1="1 Test Street",
    )


def _customer_contact(db, tenant: Tenant, customer: Customer) -> CustomerContact:
    return CustomerContact(
        tenant_id=tenant.tenant_id,
        customer_id=customer.customer_id,
        first_name="Test",
    )


def _tax_registration(db, tenant: Tenant, customer: Customer) -> CustomerTaxRegistration:
    return CustomerTaxRegistration(
        tenant_id=tenant.tenant_id,
        customer_id=customer.customer_id,
        tax_type="GSTIN",
        tax_number=f"27{uuid.uuid4().hex[:13].upper()}",
    )


def _opportunity(db, tenant: Tenant, **kwargs) -> Opportunity:
    params = {
        "tenant_id": tenant.tenant_id,
        "opportunity_number": f"OPP-{uuid.uuid4().hex[:12]}",
        "name": f"Opportunity {uuid.uuid4().hex[:6]}",
        "stage": "QUALIFICATION",
        "status": "OPEN",
    }
    params.update(kwargs)
    return Opportunity(**params)


def _assert_rejected(db, row) -> None:
    """Adding ``row`` must fail on a tenant-aware foreign key."""
    with pytest.raises(IntegrityError):
        with db.begin_nested():
            db.add(row)
            db.flush()


# ------------------------------------------------------------------ happy path


def test_same_tenant_relationships_are_accepted():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _tenant(db, edition_id, _tag())
        customer = _customer(db, tenant)
        lead = _lead(db, tenant)
        activity = _activity(db, tenant, _owner_id(db))

        db.add(_customer_address(db, tenant, customer))
        db.add(_customer_contact(db, tenant, customer))
        db.add(_tax_registration(db, tenant, customer))
        db.add(
            _opportunity(
                db,
                tenant,
                customer_id=customer.customer_id,
                source_lead_id=lead.lead_id,
            )
        )
        db.add(
            ActivityLink(
                tenant_id=tenant.tenant_id,
                activity_id=activity.activity_id,
                entity_type="CUSTOMER",
                entity_id=customer.customer_id,
            )
        )
        db.flush()  # no IntegrityError -> every composite key matched


# ------------------------------------------------------- cross-tenant refusals


def test_cross_tenant_customer_address_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_customer = _customer(db, tenant_b)

        _assert_rejected(db, _customer_address(db, tenant_a, foreign_customer))


def test_cross_tenant_customer_contact_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_customer = _customer(db, tenant_b)

        _assert_rejected(db, _customer_contact(db, tenant_a, foreign_customer))


def test_cross_tenant_customer_tax_registration_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_customer = _customer(db, tenant_b)

        _assert_rejected(db, _tax_registration(db, tenant_a, foreign_customer))


def test_cross_tenant_opportunity_customer_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_customer = _customer(db, tenant_b)

        _assert_rejected(
            db,
            _opportunity(db, tenant_a, customer_id=foreign_customer.customer_id),
        )


def test_cross_tenant_lead_reference_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_lead = _lead(db, tenant_b)

        _assert_rejected(
            db,
            _opportunity(db, tenant_a, source_lead_id=foreign_lead.lead_id),
        )


def test_cross_tenant_activity_reference_is_rejected():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant_a = _tenant(db, edition_id, "A" + _tag())
        tenant_b = _tenant(db, edition_id, "B" + _tag())
        foreign_activity = _activity(db, tenant_b, _owner_id(db))

        _assert_rejected(
            db,
            ActivityLink(
                tenant_id=tenant_a.tenant_id,
                activity_id=foreign_activity.activity_id,
                entity_type="CUSTOMER",
                entity_id=uuid.uuid4(),
            ),
        )


# -------------------------------------------------------------- nullability


def test_opportunity_nullable_references_are_allowed():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _tenant(db, edition_id, _tag())

        # No customer and no source lead at all.
        db.add(_opportunity(db, tenant))
        db.flush()

        # Customer but no lead, and lead but no customer - MATCH SIMPLE skips the
        # check whenever a key column is NULL.
        customer = _customer(db, tenant)
        lead = _lead(db, tenant)
        db.add(_opportunity(db, tenant, customer_id=customer.customer_id))
        db.add(_opportunity(db, tenant, source_lead_id=lead.lead_id))
        db.flush()


# ------------------------------------------------------------ cascade delete


def test_tax_registration_cascades_on_customer_delete():
    with platform_session() as db:
        edition_id = _edition_id(db)
        tenant = _tenant(db, edition_id, _tag())
        customer = _customer(db, tenant)
        registration = _tax_registration(db, tenant, customer)
        db.add(registration)
        db.flush()

        registration_id = registration.customer_tax_registration_id
        customer_id = customer.customer_id

        db.delete(customer)
        db.flush()

        assert (
            db.scalars(
                select(CustomerTaxRegistration).where(
                    CustomerTaxRegistration.customer_tax_registration_id
                    == registration_id
                )
            ).first()
            is None
        ), "customer_tax_registration must cascade on customer delete"
        assert (
            db.scalars(
                select(Customer).where(Customer.customer_id == customer_id)
            ).first()
            is None
        )


# ------------------------------------------------------- schema / idempotency


def test_migration_installed_the_composite_constraints():
    with platform_session() as db:
        rows = db.execute(
            text(
                """
                SELECT conrelid::regclass::text AS child, conname, confdeltype
                FROM pg_constraint
                WHERE contype = 'f'
                  AND conrelid::regclass::text IN (
                      'crm.customer_address',
                      'crm.customer_contact',
                      'crm.customer_tax_registration',
                      'crm.opportunity',
                      'crm.activity_link'
                  )
                """
            )
        ).all()
        by_name = {row[1]: row for row in rows}

        for child, expected in EXPECTED_FKS.items():
            if expected is None:
                continue
            name, cascades = expected
            assert name in by_name, f"missing composite FK {name} on {child}"
            # 'c' == CASCADE, 'a' == NO ACTION
            assert by_name[name][2] == ("c" if cascades else "a"), (
                f"{name} has ON DELETE {by_name[name][2]}, expected "
                f"{'CASCADE' if cascades else 'NO ACTION'}"
            )

        assert "fk_crm_opportunity_tenant_customer" in by_name
        assert "fk_crm_opportunity_tenant_source_lead" in by_name

        for legacy in LEGACY_SINGLE_COLUMN_FKS:
            assert legacy not in by_name, f"legacy single-column FK {legacy} still exists"

        # core.tenant / core.users references must survive untouched.
        remaining = db.execute(
            text(
                """
                SELECT conrelid::regclass::text AS child, confrelid::regclass::text AS parent
                FROM pg_constraint
                WHERE contype = 'f'
                  AND conrelid::regclass::text IN (
                      'crm.customer_address',
                      'crm.customer_contact',
                      'crm.customer_tax_registration',
                      'crm.opportunity',
                      'crm.activity_link'
                  )
                """
            )
        ).all()
        assert ("crm.customer_address", "core.tenant") in remaining
        assert ("crm.opportunity", "core.tenant") in remaining
        assert ("crm.opportunity", "core.users") in remaining
        assert ("crm.activity_link", "core.tenant") in remaining


def test_migration_is_idempotent():
    with platform_session() as db:
        before = db.execute(
            text(
                """
                SELECT count(*)
                FROM pg_constraint
                WHERE contype = 'f' AND connamespace = 'crm'::regnamespace
                """
            )
        ).scalar_one()

        apply_crm_ddl(db)
        apply_crm_ddl(db)

        after = db.execute(
            text(
                """
                SELECT count(*)
                FROM pg_constraint
                WHERE contype = 'f' AND connamespace = 'crm'::regnamespace
                """
            )
        ).scalar_one()

        assert after == before, "re-running the migration must not add or drop keys"


def test_referenced_unique_keys_exist():
    with platform_session() as db:
        rows = db.execute(
            text(
                """
                SELECT conrelid::regclass::text AS tbl, conname
                FROM pg_constraint
                WHERE contype = 'u'
                  AND conrelid::regclass::text IN ('crm.lead', 'crm.activity')
                """
            )
        ).all()
        names = {row[1] for row in rows}
        assert "uq_crm_lead_tenant_lead_id" in names
        assert "uq_crm_activity_tenant_activity_id" in names
