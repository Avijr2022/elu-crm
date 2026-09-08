"""Unit tests for PaymentReceiptService.allocate_to_invoice using simple fakes.

These tests avoid DB dependencies by injecting fake repositories.
"""
from decimal import Decimal
from uuid import uuid4

from app.core.exceptions import ConflictError, ValidationAppError
from app.services.fin.payment_receipt_service import PaymentReceiptService


class DummyReceipt:
    def __init__(self, amount: Decimal):
        self.amount = amount


class FakeAllocRepo:
    def __init__(self, existing=None):
        self.existing = existing or []
        self.added = []

    def list_for_receipt(self, tenant_id, payment_receipt_id):
        return self.existing

    def add(self, row):
        self.added.append(row)
        return row


class FakeReceiptRepo:
    def __init__(self, receipt=None):
        self._receipt = receipt

    def get_by_id(self, tenant_id, payment_receipt_id):
        return self._receipt


class FakeInvoiceRepo:
    def __init__(self, exists=True):
        self.exists = exists

    def get_by_id(self, tenant_id, invoice_id):
        return object() if self.exists else None


def make_service(receipt_amount: Decimal, existing_allocs=None, invoice_exists=True):
    svc = PaymentReceiptService(db=None)
    class DummyDB:
        def commit(self):
            return None

    svc.db = DummyDB()
    svc.repo = FakeReceiptRepo(DummyReceipt(receipt_amount))
    svc.allocations = FakeAllocRepo(existing=existing_allocs)
    # monkeypatch invoice repository lookup via import inside method: we'll set attribute on svc
    svc._invoice_repo = FakeInvoiceRepo(invoice_exists)
    # Workaround: the service imports InvoiceRepository inside method; we'll monkeypatch by
    # setting attribute name used via closure in tests by replacing the imported name in module
    from app.services.fin import payment_receipt_service as mod

    class DummyInvoiceRepoFactory:
        def __init__(self, db):
            pass

        def get_by_id(self_inner, tenant_id, invoice_id):
            return svc._invoice_repo.get_by_id(tenant_id, invoice_id)

    # Patch the repository used by the service (imported from app.repositories.fin.invoice_repository)
    import app.repositories.fin.invoice_repository as inv_mod

    inv_mod.InvoiceRepository = DummyInvoiceRepoFactory
    return svc


def test_full_allocation():
    svc = make_service(Decimal("100.00"), existing_allocs=[])
    alloc = svc.allocate_to_invoice(uuid4(), uuid4(), uuid4(), frozenset(["quotation.update"]))
    assert alloc.allocated_amount == Decimal("100.00")


def test_partial_allocation():
    svc = make_service(Decimal("200.00"), existing_allocs=[])
    alloc = svc.allocate_to_invoice(uuid4(), uuid4(), uuid4(), frozenset(["quotation.update"]), allocated_amount=50.0)
    assert alloc.allocated_amount == Decimal("50.00")


def test_over_allocate_raises_conflict():
    svc = make_service(Decimal("50.00"), existing_allocs=[])
    try:
        svc.allocate_to_invoice(uuid4(), uuid4(), uuid4(), frozenset(["quotation.update"]), allocated_amount=100.0)
        assert False, "should have raised ConflictError"
    except ConflictError:
        pass


def test_negative_or_zero_raises_validation():
    svc = make_service(Decimal("100.00"), existing_allocs=[])
    try:
        svc.allocate_to_invoice(uuid4(), uuid4(), uuid4(), frozenset(["quotation.update"]), allocated_amount=0)
        assert False
    except ValidationAppError:
        pass
