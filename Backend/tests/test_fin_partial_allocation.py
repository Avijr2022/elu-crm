"""Tests for partial allocation behavior on payment receipts."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.main import app
from app.models.pf import User


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client: TestClient) -> str:
    settings = get_settings()
    from tests.conftest import platform_session

    with platform_session() as db:
        admin = db.scalars(select(User).where(User.email == settings.seed_admin_email.lower())).first()
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


from tests.test_fin_payment_receipts import _so_with_payment_stub as _shared_so_with_stub


def _create_so_with_stub(client: TestClient, headers: dict) -> str:
    # reuse the shared helper from the existing test module
    return _shared_so_with_stub(client, headers)


def test_partial_allocation_flow(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    so_id = _create_so_with_stub(client, headers)

    # Create the invoice first. This auto-allocates the helper's receipt fully,
    # so we record a SECOND receipt (fresh, unallocated) to test partial
    # allocation against a real invoice + remaining balance.
    invoice = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/generate-invoice-stub",
        headers=headers,
    )
    assert invoice.status_code == 200, invoice.text
    invoice_id = invoice.json()["invoice"]["invoice_id"]

    stub2 = client.post(
        f"/api/v1/sal/sales-orders/{so_id}/record-payment-stub",
        headers=headers,
    )
    assert stub2.status_code == 200, stub2.text
    rid = stub2.json()["payment_receipt_id"]

    receipt_detail = client.get(f"/api/v1/fin/payment-receipts/{rid}", headers=headers)
    assert receipt_detail.status_code == 200, receipt_detail.text
    total_amount = float(receipt_detail.json()["amount"])
    assert total_amount > 0

    # Attempt allocate zero -> expect validation error (422)
    resp = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id, "allocated_amount": 0},
    )
    assert resp.status_code == 422

    # Attempt allocate negative -> 422
    resp = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id, "allocated_amount": -10},
    )
    assert resp.status_code == 422

    # Attempt allocate more than remaining -> 409
    resp = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id, "allocated_amount": total_amount + 1},
    )
    assert resp.status_code == 409

    # Valid partial allocation (half)
    half = round(total_amount / 2, 2)
    resp = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id, "allocated_amount": half},
    )
    assert resp.status_code == 200, resp.text
    assert float(resp.json()["allocated_amount"]) == half

    # Detail should now show one allocation of half the amount
    detail_after = client.get(f"/api/v1/fin/payment-receipts/{rid}", headers=headers)
    assert detail_after.status_code == 200, detail_after.text
    allocs = detail_after.json()["allocations"]
    assert len(allocs) == 1
    assert float(allocs[0]["allocated_amount"]) == half

    # Allocate the remaining amount (no amount -> full remaining) should succeed
    resp2 = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id},
    )
    assert resp2.status_code == 200, resp2.text

    # Receipt is now fully allocated; allocating again should conflict (409)
    resp3 = client.post(
        f"/api/v1/fin/payment-receipts/{rid}/allocate",
        headers=headers,
        json={"invoice_id": invoice_id},
    )
    assert resp3.status_code == 409
