"""SAL sales-order API tests."""

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


def test_sales_order_list_detail_lines_and_confirm_links_work_order(
    client: TestClient, admin_token: str
):
    headers = {"Authorization": f"Bearer {admin_token}"}
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"SO PRJ {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
    )
    assert opp.status_code == 201, opp.text
    opp_id = opp.json()["opportunity_id"]
    won = client.patch(
        f"/api/v1/crm/opportunities/{opp_id}",
        headers=headers,
        json={"status": "CLOSED_WON"},
    )
    assert won.status_code == 200, won.text
    handoff = client.post(f"/api/v1/prj/handoffs/from-opportunity/{opp_id}", headers=headers)
    assert handoff.status_code == 201, handoff.text
    wo_id = handoff.json()["work_order_id"]

    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": None, "opportunity_id": opp_id},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]
    client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Delivery", "qty": "1", "unit_price": "1000"},
    )
    for status in ("SUBMITTED", "APPROVED", "SENT"):
        r = client.patch(
            f"/api/v1/sal/quotations/{qid}/status",
            headers=headers,
            json={"status": status},
        )
        assert r.status_code == 200, r.text
    client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    convert = client.post(f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=headers)
    assert convert.status_code == 201, convert.text
    so_id = convert.json()["sales_order_id"]

    listed = client.get("/api/v1/sal/sales-orders", headers=headers)
    assert listed.status_code == 200, listed.text
    assert any(i["sales_order_id"] == so_id for i in listed.json()["items"])

    detail = client.get(f"/api/v1/sal/sales-orders/{so_id}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert len(detail.json()["lines"]) == 1

    confirm = client.post(f"/api/v1/sal/sales-orders/{so_id}/confirm", headers=headers)
    assert confirm.status_code == 200, confirm.text
    assert confirm.json()["status"] == "CONFIRMED"
    assert confirm.json()["work_orders_linked"] >= 1

    wo = client.get(f"/api/v1/prj/work-orders/{wo_id}", headers=headers)
    assert wo.status_code == 200, wo.text
    assert wo.json()["sales_order_id"] == so_id
    assert wo.json()["so_number"] == convert.json()["so_number"]

    wo_list = client.get("/api/v1/prj/work-orders", headers=headers)
    assert wo_list.status_code == 200, wo_list.text
    linked = next(i for i in wo_list.json()["items"] if i["work_order_id"] == wo_id)
    assert linked["so_number"] == convert.json()["so_number"]

    so_detail = client.get(f"/api/v1/sal/sales-orders/{so_id}", headers=headers)
    assert so_detail.status_code == 200, so_detail.text
    assert any(w["work_order_id"] == wo_id for w in so_detail.json()["work_orders"])


def test_sales_order_list_filter_and_payment_stub(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    opp = client.post(
        "/api/v1/crm/opportunities",
        headers=headers,
        json={"name": f"SO Filter {uuid.uuid4().hex[:6]}", "stage": "NEGOTIATION", "status": "OPEN"},
    )
    assert opp.status_code == 201, opp.text
    opp_id = opp.json()["opportunity_id"]
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SO Filter Cust {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    cust_id = cust.json()["customer_id"]
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust_id, "opportunity_id": opp_id},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]
    client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Item", "qty": "1", "unit_price": "500"},
    )
    for status in ("SUBMITTED", "APPROVED", "SENT"):
        client.patch(
            f"/api/v1/sal/quotations/{qid}/status",
            headers=headers,
            json={"status": status},
        )
    client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    convert = client.post(f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=headers)
    assert convert.status_code == 201, convert.text
    so_id = convert.json()["sales_order_id"]

    by_opp = client.get(
        "/api/v1/sal/sales-orders",
        headers=headers,
        params={"opportunity_id": opp_id},
    )
    assert by_opp.status_code == 200, by_opp.text
    assert any(i["sales_order_id"] == so_id for i in by_opp.json()["items"])

    by_cust = client.get(
        "/api/v1/sal/sales-orders",
        headers=headers,
        params={"customer_id": cust_id},
    )
    assert by_cust.status_code == 200, by_cust.text
    assert any(i["sales_order_id"] == so_id for i in by_cust.json()["items"])

    confirm = client.post(f"/api/v1/sal/sales-orders/{so_id}/confirm", headers=headers)
    assert confirm.status_code == 200, confirm.text

    stub = client.post(f"/api/v1/sal/sales-orders/{so_id}/record-payment-stub", headers=headers)
    assert stub.status_code == 200, stub.text
    assert stub.json()["payment_status"] == "RECORDED_STUB"
    assert stub.json()["sales_order_id"] == so_id

    so_detail = client.get(f"/api/v1/sal/sales-orders/{so_id}", headers=headers)
    assert so_detail.status_code == 200, so_detail.text
    stubs = so_detail.json()["payment_stubs"]
    assert len(stubs) == 1
    assert stubs[0]["payment_status"] == "RECORDED_STUB"
    assert stubs[0]["amount"] == stub.json()["amount"]
    assert stub.json()["receipt_number"].startswith("PR-")
    assert stubs[0]["receipt_number"] == stub.json()["receipt_number"]
