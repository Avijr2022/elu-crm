from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from app.models.pf import Role, Tenant, User, UserInvite


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_email(
        self, email: str, tenant_id: UUID
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
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
            )
        )
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

    # --- PF-008 CORE (ELU-BFS-PF-008 §10) -------------------------------------
    _SORT_COLUMNS = {
        "name": (User.first_name, User.last_name),
        "display_name": (User.display_name,),
        "email": (User.email,),
        "status": (User.account_status,),
        "employee_code": (User.employee_code,),
        "last_login": (User.last_login,),
        "created_on": (User.created_on,),
    }

    def active_invite_holder_count(self, tenant_id: UUID) -> int:
        """Seat usage for BR-PF-052: ACTIVE + INVITED + LOCKED hold a seat."""
        stmt = (
            select(func.count())
            .select_from(User)
            .where(
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
                User.is_active.is_(True),
                User.account_status.in_(("ACTIVE", "INVITED", "LOCKED")),
            )
        )
        return int(self.db.scalar(stmt) or 0)

    def count_by_role_code(
        self, tenant_id: UUID, role_code: str, statuses: tuple[str, ...] = ("ACTIVE",)
    ) -> int:
        """Active holders of a role — used for the BR-PF-060 guard."""
        stmt = (
            select(func.count())
            .select_from(User)
            .join(Role, Role.role_id == User.role_id)
            .where(
                User.tenant_id == tenant_id,
                User.is_deleted.is_(False),
                User.is_active.is_(True),
                User.account_status.in_(statuses),
                Role.role_code == role_code,
            )
        )
        return int(self.db.scalar(stmt) or 0)

    def email_exists(
        self, tenant_id: UUID, email: str, exclude_user_id: UUID | None = None
    ) -> bool:
        """BR-PF-051 — email is unique within the tenant."""
        stmt = select(User.user_id).where(
            User.tenant_id == tenant_id,
            User.email == email.lower(),
            User.is_deleted.is_(False),
        )
        if exclude_user_id is not None:
            stmt = stmt.where(User.user_id != exclude_user_id)
        return self.db.scalars(stmt).first() is not None

    def _filters(
        self,
        tenant_id: UUID,
        *,
        status: str | None = None,
        role_id: UUID | None = None,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        business_unit_id: UUID | None = None,
        search: str | None = None,
    ) -> list:
        conditions = [User.tenant_id == tenant_id, User.is_deleted.is_(False)]
        if status:
            conditions.append(User.account_status == status)
        if role_id:
            conditions.append(User.role_id == role_id)
        if organization_id:
            conditions.append(User.organization_id == organization_id)
        if branch_id:
            conditions.append(User.branch_id == branch_id)
        if department_id:
            conditions.append(User.department_id == department_id)
        if business_unit_id:
            conditions.append(User.business_unit_id == business_unit_id)
        if search and search.strip():
            like = f"%{search.strip().lower()}%"
            conditions.append(
                or_(
                    func.lower(User.email).like(like),
                    func.lower(User.display_name).like(like),
                    func.lower(User.first_name).like(like),
                    func.lower(User.employee_code).like(like),
                )
            )
        return conditions

    def _order_by(self, sort: str | None) -> tuple:
        key = (sort or "created_on").strip()
        descending = key.startswith("-")
        key = key.lstrip("-") or "created_on"
        columns = self._SORT_COLUMNS.get(key, self._SORT_COLUMNS["created_on"])
        expressions = [col.desc() if descending else col.asc() for col in columns]
        return tuple(expressions) + (User.user_id.asc(),)

    def list_users(
        self,
        tenant_id: UUID,
        *,
        page: int = 1,
        page_size: int = 20,
        status: str | None = None,
        role_id: UUID | None = None,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        business_unit_id: UUID | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> tuple[list[User], int]:
        conditions = self._filters(
            tenant_id,
            status=status,
            role_id=role_id,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
        )
        total = int(
            self.db.scalar(select(func.count()).select_from(User).where(*conditions)) or 0
        )
        stmt = (
            select(User)
            .options(joinedload(User.role), joinedload(User.organization))
            .where(*conditions)
            .order_by(*self._order_by(sort))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.db.scalars(stmt).all()), total

    def list_for_export(
        self,
        tenant_id: UUID,
        *,
        status: str | None = None,
        role_id: UUID | None = None,
        organization_id: UUID | None = None,
        branch_id: UUID | None = None,
        department_id: UUID | None = None,
        business_unit_id: UUID | None = None,
        search: str | None = None,
        sort: str | None = None,
    ) -> list[User]:
        conditions = self._filters(
            tenant_id,
            status=status,
            role_id=role_id,
            organization_id=organization_id,
            branch_id=branch_id,
            department_id=department_id,
            business_unit_id=business_unit_id,
            search=search,
        )
        stmt = (
            select(User)
            .options(joinedload(User.role), joinedload(User.organization))
            .where(*conditions)
            .order_by(*self._order_by(sort))
        )
        return list(self.db.scalars(stmt).all())


class UserInviteRepository:
    """PF-008 invitation persistence (core.user_invite; D2)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_active_for_user(self, user_id: UUID) -> "UserInvite | None":
        stmt = select(UserInvite).where(
            UserInvite.user_id == user_id,
            UserInvite.status == "ACTIVE",
            UserInvite.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def get_by_token_hash(self, token_hash: str) -> "UserInvite | None":
        """Token activation is an auth-bootstrap read (platform RLS context, ADR-015)."""
        stmt = select(UserInvite).where(
            UserInvite.token_hash == token_hash,
            UserInvite.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()

    def add(self, invite: "UserInvite") -> "UserInvite":
        self.db.add(invite)
        self.db.flush()
        return invite



class TenantRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_code(self, tenant_code: str) -> Tenant | None:
        """Case-insensitive lookup (BR-PF-009 lowercase + legacy seed codes)."""
        code = tenant_code.strip()
        stmt = (
            select(Tenant)
            .options(joinedload(Tenant.edition), joinedload(Tenant.settings))
            .where(
                func.lower(Tenant.tenant_code) == code.lower(),
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

    def get_by_id(self, tenant_id: UUID, role_id: UUID) -> Role | None:
        """PF-008: resolve a role by id inside the tenant boundary (BR-PF-059)."""
        stmt = select(Role).where(
            Role.tenant_id == tenant_id,
            Role.role_id == role_id,
            Role.is_deleted.is_(False),
        )
        return self.db.scalars(stmt).first()
