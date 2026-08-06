from typing import Any, Optional

from fastapi import HTTPException, status


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        http_status: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[dict[str, Any]] = None,
        req_id: Optional[str] = None,
    ) -> None:
        self.code = code
        self.message = message
        self.http_status = http_status
        self.details = details or {}
        self.req_id = req_id
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", **kwargs: Any) -> None:
        super().__init__(
            code="NOT_FOUND",
            message=message,
            http_status=status.HTTP_404_NOT_FOUND,
            **kwargs,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", **kwargs: Any) -> None:
        super().__init__(
            code="UNAUTHORIZED",
            message=message,
            http_status=status.HTTP_401_UNAUTHORIZED,
            **kwargs,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", **kwargs: Any) -> None:
        super().__init__(
            code="FORBIDDEN",
            message=message,
            http_status=status.HTTP_403_FORBIDDEN,
            **kwargs,
        )


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", **kwargs: Any) -> None:
        super().__init__(
            code="CONFLICT",
            message=message,
            http_status=status.HTTP_409_CONFLICT,
            **kwargs,
        )


class ValidationAppError(AppError):
    def __init__(self, message: str = "Validation failed", **kwargs: Any) -> None:
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            **kwargs,
        )


def error_body(exc: AppError, request_id: Optional[str] = None) -> dict[str, Any]:
    return {
        "error": {
            "code": exc.code,
            "message": exc.message,
            "req_id": exc.req_id,
            "details": exc.details,
            "request_id": request_id,
        }
    }


def http_error_from_app(exc: AppError, request_id: Optional[str] = None) -> HTTPException:
    return HTTPException(
        status_code=exc.http_status,
        detail=error_body(exc, request_id),
    )
