from typing import Annotated



from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session



from app.core.deps import CurrentUser, get_current_user

from app.core.exceptions import AppError, http_error_from_app

from app.db.session import get_db

from app.schemas.pf.branding import TenantBrandingResponse, TenantLogoUpload, TenantPrimaryColorUpdate

from app.services.pf.branding_service import BrandingService



router = APIRouter(prefix="/tenant/branding", tags=["PF Branding"])





@router.get("", response_model=TenantBrandingResponse)

def get_tenant_branding(

    current: Annotated[CurrentUser, Depends(get_current_user)],

    db: Annotated[Session, Depends(get_db)],

) -> TenantBrandingResponse:

    try:

        return BrandingService(db).get_branding(current.tenant_id)

    except AppError as exc:

        raise http_error_from_app(exc) from exc





@router.put("/logo", response_model=TenantBrandingResponse)

def upload_tenant_logo(

    payload: TenantLogoUpload,

    current: Annotated[CurrentUser, Depends(get_current_user)],

    db: Annotated[Session, Depends(get_db)],

) -> TenantBrandingResponse:

    try:

        return BrandingService(db).upload_logo(

            current.tenant_id, payload, current.permissions

        )

    except AppError as exc:

        raise http_error_from_app(exc) from exc





@router.put("/primary-color", response_model=TenantBrandingResponse)

def update_primary_color(

    payload: TenantPrimaryColorUpdate,

    current: Annotated[CurrentUser, Depends(get_current_user)],

    db: Annotated[Session, Depends(get_db)],

) -> TenantBrandingResponse:

    try:

        return BrandingService(db).update_primary_color(

            current.tenant_id, payload, current.permissions

        )

    except AppError as exc:

        raise http_error_from_app(exc) from exc

