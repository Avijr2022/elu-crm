from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.pf import TenantBranding


class TenantBrandingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_tenant(self, tenant_id: UUID) -> TenantBranding | None:
        return self.db.scalars(
            select(TenantBranding).where(
                TenantBranding.tenant_id == tenant_id,
                TenantBranding.is_deleted.is_(False),
            )
        ).first()
