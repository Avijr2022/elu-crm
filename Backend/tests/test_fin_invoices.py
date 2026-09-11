"""FIN v4.13 — invoice list / detail / issue workflow tests."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User
from tests.test_fin_payment_receipts import _so_with_payment_stub


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    from tests.conftest import platform_session

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


def _create_invoice(client: TestClient, headers: dict) -> dict:
    """Confirmed SO (+receipt) -> invoice stub. Returns the invoice payload."""
    so_id = _so_with_payment_stub(client, headers)
    resp = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/generate-invoice-stub", headers=headers
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["invoice"]


def test_invoice_list_detail_and_issue_workflow(
    client: TestClient, admin_token: str
) -> None:
    headers = {"Authorization": f"Bearer {admin_token}"}
    invoice = _create_invoice(client, headers)
    invoice_id = invoice["invoice_id"]
    assert invoice["status"] == "DRAFT"

    # --- list ------------------------------------------------------------------
    listing = client.get(
        "/api/v1/fin/invoices", headers=headers, params={"page": 1, "page_size": 50}
    )
    assert listing.status_code == 200, listing.text
    body = listing.json()
    assert body["page"] == 1 and body["page_size"] == 50
    assert body["total"] >= 1
    row = next(item for item in body["items"] if item["invoice_id"] == invoice_id)
    assert row["invoice_number"] == invoice["invoice_number"]
    assert row["status"] == "DRAFT"
    assert row["customer_name"], "customer_name should be joined from crm.customer"
    assert row["so_number"], "so_number should be joined from sales.sales_order"
    # Allocated total / balance must be consistent with the grand total.
    assert float(row["allocated_total"]) >= 0
    assert float(row["balance_due"]) == pytest.approx(
        float(row["grand_total"]) - float(row["allocated_total"])
    )

    # status filter excludes DRAFT when asking for ISSUED
    issued_only = client.get(
        "/api/v1/fin/invoices", headers=headers, params={"status": "ISSUED"}
    )
    assert issued_only.status_code == 200, issued_only.text
    assert all(item["status"] == "ISSUED" for item in issued_only.json()["items"])

    # --- detail ----------------------------------------------------------------
    detail = client.get(f"/api/v1/fin/invoices/{invoice_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    detail_body = detail.json()
    assert detail_body["invoice_id"] == invoice_id
    assert detail_body["customer_name"]
    allocations = detail_body["allocations"]
    assert isinstance(allocations, list)
    # The SO helper records a receipt that the stub auto-allocates.
    assert allocations, "invoice detail should expose its payment allocations"
    assert allocations[0]["receipt_number"], "allocation should carry the receipt number"
    allocated_sum = sum(float(a["allocated_amount"]) for a in allocations)
    assert float(detail_body["allocated_total"]) == pytest.approx(allocated_sum)

    # unknown invoice -> 404
    missing = client.get(f"/api/v1/fin/invoices/{uuid.uuid4()}", headers=headers)
    assert missing.status_code == 404, missing.text

    # --- issue (DRAFT -> ISSUED) ----------------------------------------------
    issued = client.post(f"/api/v1/fin/invoices/{invoice_id}/issue", headers=headers)
    assert issued.status_code == 200, issued.text
    issued_body = issued.json()
    assert issued_body["invoice"]["status"] == "ISSUED"
    assert issued_body["invoice"]["issued_on"] is not None
    assert invoice["invoice_number"] in issued_body["message"]

    # issuing twice -> 409
    again = client.post(f"/api/v1/fin/invoices/{invoice_id}/issue", headers=headers)
    assert again.status_code == 409, again.text

    # detail reflects the new status
    after = client.get(f"/api/v1/fin/invoices/{invoice_id}", headers=headers)
    assert after.status_code == 200, after.text
    assert after.json()["status"] == "ISSUED"

    # issuing an unknown invoice -> 404
    unknown = client.post(f"/api/v1/fin/invoices/{uuid.uuid4()}/issue", headers=headers)
    assert unknown.status_code == 404, unknown.text
