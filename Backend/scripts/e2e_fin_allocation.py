"""Live end-to-end check: FIN payment receipt + invoice-stub + (partial) allocation.

Mirrors Backend/tests/test_fin_partial_allocation.py over real HTTP against a
locally running backend (http://localhost:8000). Creates its own customer,
opportunity, quotation (with a line), accepts it, converts to a sales order,
confirms it, records payment stubs, generates an invoice stub, and exercises the
allocation endpoint (0 -> 422, negative -> 422, over-limit -> 409, partial -> 200,
remaining -> 200, over-allocation again -> 409).

Requires: backend running + DEEPSEEK-agnostic (no DeepSeek calls). Credentials are
read from app settings (seed admin), not hard-coded.
"""
import sys
from pathlib import Path
from uuid import uuid4

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.core.config import get_settings  # noqa: E402

BASE = "http://localhost:8000"
API = f"{BASE}/api/v1"
CUSTOMER = f"FIN E2E {uuid4().hex[:6]}"
OPP = f"FIN E2E {uuid4().hex[:6]}"


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

        cust = c.post(f"{API}/crm/customers", headers=h, json={"legal_name": CUSTOMER})
        assert cust.status_code == 201, cust.text
        cust_id = cust.json()["customer_id"]

        opp = c.post(
            f"{API}/crm/opportunities",
            headers=h,
            json={"name": OPP, "stage": "NEGOTIATION", "status": "OPEN"},
        )
        assert opp.status_code == 201, opp.text
        opp_id = opp.json()["opportunity_id"]

        quote = c.post(
            f"{API}/sal/quotations",
            headers=h,
            json={"customer_id": cust_id, "opportunity_id": opp_id},
        )
        assert quote.status_code == 201, quote.text
        qid = quote.json()["quotation_id"]

        line = c.post(
            f"{API}/sal/quotations/{qid}/lines",
            headers=h,
            json={"description": "FIN E2E line", "qty": "1", "unit_price": "1000"},
        )
        assert line.status_code in (200, 201), line.text

        for status in ("SUBMITTED", "APPROVED", "SENT"):
            r = c.patch(f"{API}/sal/quotations/{qid}/status", headers=h, json={"status": status})
            assert r.status_code == 200, r.text

        acc = c.post(
            f"{API}/sal/quotations/{qid}/customer-response",
            headers=h,
            json={"response_type": "ACCEPTED"},
        )
        assert acc.status_code == 200, acc.text

        conv = c.post(f"{API}/sal/quotations/{qid}/convert-to-order", headers=h)
        assert conv.status_code == 201, conv.text
        so_id = conv.json()["sales_order_id"]
        print("sales_order:", conv.json()["so_number"])

        cfm = c.post(f"{API}/sal/sales-orders/{so_id}/confirm", headers=h)
        assert cfm.status_code == 200, cfm.text

        # First payment stub -> receipt R1 (this is auto-allocated on invoice stub)
        stub1 = c.post(f"{API}/sal/sales-orders/{so_id}/record-payment-stub", headers=h)
        assert stub1.status_code == 200, stub1.text

        # Invoice stub auto-allocates R1 fully (deliverable #4)
        inv = c.post(f"{API}/sal/sales-orders/{so_id}/generate-invoice-stub", headers=h)
        assert inv.status_code == 200, inv.text
        invoice_id = inv.json()["invoice"]["invoice_id"]
        assert inv.json()["allocations_created"] >= 1
        print("invoice:", inv.json()["invoice"]["invoice_number"],
              "allocations_created:", inv.json()["allocations_created"])

        # Second, fresh receipt (unallocated) to test partial allocation
        stub2 = c.post(f"{API}/sal/sales-orders/{so_id}/record-payment-stub", headers=h)
        assert stub2.status_code == 200, stub2.text
        rid = stub2.json()["payment_receipt_id"]

        detail = c.get(f"{API}/fin/payment-receipts/{rid}", headers=h)
        assert detail.status_code == 200, detail.text
        total_amount = float(detail.json()["amount"])
        assert total_amount > 0
        print("second receipt:", stub2.json()["receipt_number"], "amount:", total_amount)

        def alloc(amount=None, expect=None):
            body = {"invoice_id": invoice_id}
            if amount is not None:
                body["allocated_amount"] = amount
            resp = c.post(f"{API}/fin/payment-receipts/{rid}/allocate", headers=h, json=body)
            if expect is not None:
                assert resp.status_code == expect, resp.text
            return resp

        alloc(0, expect=422)              # zero -> validation error
        alloc(-10, expect=422)            # negative -> validation error
        alloc(total_amount + 1, expect=409)  # over remaining -> conflict

        half = round(total_amount / 2, 2)
        r1 = alloc(half, expect=200)
        got = float(r1.json()["allocated_amount"])
        assert got == half, f"expected {half}, got {got}"
        print("partial allocation OK:", got)

        r2 = alloc(None, expect=200)      # full remaining
        print("remaining allocation OK:", r2.json()["allocated_amount"])

        alloc(None, expect=409)           # nothing left -> conflict
        print("over-allocation rejected (409) OK")

    print("E2E_FIN_ALLOCATION_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
