"""PF tenant branding API tests."""

import base64

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User

_PNG_1X1 = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)


from tests.conftest import platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            select(User).where(User.email == settings.seed_admin_email.lower())
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
    return resp.json()["access_token"]


def test_upload_png_logo_and_export_pdf(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    upload = client.put(
        "/api/v1/tenant/branding/logo",
        headers=headers,
        json={"logo_data_url": _PNG_1X1},
    )
    assert upload.status_code == 200, upload.text
    assert upload.json()["logo_url"].startswith("data:image/png;base64,")

    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": "Branding PDF Cust"},
    )
    assert cust.status_code == 201, cust.text
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust.json()["customer_id"]},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]
    export = client.get(f"/api/v1/sal/quotations/{qid}/export", headers=headers)
    assert export.status_code == 200, export.text
    assert b"/FlateDecode" in export.content or b"/DCTDecode" in export.content
