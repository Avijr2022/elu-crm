"""CRM isolation for the *platform-admin as reader* path (ADR-015 / ADR-016 item 6).

Why this module exists
----------------------
``get_current_user`` re-binds the session with ``app.platform_context=true`` for a
``PLATFORM_ADMIN`` (``Backend/app/core/deps.py:54-58``). That RLS GUC bypasses the
``tenant_isolation`` policy at the database layer, so for a platform admin the only
thing that still prevents a cross-tenant read is the explicit repository filter
(``tenant_id == current.tenant_id``).

Existing coverage does **not** exercise that direction:

* ``tests/isolation/test_crm_tenant_isolation.py`` creates rows as the EIIP001
  admin and reads them as the COMU001 *Sales Executive* (the reader is not a
  platform admin).
* ``tests/test_crm_rls_tenant_isolation.py`` proves the database-level bypass with
  ``platform_session()`` but never goes through the API with a platform-admin token.
* ``tests/isolation/test_tenant_isolation.py::test_tc_pf_iso_04_platform_admin_list``
  covers the PF tenant catalogue, not CRM resources.

These tests close that gap: tenant A is the platform tenant (EIIP001) whose seeded
admin is the ``PLATFORM_ADMIN``; tenant B is a freshly registered tenant. Every
resource id is created *by tenant B's own admin*, then requested with tenant A's
platform-admin token. A regression in any repository filter would surface here.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from tests.conftest import platform_admin_select, platform_session
from tests.isolation.test_tenant_isolation import (
    _login_tenant,
    _provision_tenant_admin,
    _register_and_approve,
    _unique_code,
)

pytestmark = pytest.mark.db_write

TENANT_ADMIN_PASSWORD = "IsoTest!234"


@pytest.fixture(scope="module")
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def platform_admin(client: TestClient) -> dict:
    """Tenant A: the platform tenant (EIIP001) and its seeded PLATFORM_ADMIN."""
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
        assert admin is not None, "seeded platform admin missing"
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
        tenant_a = admin.tenant_id
        role_code = admin.role.role_code

    assert role_code == "PLATFORM_ADMIN", role_code
    token = _login_tenant(
        client, settings.seed_admin_email, settings.seed_admin_password, "EIIP001"
    )
    return {"token": token, "tenant_id": tenant_a, "headers": {"Authorization": f"Bearer {token}"}}


@pytest.fixture(scope="module")
def tenant_b(client: TestClient, platform_admin: dict) -> dict:
    """Tenant B: a fresh tenant whose own admin creates one row per CRM resource."""
    code = _unique_code("pa")  # as_'pa'… ASCII-safe tenant code
    tenant = _register_and_approve(client, platform_admin["headers"], code)
    tenant_b_id = uuid.UUID(tenant["id"])

    email = f"admin-{code}@example.com"
    _provision_tenant_admin(tenant_b_id, email, TENANT_ADMIN_PASSWORD)
    headers_b = {
        "Authorization": f"Bearer {_login_tenant(client, email, TENANT_ADMIN_PASSWORD, code)}"
    }

    suffix = uuid.uuid4().hex[:8]
    lead_name = f"B Secret Lead {suffix}"
    customer_name = f"B Secret Customer {suffix}"
    activity_type_code = f"BONLY{uuid.uuid4().hex[:6].upper()}"

    # --- CRM-001 lead → qualify → convert (creates the opportunity) ---------
    lead = client.post(
        "/api/v1/crm/leads",
        headers=headers_b,
        json={
            "full_name": lead_name,
            "company_name": f"B Corp {suffix}",
            "email": f"b-lead-{suffix}@example.com",
            "estimated_value": 250000,
        },
    )
    assert lead.status_code == 201, lead.text
    lead_id = lead.json()["lead_id"]

    qualify = client.post(f"/api/v1/crm/leads/{lead_id}/qualify", headers=headers_b)
    assert qualify.status_code == 200, qualify.text

    convert = client.post(f"/api/v1/crm/leads/{lead_id}/convert", headers=headers_b)
    assert convert.status_code == 201, convert.text
    opportunity_id = convert.json()["opportunity"]["opportunity_id"]

    # --- CRM-003 customer with the prerequisites for ACTIVE -----------------
    customer = client.post(
        "/api/v1/crm/customers",
        headers=headers_b,
        json={"legal_name": customer_name, "trade_name": f"B Trade {suffix}"},
    )
    assert customer.status_code == 201, customer.text
    customer_id = customer.json()["customer_id"]

    contact = client.post(
        f"/api/v1/crm/customers/{customer_id}/contacts",
        headers=headers_b,
        json={"first_name": "B", "last_name": "Contact", "is_primary": True},
    )
    assert contact.status_code == 201, contact.text

    address = client.post(
        f"/api/v1/crm/customers/{customer_id}/addresses",
        headers=headers_b,
        json={"address_type": "REGISTERED", "address_line1": "1 Tenant B Street"},
    )
    assert address.status_code == 201, address.text

    activate = client.patch(
        f"/api/v1/crm/customers/{customer_id}",
        headers=headers_b,
        json={"status": "ACTIVE"},
    )
    assert activate.status_code == 200, activate.text
    assert activate.json()["status"] == "ACTIVE"

    # --- CRM-004 activity linked to tenant B's opportunity ------------------
    activity = client.post(
        "/api/v1/crm/activities",
        headers=headers_b,
        json={
            "activity_type_code": "NOTE",
            "subject": f"B Secret Activity {suffix}",
            "entity_type": "OPPORTUNITY",
            "entity_id": opportunity_id,
        },
    )
    assert activity.status_code == 201, activity.text

    # --- CRM lookup row that exists only in tenant B ------------------------
    activity_type = client.post(
        "/api/v1/crm/activity-types",
        headers=headers_b,
        json={"code": activity_type_code, "name": "Tenant B Only Type"},
    )
    assert activity_type.status_code == 201, activity_type.text

    stage_code = f"BSTAGE{uuid.uuid4().hex[:6].upper()}"
    stage = client.post(
        "/api/v1/crm/opportunity-stages",
        headers=headers_b,
        json={"code": stage_code, "name": "Tenant B Only Stage"},
    )
    assert stage.status_code == 201, stage.text

    return {
        "tenant_id": tenant_b_id,
        "headers": headers_b,
        "suffix": suffix,
        "lead_id": lead_id,
        "lead_name": lead_name,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "opportunity_id": opportunity_id,
        "activity_type_code": activity_type_code,
        "stage_code": stage_code,
    }


def test_tenant_b_can_read_its_own_records(
    client: TestClient, tenant_b: dict
) -> None:
    """Non-vacuity guard: the ids used below really exist and belong to tenant B."""
    for path in (
        f"/api/v1/crm/leads/{tenant_b['lead_id']}",
        f"/api/v1/crm/opportunities/{tenant_b['opportunity_id']}",
        f"/api/v1/crm/customers/{tenant_b['customer_id']}",
    ):
        own = client.get(path, headers=tenant_b["headers"])
        assert own.status_code == 200, (path, own.text)
        assert own.json()["tenant_id"] == str(tenant_b["tenant_id"]), path


def test_platform_admin_cannot_read_tenant_b_resources_by_id(
    client: TestClient, platform_admin: dict, tenant_b: dict
) -> None:
    """Requirement: tenant B ids are 404 for tenant A's platform-admin token."""
    for path in (
        f"/api/v1/crm/leads/{tenant_b['lead_id']}",
        f"/api/v1/crm/opportunities/{tenant_b['opportunity_id']}",
        f"/api/v1/crm/customers/{tenant_b['customer_id']}",
    ):
        cross = client.get(path, headers=platform_admin["headers"])
        assert cross.status_code == 404, (path, cross.text)
        # A 404 must not leak the row through the error envelope either.
        assert str(tenant_b["tenant_id"]) not in cross.text, path


