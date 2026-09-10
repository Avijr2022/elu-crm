"""FIN payment receipt and invoice stub tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User

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


def _so_with_payment_stub(client: TestClient, headers: dict) -> str:
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"FIN {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
    )
    assert opp.status_code == 201, opp.text
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"FIN Cust {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust.json()["customer_id"], "opportunity_id": opp.json()["opportunity_id"]},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]
    line = client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "FIN line", "qty": "1", "unit_price": "1000"},
    )
    assert line.status_code in (200, 201), line.text
    for status in ("SUBMITTED", "APPROVED", "SENT"):
        r = client.patch(
            f"/api/v1/sal/quotations/{qid}/status",
            headers=headers,
            json={"status": status},
        )
        assert r.status_code == 200, r.text
    resp_cust = client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    assert resp_cust.status_code == 200, resp_cust.text
    convert = client.post(f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=headers)
    assert convert.status_code == 201, convert.text
    so_id = convert.json()["sales_order_id"]
    client.post(f"/api/v1/sal/sales-orders/{so_id}/confirm", headers=headers)
    stub = client.post(f"/api/v1/sal/sales-orders/{so_id}/record-payment-stub", headers=headers)
    assert stub.status_code == 200, stub.text
    return so_id


def test_payment_receipt_list_and_invoice_stub(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    so_id = _so_with_payment_stub(client, headers)

    receipts = client.get("/api/v1/fin/payment-receipts", headers=headers)
    assert receipts.status_code == 200, receipts.text
    items = receipts.json()["items"]
    assert any(r["sales_order_id"] == so_id for r in items)

    rid = next(r["payment_receipt_id"] for r in items if r["sales_order_id"] == so_id)
    detail = client.get(f"/api/v1/fin/payment-receipts/{rid}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["so_number"] is not None

    invoice = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/generate-invoice-stub",
        headers=headers,
    )
    assert invoice.status_code == 200, invoice.text
    assert invoice.json()["invoice"]["invoice_number"].startswith("INV-")
    assert invoice.json()["allocations_created"] >= 1

    detail_after = client.get(f"/api/v1/fin/payment-receipts/{rid}", headers=headers)
    assert detail_after.status_code == 200, detail_after.text
    assert len(detail_after.json()["allocations"]) >= 1
