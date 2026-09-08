from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError, NotFoundError
from app.models.sal import Quotation, QuotationLine, SalesOrder, SalesOrderLine
from app.repositories.crm.opportunity_repository import OpportunityRepository
from app.repositories.crm.customer_repository import CustomerRepository
from app.repositories.pf.branding_repository import TenantBrandingRepository
from app.repositories.pf.user_repository import TenantRepository
from app.repositories.sal.quotation_line_repository import QuotationLineRepository
from app.repositories.sal.quotation_repository import QuotationRepository
from app.repositories.sal.quotation_customer_response_repository import (
    QuotationCustomerResponseRepository,
)
from app.repositories.sal.quotation_status_history_repository import (
    QuotationStatusHistoryRepository,
)
from app.repositories.sal.sales_order_line_repository import SalesOrderLineRepository
from app.repositories.sal.sales_order_repository import SalesOrderRepository
from app.schemas.sal.quotation import (
    QUOTATION_STATUSES,
    STATUS_TRANSITIONS,
    QuotationCreate,
    QuotationCustomerResponseCreate,
    QuotationDetailResponse,
    QuotationLineCreate,
    QuotationLineResponse,
    QuotationLineUpdate,
    QuotationListResponse,
    QuotationResponse,
    QuotationStatusHistoryResponse,
    QuotationStatusUpdate,
    SalesOrderConvertResponse,
)
from app.services.sal.pdf_export import (
    build_quotation_pdf,
    format_line_row,
    resolve_logo_for_pdf,
    tenant_initials,
)

_TAX_RATES: dict[str, Decimal] = {
    "GST18": Decimal("18"),
    "GST12": Decimal("12"),
    "GST5": Decimal("5"),
    "EXEMPT": Decimal("0"),
}
_MONEY = Decimal("0.01")


