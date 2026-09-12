"""Edition feature gating (ELU-EDM-001)."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.exceptions import ForbiddenError
from app.models.pf import Edition, Tenant

CRM_LEAD = "CRM_LEAD"
CRM_OPPORTUNITY = "CRM_OPPORTUNITY"
CRM_CUSTOMER = "CRM_CUSTOMER"
CRM_ACTIVITY = "CRM_ACTIVITY"
SAL_QUOTE = "SAL_QUOTE"
PRJ_WO = "PRJ_WO"
FIN_INVOICE = "FIN_INVOICE"
BRANCH = "BRANCH"  # PF-005 (ELU-BFS-PF-005 BR-PF-034; ELU-EDM-001)


def enabled_features(db: Session, tenant_id: UUID) -> frozenset[str]:
    tenant = db.scalars(
        select(Tenant)
        .options(joinedload(Tenant.edition).joinedload(Edition.features))
        .where(Tenant.tenant_id == tenant_id, Tenant.is_deleted.is_(False))
    ).first()
    if tenant is None or tenant.edition is None:
        return frozenset()
    return frozenset(
        f.feature_code for f in tenant.edition.features if f.is_enabled
    )


def has_feature(db: Session, tenant_id: UUID, feature_code: str) -> bool:
    return feature_code in enabled_features(db, tenant_id)


def require_feature(db: Session, tenant_id: UUID, feature_code: str) -> None:
    if not has_feature(db, tenant_id, feature_code):
        raise ForbiddenError(
            f"Edition feature '{feature_code}' is not enabled for this tenant",
            req_id="REQ-EDM-001",
        )
