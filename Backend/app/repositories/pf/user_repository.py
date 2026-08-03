from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.pf import Role, Tenant, User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(
        self, email: str, tenant_id: UUID | None = None
    ) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.role),
                joinedload(User.tenant).joinedload(Tenant.settings),
                joinedload(User.tenant).joinedload(Tenant.edition),
                joinedload(User.organization),
            )
            .where(
                User.email == email.lower(),
                User.is_deleted.is_(False),
            )
        )
        if tenant_id is not None:
            stmt = stmt.where(User.tenant_id == tenant_id)
        return self.db.scalars(stmt).first()

    def get_by_id(self, user_id: UUID, tenant_id: UUID) -> User | None:
        stmt = (
            select(User)
            .options(
                joinedload(User.role),
                joinedload(User.tenant).joinedload(Tenant.settings),
                joinedload(User.organization),
            )
            .where(
                User.user_id == user_id,
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
            )
        )
        return self.db.scalars(stmt).first()


class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_code(self, tenant_code: str) -> Tenant | None:
        stmt = (
            select(Tenant)
            .options(joinedload(Tenant.edition), joinedload(Tenant.settings))
            .where(
                Tenant.tenant_code == tenant_code.upper(),
                Tenant.is_deleted.is_(False),
            )
        )
        return self.db.scalars(stmt).first()

    def get_by_id(self, tenant_id: UUID) -> Tenant | None:
        stmt = (
            select(Tenant)
            .options(joinedload(Tenant.edition), joinedload(Tenant.settings))
            .where(Tenant.tenant_id == tenant_id, Tenant.is_deleted.is_(False))
        )
        return self.db.scalars(stmt).first()


class RoleRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_code(self, tenant_id: UUID, role_code: str) -> Role | None:
        stmt = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.role_code == role_code,
            Role.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()
