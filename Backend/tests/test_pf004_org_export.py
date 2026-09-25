"""PF-004 organization export — authorization, masking and tenant isolation.

Covers the approved corrections HD-02 (export = Tenant Admin + Finance User only)
and HD-03 (GSTIN/PAN masked in the exported representation).
"""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import Organization, Role, User
from tests.conftest import platform_admin_select, platform_session

_EXPORT_URL = "/api/v1/org/organizations/export"
_VALID_GSTIN = "29ABCDE1234F1Z5"
_VALID_PAN = "ABCDE1234F"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _role_token(client: TestClient, role_code: str) -> str:
    """Create an ACTIVE user with the given role in the seed tenant and log in."""
    settings = get_settings()
    password = "Pf004Export!234"
    email = f"pf004-{role_code.lower()}-{uuid.uuid4().hex[:8]}@euphoriainfotech.com"
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        role = db.scalars(
            select(Role).where(
                Role.tenant_id == admin.tenant_id,
                Role.role_code == role_code,
            )
        ).first()
        assert role is not None, f"role {role_code} not seeded for the tenant"
        db.add(
            User(
                tenant_id=admin.tenant_id,
                organization_id=admin.organization_id,
                role_id=role.role_id,
                employee_code=f"P4{uuid.uuid4().hex[:6].upper()}",
                first_name="PF004",
                last_name=role_code.title(),
                display_name=f"PF004 {role_code}",
                email=email,
                password_hash=hash_password(password),
                account_status="ACTIVE",
            )
        )
        db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
            "tenant_code": "EIIP001",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def tenant_admin_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_role_token(client, 'TENANT_ADMIN')}"}


@pytest.fixture(scope="module")
def finance_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_role_token(client, 'FINANCE_USER')}"}


@pytest.fixture(scope="module")
def sales_manager_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_role_token(client, 'SALES_MANAGER')}"}


@pytest.fixture(scope="module")
def project_manager_headers(client: TestClient) -> dict[str, str]:
    return {"Authorization": f"Bearer {_role_token(client, 'PROJECT_MANAGER')}"}


@pytest.fixture(scope="module")
def platform_admin_headers(client: TestClient) -> dict[str, str]:
    """The seeded admin account carries the PLATFORM_ADMIN role."""
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": settings.seed_admin_email,
            "password": settings.seed_admin_password,
            "tenant_code": "EIIP001",
        },
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


# --- HD-02: export authorization matrix -------------------------------------


def test_export_allowed_for_tenant_admin(
    client: TestClient, tenant_admin_headers: dict[str, str]
) -> None:
    resp = client.get(_EXPORT_URL, headers=tenant_admin_headers)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert isinstance(payload, list)
    assert payload, "seed tenant must expose at least the ROOT organization"


def test_export_allowed_for_finance_user(
    client: TestClient, finance_headers: dict[str, str]
) -> None:
    resp = client.get(_EXPORT_URL, headers=finance_headers)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_export_denied_for_sales_manager(
    client: TestClient, sales_manager_headers: dict[str, str]
) -> None:
    resp = client.get(_EXPORT_URL, headers=sales_manager_headers)
    assert resp.status_code == 403, resp.text


def test_export_denied_for_platform_admin(
    client: TestClient, platform_admin_headers: dict[str, str]
) -> None:
    """BFS-PF-004 §12: Platform Admin is read-only and must not export."""
    resp = client.get(_EXPORT_URL, headers=platform_admin_headers)
    assert resp.status_code == 403, resp.text


def test_export_denied_for_project_manager(
    client: TestClient, project_manager_headers: dict[str, str]
) -> None:
    resp = client.get(_EXPORT_URL, headers=project_manager_headers)
    assert resp.status_code == 403, resp.text


# --- HD-03: masking ---------------------------------------------------------


def test_export_masks_gstin_and_pan(
    client: TestClient, tenant_admin_headers: dict[str, str]
) -> None:
    root = client.get("/api/v1/org/organizations/root", headers=tenant_admin_headers)
    assert root.status_code == 200, root.text
    root_id = root.json()["id"]
    prior_gstin = root.json().get("gstin")
    prior_pan = root.json().get("pan")

    set_tax = client.patch(
        f"/api/v1/org/organizations/{root_id}",
        headers=tenant_admin_headers,
        json={
            "gstin": _VALID_GSTIN,
            "pan": _VALID_PAN,
            "version_no": root.json()["version_no"],
        },
    )
    assert set_tax.status_code == 200, set_tax.text
    bumped_version = set_tax.json()["version_no"]
    try:
        # The read surface still returns the real identifiers …
        assert set_tax.json()["gstin"] == _VALID_GSTIN
        assert set_tax.json()["pan"] == _VALID_PAN

        export = client.get(_EXPORT_URL, headers=tenant_admin_headers)
        assert export.status_code == 200, export.text
        row = next(r for r in export.json() if r["id"] == root_id)
        assert row["gstin"] == "***", row
        assert row["pan"] == "***", row

        # … and the stored values are untouched (export masks the representation only).
        with platform_session() as db:
            stored = db.scalars(
                select(Organization).where(
                    Organization.organization_id == uuid.UUID(root_id)
                )
            ).first()
            assert stored is not None
            assert stored.gstin == _VALID_GSTIN
            assert stored.pan == _VALID_PAN
    finally:
        client.patch(
            f"/api/v1/org/organizations/{root_id}",
            headers=tenant_admin_headers,
            json={
                "gstin": prior_gstin,
                "pan": prior_pan,
                "version_no": bumped_version,
            },
        )


# --- Tenant isolation ------------------------------------------------------


def test_export_is_tenant_scoped(
    client: TestClient, tenant_admin_headers: dict[str, str]
) -> None:
    """Export returns exactly the caller tenant's organizations (RLS + tenant filter)."""
    export = client.get(_EXPORT_URL, headers=tenant_admin_headers)
    assert export.status_code == 200, export.text
    exported_ids = {row["id"] for row in export.json()}

    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        own_ids = {
            str(org_id)
            for org_id in db.scalars(
                select(Organization.organization_id).where(
                    Organization.tenant_id == admin.tenant_id,
                    Organization.is_deleted.is_(False),
                )
            ).all()
        }
        foreign_ids = {
            str(org_id)
            for org_id in db.scalars(
                select(Organization.organization_id).where(
                    Organization.tenant_id != admin.tenant_id,
                    Organization.is_deleted.is_(False),
                )
            ).all()
        }

    assert foreign_ids, "test needs a second tenant with organizations to be meaningful"
    assert exported_ids == own_ids
    assert not (exported_ids & foreign_ids)
