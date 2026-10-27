"""REQ-CRM-027 / BR-CRM-042 / BR-CRM-045 — pre-create customer duplicate check."""

import re
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.exceptions import ValidationAppError

_GSTIN_RE = re.compile(
    r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"
)


def normalize_tax_number(tax_number: str) -> str:
    return tax_number.strip().upper().replace(" ", "")


def normalize_customer_name(value: str) -> str:
    return " ".join(value.split()).casefold()


def validate_gstin_tax_number(tax_number: str) -> str:
    normalized = normalize_tax_number(tax_number)
    if not _GSTIN_RE.fullmatch(normalized):
        raise ValidationAppError(
            "Invalid GSTIN format (BR-CRM-042)",
            req_id="REQ-CRM-027",
        )
    return normalized


# BR-CRM-045 / REQ-CRM-027: GSTIN is the only tax identifier supported by the
# duplicate check. Any other type must be rejected rather than silently read as GSTIN.
SUPPORTED_TAX_TYPES: tuple[str, ...] = ("GSTIN",)


def validate_tax_type(tax_type: Optional[str]) -> str:
    """Allow only a supported, normalized ``tax_type`` (GSTIN).

    Called only when a ``tax_number`` is supplied, so a name-only duplicate check is
    unaffected. Rejecting here means an unsupported or missing type can never reach the
    repository lookup, and that no other type is interpreted as GSTIN.
    """
    normalized = (tax_type or "").strip().upper()
    if not normalized:
        raise ValidationAppError(
            "tax_type is required when tax_number is supplied (BR-CRM-045)",
            req_id="REQ-CRM-027",
        )
    if normalized not in SUPPORTED_TAX_TYPES:
        raise ValidationAppError(
            "Unsupported tax_type '"
            + normalized
            + "' (supported: "
            + ", ".join(SUPPORTED_TAX_TYPES)
            + ") (BR-CRM-045)",
            req_id="REQ-CRM-027",
        )
    return normalized


def mask_tax_number(tax_number: str) -> str:
    if len(tax_number) <= 4:
        return "***"
    return f"***{tax_number[-4:]}"


class CustomerDuplicateCheckRequest(BaseModel):
    legal_name: Optional[str] = Field(default=None, max_length=250)
    trade_name: Optional[str] = Field(default=None, max_length=200)
    tax_type: str = Field(default="GSTIN", max_length=20)
    tax_number: Optional[str] = Field(default=None, max_length=30)
    state_code: Optional[str] = Field(default=None, max_length=10)

    @field_validator("tax_type")
    @classmethod
    def tax_type_nonempty(cls, v: str) -> str:
        t = v.strip().upper()
        if not t:
            raise ValueError("tax_type is required")
        return t

    @field_validator("legal_name", "trade_name")
    @classmethod
    def strip_optional_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s or None


class CustomerDuplicateMatch(BaseModel):
    customer_id: UUID
    customer_number: str
    legal_name: str
    trade_name: Optional[str] = None
    match_kind: Literal["TAX_ID", "LEGAL_NAME", "TRADE_NAME"]
    severity: Literal["BLOCK", "WARNING"]
    tax_number_masked: Optional[str] = None


class CustomerDuplicateCheckResponse(BaseModel):
    blocked: bool
    matches: list[CustomerDuplicateMatch]
