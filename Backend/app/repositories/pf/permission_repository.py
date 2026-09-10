from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pf import Permission, RolePermission


def permissions_for_role(db: Session, role_id: UUID) -> frozenset[str]:
    rows = db.scalars(
        select(Permission.permission_code)
        .join(RolePermission, RolePermission.permission_id == Permission.permission_id)
        .where(RolePermission.role_id == role_id)
    ).all()
    return frozenset(rows)
