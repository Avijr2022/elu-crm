"""Live P3 v1.0 UAT: Lead -> Payment with invoice allocation."""

import sys
from pathlib import Path
from uuid import uuid4

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import get_settings

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"


def main() -> int:
    settings = get_settings()

    with httpx.Client(base_url=BASE, timeout=60) as c:
        login = c.post(
            f"{API}/auth/login",
            json={
                "email": settings.seed_admin_email,
                "password": settings.seed_admin_password,
                "tenant_code": "EIIP001",
            },
        )
        assert login.status_code == 200, login.text
        h = {"Authorization": f"Bearer {login.json()['access_token']}"}

        suffix = uuid4().hex[:8]

        lead = c.post(
            f"{API}/crm/leads",
            headers=h,
            json={
                "full_name": f"P3 UAT {suffix}",
                "company_name": f"P3 UAT {suffix}",
                "email": f"p3-{suffix}@example.com",
                "estimated_value": 1000,
            },
        )
        assert lead.status_code == 201, lead.text
        lead_id = lead.json()["lead_id"]
        print("lead:", lead_id)

        qualify = c.post(
            f"{API}/crm/leads/{lead_id}/qualify",
            headers=h,
        )
        assert qualify.status_code == 200, qualify.text
        assert qualify.json()["status"] == "QUALIFIED"

        convert = c.post(
            f"{API}/crm/leads/{lead_id}/convert",
            headers=h,
        )
        assert convert.status_code == 201, convert.text
        assert convert.json()["convert_type"] == "OPPORTUNITY"
        opp_id = convert.json()["opportunity"]["opportunity_id"]
        print("opportunity:", opp_id)

        close = c.patch(
            f"{API}/crm/opportunities/{opp_id}",
            headers=h,
            json={"status": "CLOSED_WON"},
        )
        assert close.status_code == 200, close.text
        customer_id = close.json()["customer_id"]
        assert customer_id is not None
        print("customer:", customer_id)

        quote = c.post(
            f"{API}/sal/quotations",
            headers=h,
            json={"opportunity_id": opp_id},
        )
        assert quote.status_code == 201, quote.text
        quotation_id = quote.json()["quotation_id"]

        line = c.post(
            f"{API}/sal/quotations/{quotation_id}/lines",
            headers=h,
            json={
                "description": "P3 UAT line",
                "qty": "1",
                "unit_price": "1000",
            },
        )
        assert line.status_code in (200, 201), line.text

        for status in ("SUBMITTED", "APPROVED", "SENT"):
            r = c.patch(
                f"{API}/sal/quotations/{quotation_id}/status",
                headers=h,
                json={"status": status},
            )
            assert r.status_code == 200, r.text

        accepted = c.post(
            f"{API}/sal/quotations/{quotation_id}/customer-response",
            headers=h,
            json={"response_type": "ACCEPTED"},
        )
        assert accepted.status_code == 200, accepted.text

        order = c.post(
            f"{API}/sal/quotations/{quotation_id}/convert-to-order",
            headers=h,
        )
        assert order.status_code == 201, order.text
        so_id = order.json()["sales_order_id"]

        confirm = c.post(
            f"{API}/sal/sales-orders/{so_id}/confirm",
            headers=h,
        )
        assert confirm.status_code == 200, confirm.text

        receipt = c.post(
            f"{API}/sal/sales-orders/{so_id}/record-payment-stub",
            headers=h,
        )
        assert receipt.status_code == 200, receipt.text

        invoice = c.post(
            f"{API}/sal/sales-orders/{so_id}/generate-invoice-stub",
            headers=h,
        )
        assert invoice.status_code == 200, invoice.text
        assert invoice.json()["allocations_created"] >= 1

        print("P3_UAT_LEAD_TO_PAYMENT_OK")
        print("invoice:", invoice.json()["invoice"]["invoice_number"])
        print("allocations_created:", invoice.json()["allocations_created"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
