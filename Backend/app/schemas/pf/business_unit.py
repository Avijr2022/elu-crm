"""PF-007 Business Unit Management schemas (ELU-BFS-PF-007 §9/§10).

Conventions follow ``app/schemas/pf/department.py`` (PF-006) and
``app/schemas/pf/branch.py`` (PF-005). PUT and PATCH use distinct models:
``BusinessUnitReplace`` (PUT — ``name`` required) and ``BusinessUnitUpdate``
(PATCH — all optional); both carry ``version_no`` for optimistic locking.

Scope notes (approved D1-D11 decisions):
  * D1  — exactly the 8 BFS §10 endpoints are exposed; there is **no** history schema.
  * D4  — ``bu_manager_user_id`` IS accepted on input (create/update) and validated by the
          service against an ACTIVE user of the same tenant (BR-PF-048). No
          ``users.business_unit_id`` field exists and the column carries no FK.
  * D7  — ``organization_id`` is accepted on create; on update it may only be repeated
          unchanged (the service rejects any change — organization_id is immutable).
  * D9  — ``status`` is limited to ``ACTIVE`` / ``INACTIVE`` / ``ARCHIVED`` (§5); default on
          create is ``ACTIVE``. ``description`` (500) and ``cost_centre_code`` (32) follow
          the PF-006 lengths; ``revenue_target_annual`` is a non-negative monetary amount
          (NUMERIC(18,2) convention) and ``start_date``/``end_date`` are plain optional
          dates — the specification defines no cross-field rule, so none is invented.
"""

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

BUSINESS_UNIT_STATUSES = ("ACTIVE", "INACTIVE", "ARCHIVED")

_CODE_RE = re.compile(r"[A-Z0-9_-]{2,30}")


def _normalize_status(value: str, field: str = "status") -> str:
    """Normalise and validate the approved PF-007 lifecycle values (§5)."""
    normalized = value.strip().upper()
    if normalized not in BUSINESS_UNIT_STATUSES:
        raise ValueError(f"{field} must be one of {', '.join(BUSINESS_UNIT_STATUSES)}")
    return normalized


class BusinessUnitCreate(BaseModel):
    """POST payload — create business unit (ELU-BFS-PF-007 §10)."""

    code: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=200)
    organization_id: UUID
    description: Optional[str] = Field(default=None, max_length=500)
    bu_manager_user_id: Optional[UUID] = None
    cost_centre_code: Optional[str] = Field(default=None, max_length=32)
    revenue_target_annual: Optional[Decimal] = Field(default=None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str = Field(default="ACTIVE")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not _CODE_RE.fullmatch(code):
            raise ValueError("code must be 2-30 chars A-Z0-9_-")
        return code

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return _normalize_status(v)


class BusinessUnitUpdate(BaseModel):
    """PATCH payload — partial update (ELU-BFS-PF-007 §10).

    ``code`` is deliberately absent: the business-unit code is immutable (PF-004/PF-005/
    PF-006 convention). ``organization_id`` is accepted only so that a change can be
    explicitly rejected (D7 — immutable after creation).
    """

    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    organization_id: Optional[UUID] = None
    description: Optional[str] = Field(default=None, max_length=500)
    bu_manager_user_id: Optional[UUID] = None
    cost_centre_code: Optional[str] = Field(default=None, max_length=32)
    revenue_target_annual: Optional[Decimal] = Field(default=None, ge=0)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: Optional[str] = None
    version_no: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v is not None else v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_status(v) if v is not None else v


class BusinessUnitReplace(BusinessUnitUpdate):
    """PUT payload — full replace (ELU-BFS-PF-007 §10 "Full update").

    Mirrors the PF-004/PF-005/PF-006 PUT rule: ``name`` is mandatory; ``code`` is
    immutable.
    """

    name: str = Field(min_length=2, max_length=200)


class BusinessUnitResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    organization_id: UUID
    description: Optional[str] = None
    # Accepted on input and validated against an ACTIVE same-tenant user (BR-PF-048 / D4);
    # no FK and no users.business_unit_id linkage (PF-008).
    bu_manager_user_id: Optional[UUID] = None
    cost_centre_code: Optional[str] = None
    revenue_target_annual: Optional[Decimal] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    status: str
    warnings: list[str] = []
    version_no: int
    created_on: datetime
    modified_on: Optional[datetime] = None

    model_config = {"from_attributes": True}


class BusinessUnitListResponse(BaseModel):
    items: list[BusinessUnitResponse]
    page: int
    page_size: int
    total: int
    warnings: list[str] = []
