"""SAL quotation bootstrap tests."""

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


def test_create_and_list_quotation(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL Cust {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    customer_id = cust.json()["customer_id"]

    create = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": customer_id, "currency_code": "INR"},
    )
    assert create.status_code == 201, create.text
    body = create.json()
    assert body["status"] == "DRAFT"
    assert body["quotation_number"].startswith("QUO-")
    assert body["customer_id"] == customer_id

    listed = client.get("/api/v1/sal/quotations", headers=headers)
    assert listed.status_code == 200, listed.text
    assert listed.json()["total"] >= 1
    assert any(i["quotation_id"] == body["quotation_id"] for i in listed.json()["items"])


def test_get_quotation_with_lines_and_lifecycle(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL Get {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust.json()["customer_id"]},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]

    detail = client.get(f"/api/v1/sal/quotations/{qid}", headers=headers)
    assert detail.status_code == 200, detail.text
    assert detail.json()["lines"] == []

    client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Item", "qty": "1", "unit_price": "100"},
    )

    detail = client.get(f"/api/v1/sal/quotations/{qid}", headers=headers)
    assert len(detail.json()["lines"]) == 1

    submit = client.patch(
        f"/api/v1/sal/quotations/{qid}/status",
        headers=headers,
        json={"status": "SUBMITTED"},
    )
    assert submit.status_code == 200, submit.text
    assert submit.json()["status"] == "SUBMITTED"

    approve = client.patch(
        f"/api/v1/sal/quotations/{qid}/status",
        headers=headers,
        json={"status": "APPROVED"},
    )
    assert approve.status_code == 200, approve.text
    assert approve.json()["status"] == "APPROVED"

    blocked = client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Late line", "qty": "1", "unit_price": "50"},
    )
    assert blocked.status_code == 422, blocked.text


def test_quotation_lines_recalc_totals(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL Line {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust.json()["customer_id"]},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]

    line1 = client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={
            "description": "Widget A",
            "qty": "2",
            "unit_price": "1000",
            "discount_pct": "10",
            "tax_code": "GST18",
        },
    )
    assert line1.status_code == 201, line1.text
    assert line1.json()["line_total"] == "2124.00"

    line2 = client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Service B", "qty": "1", "unit_price": "500", "tax_code": "EXEMPT"},
    )
    assert line2.status_code == 201, line2.text

    listed = client.get("/api/v1/sal/quotations", headers=headers)
    q = next(i for i in listed.json()["items"] if i["quotation_id"] == qid)
    assert q["subtotal"] == "2500.00"
    assert q["discount_total"] == "200.00"
    assert q["tax_total"] == "324.00"
    assert q["grand_total"] == "2624.00"

    upd = client.put(
        f"/api/v1/sal/quotations/{qid}/lines/{line1.json()['quotation_line_id']}",
        headers=headers,
        json={"qty": "1"},
    )
    assert upd.status_code == 200, upd.text

    listed = client.get("/api/v1/sal/quotations", headers=headers)
    q = next(i for i in listed.json()["items"] if i["quotation_id"] == qid)
    assert q["subtotal"] == "1500.00"
    assert q["grand_total"] == "1562.00"

    del_resp = client.delete(
        f"/api/v1/sal/quotations/{qid}/lines/{line2.json()['quotation_line_id']}",
        headers=headers,
    )
    assert del_resp.status_code == 204, del_resp.text

    listed = client.get("/api/v1/sal/quotations", headers=headers)
    q = next(i for i in listed.json()["items"] if i["quotation_id"] == qid)
    assert q["subtotal"] == "1000.00"
    assert q["grand_total"] == "1062.00"


def _quote_to_sent(client, headers, customer_id):
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": customer_id},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]
    client.post(
        f"/api/v1/sal/quotations/{qid}/lines",
        headers=headers,
        json={"description": "Item", "qty": "1", "unit_price": "100"},
    )
    for status in ("SUBMITTED", "APPROVED", "SENT"):
        r = client.patch(
            f"/api/v1/sal/quotations/{qid}/status",
            headers=headers,
            json={"status": status},
        )
        assert r.status_code == 200, r.text
    return qid


def test_quotation_status_history_and_customer_response(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL Hist {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    qid = _quote_to_sent(client, headers, cust.json()["customer_id"])

    hist = client.get(f"/api/v1/sal/quotations/{qid}/history", headers=headers)
    assert hist.status_code == 200, hist.text
    assert len(hist.json()) >= 3

    accept = client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED", "comment": "Customer confirmed"},
    )
    assert accept.status_code == 200, accept.text
    assert accept.json()["status"] == "ACCEPTED"


def test_quotation_pdf_export(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL PDF {uuid.uuid4().hex[:6]}"},
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
    assert export.headers["content-type"] == "application/pdf"
    assert export.content.startswith(b"%PDF")
    assert b"Powered by E-LinkUp CRM" in export.content
    assert b"/DCTDecode" in export.content or b"/FlateDecode" in export.content


def test_quotation_detail_includes_linked_sales_order(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL Link {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    qid = _quote_to_sent(client, headers, cust.json()["customer_id"])
    client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    convert = client.post(f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=headers)
    assert convert.status_code == 201, convert.text
    so_id = convert.json()["sales_order_id"]
    so_number = convert.json()["so_number"]

    detail = client.get(f"/api/v1/sal/quotations/{qid}", headers=headers)
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert body["sales_order_id"] == so_id
    assert body["so_number"] == so_number


def test_quotation_list_includes_linked_sales_order(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL List {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    qid = _quote_to_sent(client, headers, cust.json()["customer_id"])
    client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    convert = client.post(f"/api/v1/sal/quotations/{qid}/convert-to-order", headers=headers)
    assert convert.status_code == 201, convert.text

    listed = client.get("/api/v1/sal/quotations", headers=headers)
    assert listed.status_code == 200, listed.text
    row = next(i for i in listed.json()["items"] if i["quotation_id"] == qid)
    assert row["sales_order_id"] == convert.json()["sales_order_id"]
    assert row["so_number"] == convert.json()["so_number"]


def test_quotation_convert_to_sales_order(client: TestClient, admin_token: str):
    headers = {"Authorization": f"Bearer {admin_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=headers,
        json={"legal_name": f"SAL SO {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    qid = _quote_to_sent(client, headers, cust.json()["customer_id"])
    accept = client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    assert accept.status_code == 200, accept.text

    convert = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order",
        headers=headers,
    )
    assert convert.status_code == 201, convert.text
    body = convert.json()
    assert body["quotation_id"] == qid
    assert body["so_number"].startswith("SO-")
    assert body["status"] == "DRAFT"

    again = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order",
        headers=headers,
    )
    assert again.status_code == 201, again.text
    assert again.json()["sales_order_id"] == body["sales_order_id"]

    draft = client.post(
        "/api/v1/sal/quotations",
        headers=headers,
        json={"customer_id": cust.json()["customer_id"]},
    )
    assert draft.status_code == 201, draft.text
    blocked = client.post(
        f"/api/v1/sal/quotations/{draft.json()['quotation_id']}/convert-to-order",
        headers=headers,
    )
    assert blocked.status_code == 422, blocked.text
