"""M-2: the suspension route must document its real error responses.

``POST /api/v1/crm/customers/{customer_id}/suspend`` was published with only ``200``
and ``422`` - the operation's primary behaviour (Finance-only enforcement, 403) and
its two other reachable rejections (404 for an unknown/foreign customer, 409 for an
already-suspended one) were invisible to any consumer generating a client from the
contract.

This module asserts the semantics of the published operation, independently of the
byte-level snapshot guard in ``test_openapi_snapshot.py``. It needs no database: it
only inspects ``app.openapi()``, which is pure schema introspection (no TestClient, no
application lifespan, no connection).
"""

from app.main import app

SUSPEND_PATH = "/api/v1/crm/customers/{customer_id}/suspend"

#: Every status the handler can actually return: the 200 response model, the
#: Finance-only 403, the tenant-scoped 404, the already-suspended 409, and FastAPI's
#: request-validation 422.
EXPECTED_STATUSES = {"200", "403", "404", "409", "422"}

#: Statuses documented with the shared ``{"error": {...}}`` envelope from
#: ``app.core.exceptions.error_body``.
ENVELOPE_STATUSES = ("403", "404", "409")


def _operation() -> dict:
    schema = app.openapi()
    assert SUSPEND_PATH in schema["paths"], f"{SUSPEND_PATH} missing from the schema"
    assert "post" in schema["paths"][SUSPEND_PATH]
    return schema["paths"][SUSPEND_PATH]["post"]


def _schema_ref(response: dict) -> str:
    return response["content"]["application/json"]["schema"]["$ref"]


def test_suspend_operation_documents_every_reachable_status() -> None:
    """The documented status set must equal the set the handler can return."""
    responses = _operation()["responses"]
    assert set(responses) == EXPECTED_STATUSES, sorted(responses)


def test_suspend_operation_keeps_its_success_contract() -> None:
    """``200`` must stay the existing ``CustomerResponse`` and ``422`` the validation one."""
    responses = _operation()["responses"]
    assert _schema_ref(responses["200"]) == "#/components/schemas/CustomerResponse"
    assert _schema_ref(responses["422"]) == "#/components/schemas/HTTPValidationError"


def test_suspend_error_responses_use_the_shared_error_envelope() -> None:
    """403/404/409 must reference the real runtime envelope and explain themselves."""
    responses = _operation()["responses"]
    for status_code in ENVELOPE_STATUSES:
        response = responses[status_code]
        assert _schema_ref(response) == "#/components/schemas/ErrorResponse", status_code
        assert response.get("description", "").strip(), (
            f"{status_code} has no description"
        )


def test_error_envelope_schema_matches_error_body() -> None:
    """The documented envelope must mirror ``app.core.exceptions.error_body`` exactly."""
    schemas = app.openapi()["components"]["schemas"]
    assert "ErrorResponse" in schemas, "ErrorResponse is not published"
    assert schemas["ErrorResponse"]["properties"]["error"]["$ref"] == (
        "#/components/schemas/ErrorDetail"
    )

    detail = schemas["ErrorDetail"]
    assert set(detail["properties"]) == {
        "code",
        "message",
        "req_id",
        "details",
        "request_id",
    }
    # ``error_body`` always sets these two; the rest may be null/empty.
    assert set(detail["required"]) == {"code", "message"}