def test_platform_admin_collections_return_only_its_own_tenant(
    client: TestClient, platform_admin: dict, tenant_b: dict
) -> None:
    """Requirement: list endpoints never expose tenant B rows (search hits none)."""
    checks = (
        ("/api/v1/crm/leads", "lead_id", tenant_b["lead_id"], tenant_b["lead_name"]),
        (
            "/api/v1/crm/customers",
            "customer_id",
            tenant_b["customer_id"],
            tenant_b["customer_name"],
        ),
        (
            "/api/v1/crm/opportunities",
            "opportunity_id",
            tenant_b["opportunity_id"],
            f"B Secret Lead {tenant_b['suffix']}",
        ),
    )
    for path, id_key, record_id, unique_name in checks:
        resp = client.get(
            path,
            headers=platform_admin["headers"],
            params={"search": unique_name, "page_size": 100},
        )
        assert resp.status_code == 200, (path, resp.text)
        body = resp.json()
        assert body["total"] == 0, (path, body["total"])
        assert record_id not in {item[id_key] for item in body["items"]}, path

    # Unfiltered page: every row returned still belongs to tenant A.
    for path in ("/api/v1/crm/leads", "/api/v1/crm/customers"):
        resp = client.get(
            path, headers=platform_admin["headers"], params={"page_size": 100}
        )
        assert resp.status_code == 200, (path, resp.text)
        for item in resp.json()["items"]:
            assert item["tenant_id"] == str(platform_admin["tenant_id"]), (
                path,
                item["tenant_id"],
            )


