"""REQ-CRM-027 / TC-CRM-003-03 â€” customer duplicate-check."""

import uuid
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.migrate_crm import apply_crm_ddl
from app.db.session import SessionLocal
from app.main import app
from app.models.crm import Customer, CustomerTaxRegistration
from app.models.pf import User
from app.repositories.crm.customer_tax_registration_repository import (
    CustomerTaxRegistrationRepository,
)
from tests.conftest import platform_admin_select, platform_session

def _unique_gstin() -> str:
    """Return a valid-format GSTIN not already reserved in the test database."""
    for _ in range(100):
        digits = f"{uuid.uuid4().int % 10_000:04d}"
        candidate = f"27AAAAB{digits}AFZ5"
        with platform_session() as db:
            exists = db.scalars(
                select(CustomerTaxRegistration.customer_tax_registration_id).where(
                    CustomerTaxRegistration.tax_type == "GSTIN",
                    CustomerTaxRegistration.tax_number == candidate,
                    CustomerTaxRegistration.is_deleted.is_(False),
                )
            ).first()
        if exists is None:
            return candidate
    raise RuntimeError("Unable to generate an unused test GSTIN after 100 attempts")


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def pro_token(client: TestClient) -> str:
    settings = get_settings()
    with platform_session() as db:
        admin = db.scalars(platform_admin_select()).first()
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


