from datetime import date
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, NotFoundError
from app.models.crm import Customer, CustomerAddress, CustomerContact, Lead, Opportunity
from app.models.pf import Tenant
from app.repositories.crm.customer_contact_repository import (
    CustomerAddressRepository,
    CustomerContactRepository,
)
from app.repositories.crm.customer_repository import CustomerRepository
from app.repositories.crm.lead_repository import LeadRepository
from app.repositories.pf.user_repository import TenantRepository
from app.schemas.crm.customer import (
    CustomerAddressCreate,
    CustomerAddressResponse,
    CustomerContactCreate,
    CustomerContactResponse,
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerUpdate,
)


class CustomerService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = CustomerRepository(db)
        self.contacts = CustomerContactRepository(db)
        self.addresses = CustomerAddressRepository(db)
        self.leads = LeadRepository(db)
        self.tenants = TenantRepository(db)

    def list_customers(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 25,
        search: str | None = None,
        status: str | None = None,
    ) -> CustomerListResponse:
        items, total = self.repo.list(
            tenant_id, page=page, page_size=page_size, search=search, status=status
        )
        return CustomerListResponse(
            items=[self._to_response(c, include_children=False) for c in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_customer(self, tenant_id: UUID, customer_id: UUID) -> CustomerResponse:
        row = self.repo.get_by_id(tenant_id, customer_id)
        if row is None:
            raise NotFoundError("Customer not found", req_id="REQ-CRM-003")
        return self._to_response(row, include_children=True)

    def create_customer(
        self, tenant_id: UUID, owner_id: UUID, payload: CustomerCreate
    ) -> CustomerResponse:
        status = (payload.status or "PROSPECT").upper()
        if status == "ACTIVE":
            raise AppError(
                "VALIDATION_ERROR",
                "Add contact and address before activating (BR-CRM-043/044)",
                422,
                req_id="REQ-CRM-003",
            )
        customer = Customer(
            customer_id=uuid4(),
            tenant_id=tenant_id,
            customer_number=self._next_number(tenant_id),
            legal_name=payload.legal_name.strip(),
            trade_name=(payload.trade_name or "").strip() or None,
            customer_type=(payload.customer_type or "ACCOUNT").upper(),
            status=status,
            owner_id=owner_id,
            source_opportunity_id=payload.source_opportunity_id,
            notes=payload.notes,
        )
        return self._to_response(self.repo.add(customer), include_children=True)

    def create_from_opportunity(
        self, tenant_id: UUID, owner_id: UUID, opp: Opportunity
    ) -> Customer:
        if opp.customer_id:
            existing = self.repo.get_by_id(tenant_id, opp.customer_id)
            if existing:
                return existing
        legal = (opp.company_name or opp.name).strip()[:250]
        customer = Customer(
            customer_id=uuid4(),
            tenant_id=tenant_id,
            customer_number=self._next_number(tenant_id),
            legal_name=legal,
            trade_name=opp.name if opp.company_name else None,
            customer_type="ACCOUNT",
            status="ACTIVE",
            owner_id=owner_id,
            source_opportunity_id=opp.opportunity_id,
            notes=f"Auto-created from closed-won {opp.opportunity_number}",
        )
        customer = self.repo.add(customer)
        if opp.source_lead_id:
            lead = self.leads.get_by_id(tenant_id, opp.source_lead_id)
            if lead:
                self._add_contact_from_lead(tenant_id, customer.customer_id, lead)
        return customer

    def add_contact(
        self, tenant_id: UUID, customer_id: UUID, payload: CustomerContactCreate
    ) -> CustomerContactResponse:
        customer = self.repo.get_by_id(tenant_id, customer_id)
        if customer is None:
            raise NotFoundError("Customer not found", req_id="REQ-CRM-003")
        row = CustomerContact(
            customer_contact_id=uuid4(),
            tenant_id=tenant_id,
            customer_id=customer_id,
            first_name=payload.first_name.strip(),
            last_name=(payload.last_name or "").strip() or None,
            job_title=payload.job_title,
            email=(payload.email or "").strip().lower() or None,
            phone_mobile=payload.phone_mobile,
            phone_work=payload.phone_work,
            contact_role=payload.contact_role,
            is_primary=payload.is_primary,
            is_decision_maker=payload.is_decision_maker,
        )
        return CustomerContactResponse.model_validate(self.contacts.add(row))

    def add_address(
        self, tenant_id: UUID, customer_id: UUID, payload: CustomerAddressCreate
    ) -> CustomerAddressResponse:
        customer = self.repo.get_by_id(tenant_id, customer_id)
        if customer is None:
            raise NotFoundError("Customer not found", req_id="REQ-CRM-003")
        row = CustomerAddress(
            customer_address_id=uuid4(),
            tenant_id=tenant_id,
            customer_id=customer_id,
            address_type=(payload.address_type or "REGISTERED").upper(),
            address_line1=payload.address_line1.strip(),
            address_line2=(payload.address_line2 or "").strip() or None,
            city=payload.city,
            state=payload.state,
            country=payload.country,
            postal_code=payload.postal_code,
            is_default_billing=payload.is_default_billing,
            is_default_shipping=payload.is_default_shipping,
        )
        return CustomerAddressResponse.model_validate(self.addresses.add(row))

    def update_customer(
        self, tenant_id: UUID, customer_id: UUID, payload: CustomerUpdate
    ) -> CustomerResponse:
        row = self.repo.get_by_id(tenant_id, customer_id)
        if row is None:
            raise NotFoundError("Customer not found", req_id="REQ-CRM-003")
        data = payload.model_dump(exclude_unset=True)
        if "legal_name" in data and data["legal_name"]:
            row.legal_name = data["legal_name"].strip()
        if "trade_name" in data:
            row.trade_name = data["trade_name"]
        if "status" in data and data["status"]:
            new_status = data["status"].upper()
            if new_status == "ACTIVE" and row.status != "ACTIVE":
                self._validate_active_prerequisites(tenant_id, customer_id)
            row.status = new_status
        if "notes" in data:
            row.notes = data["notes"]
        return self._to_response(self.repo.save(row), include_children=True)

    def convert_from_lead(
        self, tenant_id: UUID, owner_id: UUID, lead_id: UUID
    ) -> CustomerResponse:
        from app.repositories.crm.lead_repository import LeadRepository

        leads = LeadRepository(self.db)
        lead = leads.get_by_id(tenant_id, lead_id)
        if lead is None:
            raise NotFoundError("Lead not found", req_id="REQ-CRM-002")
        if lead.status == "CONVERTED":
            raise AppError("CONFLICT", "Lead is already converted", 409, req_id="REQ-CRM-002")
        if lead.status == "DISQUALIFIED":
            raise AppError(
                "VALIDATION_ERROR",
                "Disqualified leads cannot be converted",
                422,
                req_id="REQ-CRM-002",
            )
        legal = (lead.company_name or lead.full_name).strip()[:250]
        customer = Customer(
            customer_id=uuid4(),
            tenant_id=tenant_id,
            customer_number=self._next_number(tenant_id),
            legal_name=legal,
            trade_name=lead.company_name,
            customer_type="ACCOUNT",
            status="PROSPECT",
            owner_id=owner_id,
            notes=f"Converted from lead {lead.lead_number}",
        )
        saved = self.repo.add(customer)
        self._add_contact_from_lead(tenant_id, saved.customer_id, lead)
        lead.status = "CONVERTED"
        leads.save(lead)
        return self._to_response(saved, include_children=True)

    def _validate_active_prerequisites(self, tenant_id: UUID, customer_id: UUID) -> None:
        contacts = self.contacts.list_for_customer(tenant_id, customer_id)
        if not any(c.is_primary for c in contacts):
            raise AppError(
                "VALIDATION_ERROR",
                "At least one primary customer contact required before Active (BR-CRM-043)",
                422,
                req_id="REQ-CRM-003",
            )
        addresses = self.addresses.list_for_customer(tenant_id, customer_id)
        types = {a.address_type for a in addresses}
        if not types.intersection({"REGISTERED", "BILLING"}):
            raise AppError(
                "VALIDATION_ERROR",
                "Registered or Billing address required before Active (BR-CRM-044)",
                422,
                req_id="REQ-CRM-003",
            )

    def _add_contact_from_lead(
        self, tenant_id: UUID, customer_id: UUID, lead: Lead
    ) -> None:
        parts = (lead.full_name or "").strip().split(None, 1)
        first = parts[0] if parts else "Primary"
        last = parts[1] if len(parts) > 1 else None
        self.contacts.add(
            CustomerContact(
                customer_contact_id=uuid4(),
                tenant_id=tenant_id,
                customer_id=customer_id,
                first_name=first[:100],
                last_name=last[:100] if last else None,
                email=(lead.email or "").strip().lower() or None,
                phone_mobile=lead.phone,
                is_primary=True,
            )
        )

    def _to_response(self, row: Customer, *, include_children: bool) -> CustomerResponse:
        contacts: list[CustomerContact] = []
        addresses: list[CustomerAddress] = []
        if include_children:
            contacts = self.contacts.list_for_customer(row.tenant_id, row.customer_id)
            addresses = self.addresses.list_for_customer(row.tenant_id, row.customer_id)
        base = CustomerResponse.model_validate(row)
        return base.model_copy(
            update={
                "contacts": [CustomerContactResponse.model_validate(c) for c in contacts],
                "addresses": [CustomerAddressResponse.model_validate(a) for a in addresses],
            }
        )

    def _next_number(self, tenant_id: UUID) -> str:
        tenant: Tenant | None = self.tenants.get_by_id(tenant_id)
        prefix = (
            "".join(ch for ch in tenant.tenant_name if ch.isalpha())[:3] or "EUP"
        ).upper() if tenant and tenant.tenant_name else "EUP"
        year = date.today().year
        seq = self.repo.next_sequence(tenant_id, year)
        return f"{prefix}-CUS-{year}-{seq:05d}"
