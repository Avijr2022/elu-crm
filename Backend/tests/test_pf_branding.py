"""PF tenant branding API tests."""

import base64
import binascii
import struct
import zlib

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


from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
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


def _png_data_url(width: int, height: int) -> str:
    """Build a valid 8-bit RGB PNG (zlib level 0) larger than 2 KB base64."""
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # filter type 0
        for x in range(width):
            raw.extend(((x * 7) % 256, (y * 11) % 256, ((x + y) * 13) % 256))

    def chunk(tag: bytes, payload: bytes) -> bytes:
        crc = binascii.crc32(tag + payload) & 0xFFFFFFFF
        return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)

    png = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(bytes(raw), 0))
        + chunk(b"IEND", b"")
    )
    return "data:image/png;base64," + base64.b64encode(png).decode()


def test_upload_large_logo_round_trips(client: TestClient, admin_token: str):
    """Regression: logo_url must store full base64 data URLs (>2 KB).

    The column was VARCHAR(2048), so any realistic logo overflowed and the
    upload returned HTTP 500. The 1x1 test image above masked it.
    """
    headers = {"Authorization": f"Bearer {admin_token}"}
    before = client.get("/api/v1/tenant/branding", headers=headers)
    assert before.status_code == 200, before.text
    prior_logo = before.json().get("logo_url")

    data_url = _png_data_url(48, 48)  # valid PNG, ~9 KB base64
    assert len(data_url) > 2048
    assert data_url != _PNG_1X1

    try:
        upload = client.put(
            "/api/v1/tenant/branding/logo",
            headers=headers,
            json={"logo_data_url": data_url},
        )
        assert upload.status_code == 200, upload.text
        stored = upload.json()["logo_url"]
        assert stored == data_url
        assert len(stored) > 2048

        # Persisted: a subsequent GET returns the full logo.
        fetched = client.get("/api/v1/tenant/branding", headers=headers)
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["logo_url"] == data_url
    finally:
        # Branding is shared tenant state; other suites export PDFs with it.
        client.put(
            "/api/v1/tenant/branding/logo",
            headers=headers,
            json={"logo_data_url": prior_logo or _PNG_1X1},
        )