def test_platform_admin_pipeline_excludes_tenant_b(
    client: TestClient, platform_admin: dict, tenant_b: dict
) -> None:
    """Requirement: the pipeline view is tenant-scoped for the platform admin too."""
    resp = client.get("/api/v1/crm/opportunities/pipeline", headers=platform_admin["headers"])
    assert resp.status_code == 200, resp.text
    returned = {
        item["opportunity_id"]
        for bucket in resp.json()["stages"]
        for item in bucket["items"]
    }
    assert tenant_b["opportunity_id"] not in returned


def test_platform_admin_nested_endpoints_enforce_the_same_boundary(
    client: TestClient, platform_admin: dict, tenant_b: dict
) -> None:
    """Requirement: nested lookups/timelines cannot be used to reach tenant B."""
    nested = client.get(
        f"/api/v1/crm/customers/{tenant_b['customer_id']}/opportunities",
        headers=platform_admin["headers"],
    )
    assert nested.status_code == 404, nested.text

    for entity_type, entity_id in (
        ("OPPORTUNITY", tenant_b["opportunity_id"]),
        ("CUSTOMER", tenant_b["customer_id"]),
        ("LEAD", tenant_b["lead_id"]),
    ):
        timeline = client.get(
            "/api/v1/crm/activities/timeline",
            headers=platform_admin["headers"],
            params={"entity_type": entity_type, "entity_id": entity_id},
        )
        assert timeline.status_code == 200, (entity_type, timeline.text)
        assert timeline.json()["total"] == 0, (entity_type, timeline.json())

    # Same timeline for tenant B's own token is non-empty → the empty result above
    # is tenant scoping, not a broken fixture.
    own_timeline = client.get(
        "/api/v1/crm/activities/timeline",
        headers=tenant_b["headers"],
        params={"entity_type": "OPPORTUNITY", "entity_id": tenant_b["opportunity_id"]},
    )
    assert own_timeline.status_code == 200, own_timeline.text
    assert own_timeline.json()["total"] >= 1, own_timeline.text


def test_platform_admin_lookups_exclude_tenant_b_data(
    client: TestClient, platform_admin: dict, tenant_b: dict
) -> None:
    """Requirement: lookup endpoints return only tenant A lookup rows."""
    types = client.get("/api/v1/crm/activity-types", headers=platform_admin["headers"])
    assert types.status_code == 200, types.text
    codes = {item["code"] for item in types.json()["items"]}
    assert tenant_b["activity_type_code"] not in codes
    for item in types.json()["items"]:
        assert item["tenant_id"] == str(platform_admin["tenant_id"])

    lookups = client.get("/api/v1/crm/lookups", headers=platform_admin["headers"])
    assert lookups.status_code == 200, lookups.text
    body = lookups.json()
    assert tenant_b["activity_type_code"] not in body["activity_types"]
    assert tenant_b["activity_type_code"] not in {
        item["code"] for item in body["activity_type_details"]
    }
    for item in body["activity_type_details"]:
        assert item["tenant_id"] == str(platform_admin["tenant_id"])

    stages = client.get("/api/v1/crm/opportunity-stages", headers=platform_admin["headers"])
    assert stages.status_code == 200, stages.text
    stage_codes = {item["code"] for item in stages.json()["items"]}
    assert tenant_b["stage_code"] not in stage_codes
    assert tenant_b["stage_code"] in {
        item["code"]
        for item in client.get(
            "/api/v1/crm/opportunity-stages", headers=tenant_b["headers"]
        ).json()["items"]
    }
