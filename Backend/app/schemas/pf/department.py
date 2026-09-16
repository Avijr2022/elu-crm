"""PF-006 Department Management schemas (ELU-BFS-PF-006 §9/§10).

Conventions follow ``app/schemas/pf/branch.py`` (PF-005). PUT and PATCH use distinct
models: ``DepartmentReplace`` (PUT — ``name`` required) and ``DepartmentUpdate``
(PATCH — all optional); both carry ``version_no`` for optimistic locking.

Batch 2 scope: schemas only. Batch 5 adds the move request schema and the typed history
response used by the API layer (`GET /org/departments/{id}/history`, PF-004 convention).

Scope notes:
  * ``department_type`` is handled as a **plain value** — no enum, no invented
    allowed-value list, no value validation (C-N1: the approved specification names the
    field but defines no value list).
  * ``status`` is limited to ``ACTIVE`` / ``INACTIVE`` / ``ARCHIVED`` (C-N3,
    `ELU-BFS-PF-006` §5); default on create is ``ACTIVE``.
  * ``department_head_user_id`` is exposed **read-only** and is never accepted on input —
    department-head assignment/validation (`BR-PF-043` / `AC-PF-006-04`) is deferred to
    PF-008; no user-existence or ACTIVE-user validation is performed here.
  * No ``level``/``path`` fields (C-N2 — hierarchy information is derived at read time).
  * No address fields (C-N6) and no ``users.department_id`` / ``users.branch_id`` (PF-008).
  * Hierarchy depth (`BR-PF-041`) and circular-parent (`BR-PF-042`) rules are
    service-layer concerns and are deliberately **not** implemented in Pydantic.
"""

import re
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

DEPARTMENT_STATUSES = ("ACTIVE", "INACTIVE", "ARCHIVED")

_CODE_RE = re.compile(r"[A-Z0-9_-]{2,30}")


def _normalize_status(value: str, field: str = "status") -> str:
    """Normalise and validate the approved PF-006 lifecycle values (C-N3)."""
    normalized = value.strip().upper()
    if normalized not in DEPARTMENT_STATUSES:
        raise ValueError(f"{field} must be one of {', '.join(DEPARTMENT_STATUSES)}")
    return normalized


def _normalize_type(value: str) -> str:
    """Normalise ``department_type`` without inventing an allowed-value list (C-N1)."""
    normalized = value.strip()
    if not normalized:
        raise ValueError("department_type must not be blank")
    return normalized


class DepartmentCreate(BaseModel):
    """POST payload — create department (ELU-BFS-PF-006 §10)."""

    code: str = Field(min_length=2, max_length=30)
    name: str = Field(min_length=2, max_length=200)
    department_type: str = Field(min_length=1, max_length=32)
    organization_id: UUID
    parent_department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    description: Optional[str] = Field(default=None, max_length=500)
    cost_centre_code: Optional[str] = Field(default=None, max_length=32)
    status: str = Field(default="ACTIVE")

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        code = v.strip().upper()
        if not _CODE_RE.fullmatch(code):
            raise ValueError("code must be 2–30 chars A-Z0-9_-")
        return code

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    @field_validator("department_type")
    @classmethod
    def validate_department_type(cls, v: str) -> str:
        return _normalize_type(v)

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        return _normalize_status(v)


class DepartmentUpdate(BaseModel):
    """PATCH payload — partial update (ELU-BFS-PF-006 §10).

    ``code`` is deliberately absent: the department code is immutable (PF-004/PF-005
    convention). ``department_head_user_id`` is not accepted — it is read-only (PF-008).
    """

    name: Optional[str] = Field(default=None, min_length=2, max_length=200)
    department_type: Optional[str] = Field(default=None, min_length=1, max_length=32)
    organization_id: Optional[UUID] = None
    parent_department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    description: Optional[str] = Field(default=None, max_length=500)
    cost_centre_code: Optional[str] = Field(default=None, max_length=32)
    status: Optional[str] = None
    version_no: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        return v.strip() if v is not None else v

    @field_validator("department_type")
    @classmethod
    def validate_department_type(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_type(v) if v is not None else v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        return _normalize_status(v) if v is not None else v


class DepartmentReplace(DepartmentUpdate):
    """PUT payload — full replace (ELU-BFS-PF-006 §10 "Full update").

    Mirrors the PF-004/PF-005 PUT rule: ``name`` is mandatory; ``code`` is immutable.
    """

    name: str = Field(min_length=2, max_length=200)


class DepartmentMove(BaseModel):
    """PATCH payload — reparent (ELU-BFS-PF-006 §10 ``PATCH /{id}/move``).

    ``parent_department_id = None`` detaches the department to root level. ``code`` is
    immutable and is not accepted; ``organization_id`` is deliberately **not** part of
    the move operation (an organization change is a separate, policy-guarded update).
    """

    parent_department_id: Optional[UUID] = None
    version_no: int


class DepartmentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    department_type: str
    organization_id: UUID
    parent_department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    # Read-only: department-head assignment/validation is deferred to PF-008.
    department_head_user_id: Optional[UUID] = None
    description: Optional[str] = None
    cost_centre_code: Optional[str] = None
    status: str
    # Non-blocking advisories (BR-PF-045 "at least one department recommended").
    warnings: list[str] = []
    version_no: int
    created_on: datetime
    modified_on: Optional[datetime] = None

    model_config = {"from_attributes": True}


class DepartmentListResponse(BaseModel):
    items: list[DepartmentResponse]
    page: int
    page_size: int
    total: int
    warnings: list[str] = []


class DepartmentHierarchyNode(BaseModel):
    id: UUID
    code: str
    name: str
    department_type: str
    organization_id: UUID
    parent_department_id: Optional[UUID] = None
    branch_id: Optional[UUID] = None
    status: str
    children: list["DepartmentHierarchyNode"] = []


class DepartmentHierarchyResponse(BaseModel):
    """Tenant-wide department tree (ELU-BFS-PF-006 §10 ``GET /org/departments/hierarchy``).

    A forest is returned because departments without a parent are valid roots. Depth
    (``BR-PF-041``) is a service-layer rule and is not encoded in the schema.
    """

    items: list[DepartmentHierarchyNode] = []
    warnings: list[str] = []


class DepartmentHistoryItem(BaseModel):
    """Audit-trail row (ELU-BFS-PF-006 §15) — same keys as the PF-004/PF-005 item."""

    id: UUID
    event_type: str
    event_category: str
    actor_email: Optional[str] = None
    payload_json: Optional[str] = None
    created_on: datetime


class DepartmentHistoryResponse(BaseModel):
    """``GET /org/departments/{id}/history`` response (PF-004/PF-005 typed convention)."""

    items: list[DepartmentHistoryItem]
    total: int
