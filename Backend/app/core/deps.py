from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.db.rls_context import bind_rls_context
from app.db.session import get_db
from app.models.pf import User
from app.repositories.pf.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


@dataclass
class CurrentUser:
    user_id: UUID
    tenant_id: UUID
    email: str
    role_code: str
    role_id: UUID
    user: User
    platform_context: bool = False


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(bearer_scheme)
    ],
    db: Annotated[Session, Depends(get_db)],
) -> CurrentUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing bearer token", req_id="REQ-PF-051")
    try:
        payload = decode_token(credentials.credentials)
    except ValueError as exc:
        raise UnauthorizedError(str(exc), req_id="REQ-PF-051") from exc

    if payload.get("type") != "access":
        raise UnauthorizedError("Access token required", req_id="REQ-PF-051")

    user_id = UUID(payload["sub"])
    tenant_id = UUID(payload["tenant_id"])
    # ADR-015: bind JWT tenant before any repository read.
    bind_rls_context(db, tenant_id=tenant_id, platform=False)
    user = UserRepository(db).get_by_id(user_id, tenant_id)
    if user is None:
        raise UnauthorizedError("User not found", req_id="REQ-PF-051")

    platform = user.role.role_code == "PLATFORM_ADMIN"
    if platform:
        # Platform Admin bypass via app.platform_context (audited at API layer).
        bind_rls_context(db, tenant_id=tenant_id, platform=True)

    return CurrentUser(
        user_id=user.user_id,
        tenant_id=user.tenant_id,
        email=user.email,
        role_code=user.role.role_code,
        role_id=user.role.role_id,
        user=user,
        platform_context=platform,
    )
