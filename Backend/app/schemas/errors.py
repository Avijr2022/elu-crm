"""Shared error-envelope schemas (OpenAPI documentation only).

Every ``AppError`` is rendered by ``app.core.exceptions.error_body()`` and returned by
the ``AppError`` handler in ``app.main.create_app`` as::

    {"error": {"code": ..., "message": ..., "req_id": ..., "details": ...,
               "request_id": ...}}

These models mirror that envelope exactly so a route can declare its error responses
without inventing a different body shape. They are documentation artefacts: the
handler still serialises ``error_body()`` directly and no response is validated
against them at runtime.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """One error occurrence, exactly as ``error_body()`` builds it."""

    code: str
    message: str
    req_id: Optional[str] = None
    details: dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None


class ErrorResponse(BaseModel):
    """The ``{"error": {...}}`` envelope returned for every ``AppError``."""

    error: ErrorDetail