@pytest.fixture(scope="module")
def community_token(client: TestClient) -> str:
    with platform_session() as db:
        user = db.scalars(
            select(User).where(User.email == "community@euphoriainfotech.com")
        ).first()
        if user:
            user.password_hash = hash_password("Community@12345")
            db.commit()
    resp = client.post(
        "/api/v1/auth/login",
        json={
            "email": "community@euphoriainfotech.com",
            "password": "Community@12345",
            "tenant_code": "COMU001",
        },
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _create_customer(client: TestClient, token: str, **fields) -> dict:
    body = {"legal_name": fields.pop("legal_name", f"Customer {uuid.uuid4().hex[:6]}")}
    body.update(fields)
    resp = client.post("/api/v1/crm/customers", headers=_auth(token), json=body)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_tax_reg(
    tenant_id: UUID,
    customer_id: UUID,
    tax_number: str,
    *,
    is_active: bool = True,
    is_deleted: bool = False,
) -> None:
    with platform_session() as db:
        db.add(
            CustomerTaxRegistration(
                customer_tax_registration_id=uuid.uuid4(),
                tenant_id=tenant_id,
                customer_id=customer_id,
                tax_type="GSTIN",
                tax_number=tax_number.strip().upper().replace(" ", ""),
                is_active=is_active,
                is_deleted=is_deleted,
            )
        )
        db.commit()


def _duplicate_check(client: TestClient, token: str, payload: dict) -> dict:
    resp = client.post(
        "/api/v1/crm/customers/duplicate-check",
        headers=_auth(token),
        json=payload,
    )
    return resp


def test_crm_tax_registration_migration_idempotent() -> None:
    db = SessionLocal()
    try:
        apply_crm_ddl(db)
        apply_crm_ddl(db)
        row = db.execute(
            text(
                "SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='crm' AND table_name='customer_tax_registration'"
            )
        ).first()
        assert row is not None
    finally:
        db.close()


def test_duplicate_check_no_match(client: TestClient, pro_token: str) -> None:
    resp = _duplicate_check(
        client,
        pro_token,
        {
            "legal_name": f"Unique Co {uuid.uuid4().hex[:8]}",
            "tax_type": "GSTIN",
            "tax_number": _unique_gstin(),
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["blocked"] is False
    assert body["matches"] == []


def test_duplicate_gstin_blocks(client: TestClient, pro_token: str) -> None:
    created = _create_customer(client, pro_token, legal_name="Tax Block Co")
    cid = UUID(created["customer_id"])
    with platform_session() as db:
        tenant_id = db.get(Customer, cid).tenant_id
    gstin = _unique_gstin()
    _add_tax_reg(tenant_id, cid, gstin)

    resp = _duplicate_check(
        client,
        pro_token,
        {"tax_type": "GSTIN", "tax_number": gstin, "legal_name": "Other Name"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["blocked"] is True
    assert len(body["matches"]) == 1
    match = body["matches"][0]
    assert match["customer_id"] == str(cid)
    assert match["match_kind"] == "TAX_ID"
    assert match["severity"] == "BLOCK"
    assert match["tax_number_masked"] == f"***{gstin[-4:]}"
    assert gstin not in str(body)


def test_trade_name_match_warns(client: TestClient, pro_token: str) -> None:
    trade = f"TradeWarn {uuid.uuid4().hex[:6]}"
    _create_customer(client, pro_token, legal_name="Legal Only", trade_name=trade)

    resp = _duplicate_check(
        client,
        pro_token,
        {"trade_name": f"  {trade.upper()}  "},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["blocked"] is False
    assert any(m["match_kind"] == "TRADE_NAME" and m["severity"] == "WARNING" for m in body["matches"])


def test_name_normalization_case_and_whitespace(client: TestClient, pro_token: str) -> None:
    legal = f"Acme   Manufacturing {uuid.uuid4().hex[:4]}"
    _create_customer(client, pro_token, legal_name=legal)

    resp = _duplicate_check(
        client,
        pro_token,
        {"legal_name": legal.upper().replace("   ", "  ")},
    )
    assert resp.status_code == 200, resp.text
    assert any(m["match_kind"] == "LEGAL_NAME" for m in resp.json()["matches"])


def test_malformed_gstin_returns_422(client: TestClient, pro_token: str) -> None:
    resp = _duplicate_check(client, pro_token, {"tax_type": "GSTIN", "tax_number": "NOT-A-GSTIN"})
    assert resp.status_code == 422, resp.text


def test_deleted_customer_tax_not_matched(client: TestClient, pro_token: str) -> None:
    created = _create_customer(client, pro_token, legal_name="Deleted Tax Co")
    cid = UUID(created["customer_id"])
    with platform_session() as db:
        row = db.get(Customer, cid)
        tenant_id = row.tenant_id
        row.is_deleted = True
        db.commit()
    gstin = _unique_gstin()
    _add_tax_reg(tenant_id, cid, gstin)

    resp = _duplicate_check(client, pro_token, {"tax_type": "GSTIN", "tax_number": gstin})
    assert resp.status_code == 200, resp.text
    assert resp.json()["blocked"] is False


def test_inactive_tax_registration_not_matched(client: TestClient, pro_token: str) -> None:
    created = _create_customer(client, pro_token, legal_name="Inactive Tax Row")
    cid = UUID(created["customer_id"])
    with platform_session() as db:
        tenant_id = db.get(Customer, cid).tenant_id
    gstin = _unique_gstin()
    _add_tax_reg(tenant_id, cid, gstin, is_active=False)

    resp = _duplicate_check(client, pro_token, {"tax_type": "GSTIN", "tax_number": gstin})
    assert resp.status_code == 200, resp.text
    assert resp.json()["blocked"] is False


def test_cross_tenant_gstin_isolated(
    client: TestClient, pro_token: str, community_token: str
) -> None:
    created = _create_customer(client, pro_token, legal_name="Pro Tenant GSTIN")
    cid = UUID(created["customer_id"])
    with platform_session() as db:
        tenant_id = db.get(Customer, cid).tenant_id
    gstin = _unique_gstin()
    _add_tax_reg(tenant_id, cid, gstin)

    pro_resp = _duplicate_check(client, pro_token, {"tax_type": "GSTIN", "tax_number": gstin})
    assert pro_resp.json()["blocked"] is True

    comm_resp = _duplicate_check(client, community_token, {"tax_type": "GSTIN", "tax_number": gstin})
    assert comm_resp.status_code == 200, comm_resp.text
    assert comm_resp.json()["blocked"] is False
    assert comm_resp.json()["matches"] == []


# ---------------------------------------------------------------------------
# BR-CRM-045: only GSTIN is supported; another type must never be read as GSTIN
# ---------------------------------------------------------------------------
def _spy_tax_lookup(monkeypatch) -> list:
    """Record repository duplicate lookups, so rejection can be proven to precede them."""
    calls: list = []
    original = CustomerTaxRegistrationRepository.find_active_tax_match

    def spy(self, tenant_id, tax_type, tax_number):
        calls.append((tax_type, tax_number))
        return original(self, tenant_id, tax_type, tax_number)

    monkeypatch.setattr(CustomerTaxRegistrationRepository, "find_active_tax_match", spy)
    return calls


def test_omitted_tax_type_with_tax_number_rejected(
    client: TestClient, pro_token: str, monkeypatch
) -> None:
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client, pro_token, {"tax_number": _unique_gstin()}
    )
    assert resp.status_code == 422, resp.text
    assert resp.json()["detail"]["error"]["req_id"] == "REQ-CRM-027"
    assert calls == [], "missing tax_type reached the repository duplicate lookup"

@pytest.mark.parametrize("tax_type", ["VAT", "PAN", "CIN"])
def test_unsupported_tax_type_rejected_before_lookup(
    client: TestClient, pro_token: str, monkeypatch, tax_type: str
) -> None:
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client, pro_token, {"tax_type": tax_type, "tax_number": _unique_gstin()}
    )
    assert resp.status_code == 422, resp.text
    error = resp.json()["detail"]["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["req_id"] == "REQ-CRM-027"
    assert calls == [], "unsupported tax_type reached the repository duplicate lookup"


def test_unsupported_tax_type_case_and_whitespace_rejected(
    client: TestClient, pro_token: str, monkeypatch
) -> None:
    """A lower-case, padded unsupported type is still rejected after normalization."""
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client, pro_token, {"tax_type": "  vat  ", "tax_number": _unique_gstin()}
    )
    assert resp.status_code == 422, resp.text
    assert calls == []


def test_empty_tax_type_with_tax_number_rejected(
    client: TestClient, pro_token: str, monkeypatch
) -> None:
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client, pro_token, {"tax_type": "", "tax_number": _unique_gstin()}
    )
    assert resp.status_code == 422, resp.text
    assert calls == []


def test_null_tax_type_with_tax_number_rejected(
    client: TestClient, pro_token: str, monkeypatch
) -> None:
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client, pro_token, {"tax_type": None, "tax_number": _unique_gstin()}
    )
    assert resp.status_code == 422, resp.text
    assert calls == []


@pytest.mark.parametrize("tax_type", ["GSTIN", "gstin", "  gstin  "])
def test_gstin_tax_type_case_and_whitespace_normalized(
    client: TestClient, pro_token: str, tax_type: str
) -> None:
    """The supported type is honoured after strip+upper normalization."""
    resp = _duplicate_check(
        client, pro_token, {"tax_type": tax_type, "tax_number": _unique_gstin()}
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["blocked"] is False


def test_unsupported_tax_type_without_tax_number_is_ignored(
    client: TestClient, pro_token: str, monkeypatch
) -> None:
    """Rejection applies only when a tax number is supplied; name-only checks are unaffected."""
    calls = _spy_tax_lookup(monkeypatch)
    resp = _duplicate_check(
        client,
        pro_token,
        {"tax_type": "VAT", "legal_name": f"No Tax {uuid.uuid4().hex[:6]}"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["blocked"] is False
    assert calls == []
