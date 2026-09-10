import base64
import binascii
import re
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import AppError, ForbiddenError
from app.models.pf import TenantBranding
from app.repositories.pf.branding_repository import TenantBrandingRepository
from app.schemas.pf.branding import TenantBrandingResponse, TenantLogoUpload, TenantPrimaryColorUpdate

_LOGO_PATTERN = re.compile(
    r"^data:image/(jpeg|png);base64,([A-Za-z0-9+/=\s]+)$",
    re.IGNORECASE,
)
_MAX_LOGO_BYTES = 2 * 1024 * 1024


class BrandingService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = TenantBrandingRepository(db)

    def get_branding(self, tenant_id: UUID) -> TenantBrandingResponse:
        row = self.repo.get_by_tenant(tenant_id)
        if row is None:
            return TenantBrandingResponse(tenant_id=tenant_id)
        return TenantBrandingResponse.model_validate(row)

    def upload_logo(
        self,
        tenant_id: UUID,
        payload: TenantLogoUpload,
        permissions: frozenset[str],
    ) -> TenantBrandingResponse:
        if "tenant.update" not in permissions:
            raise ForbiddenError("Missing permission 'tenant.update'", req_id="REQ-PF-RBAC")
        match = _LOGO_PATTERN.match(payload.logo_data_url.strip())
        if not match:
            raise AppError(
                "VALIDATION_ERROR",
                "logo_data_url must be data:image/jpeg;base64,... or data:image/png;base64,...",
                422,
                req_id="REQ-PF-BRAND-001",
            )
        try:
            raw = base64.b64decode(match.group(2), validate=True)
        except (ValueError, binascii.Error) as exc:
            raise AppError(
                "VALIDATION_ERROR",
                "Invalid base64 in logo_data_url",
                422,
                req_id="REQ-PF-BRAND-002",
            ) from exc
        if len(raw) > _MAX_LOGO_BYTES:
            raise AppError(
                "VALIDATION_ERROR",
                "Logo exceeds 2 MB limit",
                422,
                req_id="REQ-PF-BRAND-003",
            )
        logo_url = f"data:image/{match.group(1).lower()};base64,{match.group(2).strip()}"
        row = self.repo.get_by_tenant(tenant_id)
        if row is None:
            row = TenantBranding(
                branding_id=uuid4(),
                tenant_id=tenant_id,
                logo_url=logo_url,
            )
            self.db.add(row)
        else:
            row.logo_url = logo_url
        self.db.commit()
        self.db.refresh(row)
        return TenantBrandingResponse.model_validate(row)

    def update_primary_color(
        self,
        tenant_id: UUID,
        payload: TenantPrimaryColorUpdate,
        permissions: frozenset[str],
    ) -> TenantBrandingResponse:
        if "tenant.update" not in permissions:
            raise ForbiddenError("Missing permission 'tenant.update'", req_id="REQ-PF-RBAC")
        color = payload.primary_color.strip()
        if not re.match(r"^#[0-9A-Fa-f]{6}$", color):
            raise AppError(
                "VALIDATION_ERROR",
                "primary_color must be a hex value like #1565C0",
                422,
                req_id="REQ-PF-BRAND-004",
            )
        row = self.repo.get_by_tenant(tenant_id)
        if row is None:
            row = TenantBranding(
                branding_id=uuid4(),
                tenant_id=tenant_id,
                primary_color=color,
            )
            self.db.add(row)
        else:
            row.primary_color = color
        self.db.commit()
        self.db.refresh(row)
        return TenantBrandingResponse.model_validate(row)