class QuotationService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = QuotationRepository(db)
        self.lines = QuotationLineRepository(db)
        self.history = QuotationStatusHistoryRepository(db)
        self.customer_responses = QuotationCustomerResponseRepository(db)
        self.sales_orders = SalesOrderRepository(db)
        self.so_lines = SalesOrderLineRepository(db)
        self.opps = OpportunityRepository(db)
        self.customers = CustomerRepository(db)
        self.tenants = TenantRepository(db)
        self.branding = TenantBrandingRepository(db)

    def list_quotations(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        status: str | None = None,
        opportunity_id: UUID | None = None,
    ) -> QuotationListResponse:
        page = max(page, 1)
        page_size = min(max(page_size, 1), 100)
        items, total = self.repo.list(
            tenant_id,
            page=page,
            page_size=page_size,
            status=status,
            opportunity_id=opportunity_id,
        )
        so_map = self.sales_orders.map_by_quotation_ids(
            tenant_id, [i.quotation_id for i in items]
        )
        response_items = []
        for item in items:
            payload = QuotationResponse.model_validate(item).model_dump()
            linked = so_map.get(item.quotation_id)
            if linked is not None:
                payload["sales_order_id"] = linked.sales_order_id
                payload["so_number"] = linked.so_number
            response_items.append(QuotationResponse.model_validate(payload))
        return QuotationListResponse(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_quotation(self, tenant_id: UUID, quotation_id: UUID) -> QuotationDetailResponse:
        quote = self.repo.get_by_id(tenant_id, quotation_id)
        if quote is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        lines = self.lines.list_for_quotation(tenant_id, quotation_id)
        existing_so = self.sales_orders.get_by_quotation(tenant_id, quotation_id)
        payload = QuotationResponse.model_validate(quote).model_dump()
        if existing_so is not None:
            payload["sales_order_id"] = existing_so.sales_order_id
            payload["so_number"] = existing_so.so_number
        return QuotationDetailResponse(
            **payload,
            lines=[QuotationLineResponse.model_validate(line) for line in lines],
        )

    def export_pdf(self, tenant_id: UUID, quotation_id: UUID) -> tuple[bytes, str]:
        quote = self.repo.get_by_id(tenant_id, quotation_id)
        if quote is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        line_rows = self.lines.list_for_quotation(tenant_id, quotation_id)
        tenant = self.tenants.get_by_id(tenant_id)
        tenant_name = (
            (tenant.trade_name or tenant.legal_name) if tenant is not None else "E-LinkUp CRM"
        )
        branding = self.branding.get_by_tenant(tenant_id)
        logo = resolve_logo_for_pdf(branding.logo_url if branding else None)
        primary_color = branding.primary_color if branding else None
        pdf = build_quotation_pdf(
            quote.quotation_number,
            quote.currency_code,
            f"{quote.grand_total}",
            quote.status,
            f"{quote.subtotal}",
            f"{quote.tax_total}",
            [format_line_row(l.line_no, l.description, l.qty, l.line_total) for l in line_rows],
            tenant_name=tenant_name,
            generated_on=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            logo_initials=tenant_initials(tenant_name),
            logo=logo,
            primary_color=primary_color,
        )
        return pdf, f"{quote.quotation_number}.pdf"

    def convert_to_sales_order(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        permissions: frozenset[str],
    ) -> SalesOrderConvertResponse:
        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-SAL-RBAC")
        quote = self.repo.get_by_id(tenant_id, quotation_id)
        if quote is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        if quote.status != "ACCEPTED":
            raise AppError(
                "VALIDATION_ERROR",
                "Quotation must be ACCEPTED before conversion to sales order",
                422,
                req_id="REQ-SAL-007",
            )
        existing = self.sales_orders.get_by_quotation(tenant_id, quotation_id)
        if existing is not None:
            return SalesOrderConvertResponse(
                sales_order_id=existing.sales_order_id,
                so_number=existing.so_number,
                quotation_id=quotation_id,
                status=existing.status,
                message=f"Sales order {existing.so_number} already exists for this quotation",
            )
        row = SalesOrder(
            sales_order_id=uuid4(),
            tenant_id=tenant_id,
            so_number=self._next_so_number(tenant_id),
            quotation_id=quotation_id,
            opportunity_id=quote.opportunity_id,
            customer_id=quote.customer_id,
            status="DRAFT",
            currency_code=quote.currency_code,
            subtotal=quote.subtotal,
            discount_total=quote.discount_total,
            tax_total=quote.tax_total,
            grand_total=quote.grand_total,
        )
        self.db.add(row)
        self.db.flush()
        for qline in self.lines.list_for_quotation(tenant_id, quotation_id):
            self.so_lines.add(
                SalesOrderLine(
                    sales_order_line_id=uuid4(),
                    tenant_id=tenant_id,
                    sales_order_id=row.sales_order_id,
                    quotation_line_id=qline.quotation_line_id,
                    line_no=qline.line_no,
                    product_code=qline.product_code,
                    description=qline.description,
                    qty=qline.qty,
                    unit_price=qline.unit_price,
                    discount_pct=qline.discount_pct,
                    tax_code=qline.tax_code,
                    line_total=qline.line_total,
                )
            )
        self.db.commit()
        self.db.refresh(row)
        saved = row
        return SalesOrderConvertResponse(
            sales_order_id=saved.sales_order_id,
            so_number=saved.so_number,
            quotation_id=quotation_id,
            status=saved.status,
            message=f"Sales order {saved.so_number} created from {quote.quotation_number}",
        )

    def transition_status(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        payload: QuotationStatusUpdate,
        permissions: frozenset[str],
        actor_id: UUID | None = None,
    ) -> QuotationResponse:
        return self._apply_status_change(
            tenant_id, quotation_id, payload.status, permissions, actor_id, payload.reason
        )

    def record_customer_response(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        payload: QuotationCustomerResponseCreate,
        permissions: frozenset[str],
        actor_id: UUID | None = None,
    ) -> QuotationResponse:
        if "quotation.update" not in permissions:
            raise ForbiddenError("Missing permission 'quotation.update'", req_id="REQ-SAL-RBAC")
        target = payload.response_type.upper()
        comment = payload.comment
        if target == "ACCEPTED":
            comment = comment or "Customer accepted quotation"
        result = self._apply_status_change(
            tenant_id, quotation_id, target, permissions, actor_id, comment
        )
        response_type = "ACCEPT" if target == "ACCEPTED" else "REJECT"
        self.customer_responses.add(
            tenant_id, quotation_id, response_type, actor_id, comment
        )
        self.db.commit()
        return result

    def list_status_history(
        self, tenant_id: UUID, quotation_id: UUID
    ) -> list[QuotationStatusHistoryResponse]:
        if self.repo.get_by_id(tenant_id, quotation_id) is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        rows = self.history.list_for_quotation(tenant_id, quotation_id)
        return [QuotationStatusHistoryResponse.model_validate(r) for r in rows]

    def _apply_status_change(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        target_status: str,
        permissions: frozenset[str],
        actor_id: UUID | None,
        reason: str | None,
    ) -> QuotationResponse:
        quote = self.repo.get_by_id(tenant_id, quotation_id)
        if quote is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        target = target_status.upper()
        if target not in QUOTATION_STATUSES:
            raise AppError("VALIDATION_ERROR", f"Invalid status '{target_status}'", 422)
        allowed = STATUS_TRANSITIONS.get(quote.status, frozenset())
        if target not in allowed:
            raise AppError(
                "VALIDATION_ERROR",
                f"Cannot transition from {quote.status} to {target}",
                422,
                req_id="REQ-SAL-005",
            )
        perm = self._permission_for_transition(quote.status, target)
        if perm not in permissions:
            raise ForbiddenError(f"Missing permission '{perm}'", req_id="REQ-SAL-RBAC")
        if target == "SUBMITTED" and not self.lines.list_for_quotation(tenant_id, quotation_id):
            raise AppError(
                "VALIDATION_ERROR",
                "At least one line is required to submit",
                422,
                req_id="REQ-SAL-006",
            )
        from_status = quote.status
        quote.status = target
        self.history.add(tenant_id, quotation_id, from_status, target, actor_id, reason)
        self.db.commit()
        self.db.refresh(quote)
        return QuotationResponse.model_validate(quote)

    @staticmethod
    def _permission_for_transition(from_status: str, to_status: str) -> str:
        if to_status == "SUBMITTED":
            return "quotation.submit"
        if to_status in {"APPROVED", "REJECTED"} and from_status == "SUBMITTED":
            return "quotation.approve"
        if to_status in {"ACCEPTED", "REJECTED"} and from_status == "SENT":
            return "quotation.update"
        if to_status == "CANCELLED":
            return "quotation.cancel"
        return "quotation.update"

    def create_quotation(
        self, tenant_id: UUID, owner_id: UUID, payload: QuotationCreate
    ) -> QuotationResponse:
        customer_id = payload.customer_id
        opportunity_id = payload.opportunity_id
        if opportunity_id is None and customer_id is None:
            raise AppError(
                "VALIDATION_ERROR",
                "customer_id or opportunity_id is required",
                422,
                req_id="REQ-SAL-001",
            )
        if opportunity_id:
            opp = self.opps.get_by_id(tenant_id, opportunity_id)
            if opp is None:
                raise NotFoundError("Opportunity not found", req_id="REQ-CRM-002")
            customer_id = customer_id or opp.customer_id
        if customer_id:
            if self.customers.get_by_id(tenant_id, customer_id) is None:
                raise NotFoundError("Customer not found", req_id="REQ-CRM-003")

        row = Quotation(
            quotation_id=uuid4(),
            tenant_id=tenant_id,
            quotation_number=self._next_number(tenant_id),
            opportunity_id=opportunity_id,
            customer_id=customer_id,
            owner_id=owner_id,
            status="DRAFT",
            currency_code=(payload.currency_code or "INR").upper(),
            valid_until=payload.valid_until,
            notes=payload.notes,
        )
        saved = self.repo.add(row)
        return QuotationResponse.model_validate(saved)

    def add_line(
        self, tenant_id: UUID, quotation_id: UUID, payload: QuotationLineCreate
    ) -> QuotationLineResponse:
        quote = self._require_draft(tenant_id, quotation_id)
        line_total = self._apply_line_amounts(
            payload.qty, payload.unit_price, payload.discount_pct, payload.tax_code
        )
        row = QuotationLine(
            quotation_line_id=uuid4(),
            tenant_id=tenant_id,
            quotation_id=quotation_id,
            line_no=self.lines.next_line_no(tenant_id, quotation_id),
            product_code=payload.product_code,
            description=payload.description,
            qty=payload.qty,
            unit_price=payload.unit_price,
            discount_pct=payload.discount_pct,
            tax_code=(payload.tax_code or "EXEMPT").upper(),
            line_total=line_total,
        )
        saved = self.lines.add(row)
        self._recalc_totals(quote)
        self.db.commit()
        self.db.refresh(saved)
        return QuotationLineResponse.model_validate(saved)

    def update_line(
        self,
        tenant_id: UUID,
        quotation_id: UUID,
        line_id: UUID,
        payload: QuotationLineUpdate,
    ) -> QuotationLineResponse:
        quote = self._require_draft(tenant_id, quotation_id)
        row = self.lines.get_by_id(tenant_id, quotation_id, line_id)
        if row is None:
            raise NotFoundError("Quotation line not found", req_id="REQ-SAL-002")
        if payload.product_code is not None:
            row.product_code = payload.product_code
        if payload.description is not None:
            row.description = payload.description
        qty = payload.qty if payload.qty is not None else row.qty
        unit_price = payload.unit_price if payload.unit_price is not None else row.unit_price
        discount_pct = (
            payload.discount_pct if payload.discount_pct is not None else row.discount_pct
        )
        tax_code = payload.tax_code if payload.tax_code is not None else row.tax_code
        row.qty = qty
        row.unit_price = unit_price
        row.discount_pct = discount_pct
        row.tax_code = (tax_code or "EXEMPT").upper()
        row.line_total = self._apply_line_amounts(qty, unit_price, discount_pct, row.tax_code)
        self._recalc_totals(quote)
        self.db.commit()
        self.db.refresh(row)
        return QuotationLineResponse.model_validate(row)

    def delete_line(self, tenant_id: UUID, quotation_id: UUID, line_id: UUID) -> None:
        quote = self._require_draft(tenant_id, quotation_id)
        row = self.lines.get_by_id(tenant_id, quotation_id, line_id)
        if row is None:
            raise NotFoundError("Quotation line not found", req_id="REQ-SAL-002")
        self.lines.soft_delete(row)
        self._recalc_totals(quote)
        self.db.commit()

    def _require_draft(self, tenant_id: UUID, quotation_id: UUID) -> Quotation:
        quote = self.repo.get_by_id(tenant_id, quotation_id)
        if quote is None:
            raise NotFoundError("Quotation not found", req_id="REQ-SAL-003")
        if quote.status != "DRAFT":
            raise AppError(
                "VALIDATION_ERROR",
                "Only draft quotations can be edited",
                422,
                req_id="REQ-SAL-004",
            )
        return quote

    def _apply_line_amounts(
        self, qty: Decimal, unit_price: Decimal, discount_pct: Decimal, tax_code: str | None
    ) -> Decimal:
        gross = (qty * unit_price).quantize(_MONEY)
        discount = (gross * discount_pct / Decimal("100")).quantize(_MONEY)
        taxable = gross - discount
        rate = _TAX_RATES.get((tax_code or "EXEMPT").upper(), Decimal("0"))
        tax = (taxable * rate / Decimal("100")).quantize(_MONEY)
        return taxable + tax

    def _line_parts(
        self, qty: Decimal, unit_price: Decimal, discount_pct: Decimal, tax_code: str | None
    ) -> tuple[Decimal, Decimal, Decimal]:
        gross = (qty * unit_price).quantize(_MONEY)
        discount = (gross * discount_pct / Decimal("100")).quantize(_MONEY)
        taxable = gross - discount
        rate = _TAX_RATES.get((tax_code or "EXEMPT").upper(), Decimal("0"))
        tax = (taxable * rate / Decimal("100")).quantize(_MONEY)
        return gross, discount, tax

    def _recalc_totals(self, quote: Quotation) -> None:
        subtotal = Decimal("0")
        discount_total = Decimal("0")
        tax_total = Decimal("0")
        for line in self.lines.list_for_quotation(quote.tenant_id, quote.quotation_id):
            gross, discount, tax = self._line_parts(
                line.qty, line.unit_price, line.discount_pct, line.tax_code
            )
            subtotal += gross
            discount_total += discount
            tax_total += tax
        quote.subtotal = subtotal
        quote.discount_total = discount_total
        quote.tax_total = tax_total
        quote.grand_total = subtotal - discount_total + tax_total
        self.db.flush()

    def _next_number(self, tenant_id: UUID) -> str:
        year = date.today().year
        seq = self.repo.next_sequence(tenant_id, year)
        return f"QUO-{year}-{seq:06d}"

    def _next_so_number(self, tenant_id: UUID) -> str:
        year = date.today().year
        seq = self.sales_orders.next_sequence(tenant_id, year)
        return f"SO-{year}-{seq:06d}"
