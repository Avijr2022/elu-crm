"""SAL quotation tenant isolation (ADR-015)."""

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_pf003a import rls_enabled
from app.main import app
from app.models.pf import User
from tests.conftest import platform_admin_select, platform_session


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _login(client: TestClient, email: str, password: str, tenant_code: str) -> str:
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password, "tenant_code": tenant_code},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


@pytest.fixture(scope="module")
def pro_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(
            platform_admin_select()
        ).first()
        assert admin is not None
        admin.password_hash = hash_password(settings.seed_admin_password)
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        if user:
            user.password_hash = hash_password("Community@12345")
        db.commit()
    return _login(
        client,
        settings.seed_admin_email,
        settings.seed_admin_password,
        "EIIP001",
    )


@pytest.fixture(scope="module")
def community_token(client: TestClient) -> str:
    return _login(
        client,
        "community@euphoriainfotech.com",
        "Community@12345",
        "COMU001",
    )


def test_sal_quotation_rls_enabled():
    with platform_session() as db:
        assert rls_enabled(db, "sales", "quotation")
        assert rls_enabled(db, "sales", "quotation_line")
        assert rls_enabled(db, "sales", "sales_order")
        assert rls_enabled(db, "sales", "sales_order_line")


def _quote_to_accepted(client: TestClient, headers: dict, customer_id: str) -> str:
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
    accept = client.post(
        f"/api/v1/sal/quotations/{qid}/customer-response",
        headers=headers,
        json={"response_type": "ACCEPTED"},
    )
    assert accept.status_code == 200, accept.text
    return qid


def test_sal_sales_order_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=pro_headers,
        json={"legal_name": f"ISO SO {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    qid = _quote_to_accepted(client, pro_headers, cust.json()["customer_id"])
    convert = client.post(
        f"/api/v1/sal/quotations/{qid}/convert-to-order",
        headers=pro_headers,
    )
    assert convert.status_code == 201, convert.text
    so_id = convert.json()["sales_order_id"]

    comm_headers = {"Authorization": f"Bearer {community_token}"}
    blocked = client.get(f"/api/v1/sal/sales-orders/{so_id}", headers=comm_headers)
    assert blocked.status_code in (403, 404), blocked.text


def test_sal_quotation_cross_tenant_isolation(
    client: TestClient, pro_token: str, community_token: str
):
    pro_headers = {"Authorization": f"Bearer {pro_token}"}
    cust = client.post(
        "/api/v1/crm/customers",
        headers=pro_headers,
        json={"legal_name": f"ISO SAL {uuid.uuid4().hex[:6]}"},
    )
    assert cust.status_code == 201, cust.text
    quote = client.post(
        "/api/v1/sal/quotations",
        headers=pro_headers,
        json={"customer_id": cust.json()["customer_id"]},
    )
    assert quote.status_code == 201, quote.text
    qid = quote.json()["quotation_id"]

    comm_headers = {"Authorization": f"Bearer {community_token}"}
    resp = client.get(f"/api/v1/sal/quotations/{qid}", headers=comm_headers)
    assert resp.status_code in (403, 404), resp.text
