import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    ValidationAppError,
)
from app.models.pf import Edition, EditionFeature, EditionLimit, EditionVersion
from app.repositories.pf.edition_repository import EditionRepository
from app.schemas.pf.edition import (
    EditionCreate,
    EditionDeprecateRequest,
    EditionFeatureOut,
    EditionLimitOut,
    EditionListResponse,
    EditionPatch,
    EditionPublishRequest,
    EditionResponse,
    EditionUpdate,
    EditionVersionOut,
)

# Community baseline (ELU-EDM-001 / BR-PF-006)
COMMUNITY_BASELINES = {
    "MAX_USERS": Decimal("5"),
    "MAX_STORAGE_GB": Decimal("5"),
    "MAX_ROLES": Decimal("5"),
}

ENTERPRISE_REQUIRED_FEATURES = {"SSO", "AUDIT_RETENTION_7Y"}


class EditionService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = EditionRepository(db)

    def _to_response(self, edition: Edition) -> EditionResponse:
        feature_names: dict[str, tuple[str, str]] = {}
        for f in edition.features:
            cat = self.repo.get_feature_catalogue(f.feature_code)
            if cat:
                feature_names[f.feature_code] = (cat.feature_name, cat.module_domain)

        return EditionResponse(
            id=edition.edition_id,
            code=edition.edition_code,
            name=edition.edition_name,
            description=edition.description,
            status=edition.status,
            version_no=edition.version_no,
            effective_from=edition.effective_from,
            effective_to=edition.effective_to,
            list_price_monthly=edition.list_price_monthly,
            list_price_annual=edition.list_price_annual,
            currency_code=edition.currency_code,
            display_order=edition.display_order,
            published_at=edition.published_at,
            published_by=edition.published_by,
            end_of_sale_date=edition.end_of_sale_date,
            features=[
                EditionFeatureOut(
                    id=f.id,
                    feature_code=f.feature_code,
                    is_enabled=f.is_enabled,
                    is_visible=f.is_visible,
                    feature_name=feature_names.get(f.feature_code, (None, None))[0],
                    module_domain=feature_names.get(f.feature_code, (None, None))[1],
                )
                for f in edition.features
            ],
            limits=[
                EditionLimitOut(
                    id=lim.id,
                    limit_code=lim.limit_code,
                    limit_name=lim.limit_name,
                    limit_value=lim.limit_value,
                    limit_unit=lim.limit_unit,
                    is_hard_limit=lim.is_hard_limit,
                    grace_percent=lim.grace_percent,
                )
                for lim in edition.limits
            ],
            created_on=edition.created_on,
            modified_on=edition.modified_on,
        )

    def _check_lock(self, edition: Edition, version_no: int) -> None:
        if edition.version_no != version_no:
            raise ConflictError(
                "Edition version conflict",
                req_id="BR-PF-004",
                details={"expected": edition.version_no, "provided": version_no},
            )

    def _validate_features_exist(self, feature_codes: list[str]) -> None:
        for code in feature_codes:
            if self.repo.get_feature_catalogue(code) is None:
                raise ValidationAppError(
                    f"Unknown feature_code: {code}",
                    req_id="BR-PF-001",
                )

    def _validate_limits_vs_community(self, limits: list) -> None:
        by_code = {lim.limit_code.upper(): lim.limit_value for lim in limits}
        for code, baseline in COMMUNITY_BASELINES.items():
            if code in by_code and by_code[code] < baseline:
                raise ValidationAppError(
                    f"Limit {code} must be ≥ Community baseline {baseline}",
                    req_id="BR-PF-006",
                )

    def _validate_enterprise(self, code: str, feature_codes: set[str]) -> None:
        if code != "ENTERPRISE":
            return
        missing = ENTERPRISE_REQUIRED_FEATURES - feature_codes
        if missing:
            raise ValidationAppError(
                f"ENTERPRISE requires features: {', '.join(sorted(missing))}",
                req_id="BR-PF-007",
            )

    def _snapshot(self, edition: Edition) -> str:
        return json.dumps(
            {
                "code": edition.edition_code,
                "name": edition.edition_name,
                "status": edition.status,
                "version_no": edition.version_no,
                "features": [
                    {
                        "feature_code": f.feature_code,
                        "is_enabled": f.is_enabled,
                        "is_visible": f.is_visible,
                    }
                    for f in edition.features
                ],
                "limits": [
                    {
                        "limit_code": lim.limit_code,
                        "limit_value": str(lim.limit_value),
                    }
                    for lim in edition.limits
                ],
            },
            default=str,
        )

    def list_editions(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> EditionListResponse:
        items, total = self.repo.list(
            page=page, page_size=page_size, status=status, search=search
        )
        return EditionListResponse(
            items=[self._to_response(e) for e in items],
            page=page,
            page_size=page_size,
            total=total,
        )

    def get_edition(self, edition_id: UUID) -> EditionResponse:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        return self._to_response(edition)

    def get_by_code(self, code: str) -> EditionResponse:
        edition = self.repo.get_by_code(code)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        return self._to_response(edition)

    def create(self, payload: EditionCreate, actor_id: UUID) -> EditionResponse:
        if self.repo.get_by_code(payload.code):
            raise ConflictError(
                f"Edition code {payload.code} already exists",
                req_id="BR-PF-001",
            )
        self._validate_features_exist([f.feature_code for f in payload.features])
        self._validate_limits_vs_community(payload.limits)
        self._validate_enterprise(
            payload.code, {f.feature_code.upper() for f in payload.features if f.is_enabled}
        )

        edition = Edition(
            edition_id=uuid4(),
            edition_code=payload.code,
            edition_name=payload.name,
            description=payload.description,
            status="DRAFT",
            display_order=payload.display_order or 0,
            effective_from=payload.effective_from,
            effective_to=payload.effective_to,
            list_price_monthly=payload.list_price_monthly,
            list_price_annual=payload.list_price_annual,
            currency_code=payload.currency_code or "INR",
            created_by=actor_id,
            version_no=1,
        )
        for f in payload.features:
            edition.features.append(
                EditionFeature(
                    id=uuid4(),
                    feature_code=f.feature_code.upper(),
                    is_enabled=f.is_enabled,
                    is_visible=f.is_visible,
                )
            )
        for lim in payload.limits:
            edition.limits.append(
                EditionLimit(
                    id=uuid4(),
                    limit_code=lim.limit_code.upper(),
                    limit_name=lim.limit_name,
                    limit_value=lim.limit_value,
                    limit_unit=lim.limit_unit,
                    is_hard_limit=lim.is_hard_limit,
                    grace_percent=lim.grace_percent or Decimal("0"),
                )
            )
            if lim.limit_code.upper() == "MAX_USERS":
                edition.max_users = int(lim.limit_value) if lim.limit_value >= 0 else None

        self.repo.add(edition)
        self.db.commit()
        self.db.refresh(edition)
        return self._to_response(self.repo.get_by_id(edition.edition_id))  # type: ignore[arg-type]

    def update(
        self, edition_id: UUID, payload: EditionUpdate, actor_id: UUID
    ) -> EditionResponse:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        self._check_lock(edition, payload.version_no)
        if edition.status not in ("DRAFT",):
            # ACTIVE matrix changes require version bump (BR-PF-004)
            if edition.status != "ACTIVE":
                raise ValidationAppError(
                    f"Cannot full-update edition in status {edition.status}",
                    req_id="BR-PF-004",
                )

        if payload.name is not None:
            edition.edition_name = payload.name
        if payload.description is not None:
            edition.description = payload.description
        if payload.display_order is not None:
            edition.display_order = payload.display_order
        if payload.effective_from is not None:
            edition.effective_from = payload.effective_from
        if payload.effective_to is not None:
            edition.effective_to = payload.effective_to
        if payload.list_price_monthly is not None:
            edition.list_price_monthly = payload.list_price_monthly
        if payload.list_price_annual is not None:
            edition.list_price_annual = payload.list_price_annual
        if payload.currency_code is not None:
            edition.currency_code = payload.currency_code

        if payload.features is not None:
            self._validate_features_exist([f.feature_code for f in payload.features])
            enabled = {f.feature_code.upper() for f in payload.features if f.is_enabled}
            self._validate_enterprise(edition.edition_code, enabled)
            rows = [
                EditionFeature(
                    id=uuid4(),
                    feature_code=f.feature_code.upper(),
                    is_enabled=f.is_enabled,
                    is_visible=f.is_visible,
                )
                for f in payload.features
            ]
            self.repo.replace_features(edition, rows)

        if payload.limits is not None:
            self._validate_limits_vs_community(payload.limits)
            rows = [
                EditionLimit(
                    id=uuid4(),
                    limit_code=lim.limit_code.upper(),
                    limit_name=lim.limit_name,
                    limit_value=lim.limit_value,
                    limit_unit=lim.limit_unit,
                    is_hard_limit=lim.is_hard_limit,
                    grace_percent=lim.grace_percent or Decimal("0"),
                )
                for lim in payload.limits
            ]
            self.repo.replace_limits(edition, rows)
            for lim in rows:
                if lim.limit_code == "MAX_USERS":
                    edition.max_users = int(lim.limit_value)

        if edition.status == "ACTIVE":
            self.db.add(
                EditionVersion(
                    id=uuid4(),
                    edition_id=edition.edition_id,
                    version_no=edition.version_no,
                    snapshot_json=self._snapshot(edition),
                    change_summary="Feature/limit update on ACTIVE edition",
                    actor_id=actor_id,
                )
            )
            edition.version_no += 1
        else:
            edition.version_no += 1

        edition.modified_by = actor_id
        self.db.commit()
        return self._to_response(self.repo.get_by_id(edition_id))  # type: ignore[arg-type]

    def patch(
        self, edition_id: UUID, payload: EditionPatch, actor_id: UUID
    ) -> EditionResponse:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        self._check_lock(edition, payload.version_no)
        if payload.name is not None:
            edition.edition_name = payload.name
        if payload.description is not None:
            edition.description = payload.description
        if payload.display_order is not None:
            edition.display_order = payload.display_order
        if payload.end_of_sale_date is not None:
            edition.end_of_sale_date = payload.end_of_sale_date
        if payload.status is not None:
            raise ValidationAppError(
                "Use /publish or /deprecate for status transitions",
                req_id="PF-001",
            )
        edition.version_no += 1
        edition.modified_by = actor_id
        self.db.commit()
        return self._to_response(self.repo.get_by_id(edition_id))  # type: ignore[arg-type]

    def publish(
        self, edition_id: UUID, payload: EditionPublishRequest, actor_id: UUID
    ) -> EditionResponse:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        self._check_lock(edition, payload.version_no)
        if edition.status != "DRAFT":
            raise ValidationAppError(
                "Only DRAFT editions can be published",
                req_id="BR-PF-008",
            )
        if not edition.features or not edition.limits:
            raise ValidationAppError(
                "Publishing requires at least one feature and one limit row",
                req_id="BR-PF-008",
            )
        enabled = {f.feature_code for f in edition.features if f.is_enabled}
        self._validate_enterprise(edition.edition_code, enabled)

        # BR-PF-002: only one ACTIVE per code — same code unique so OK
        edition.status = "ACTIVE"
        edition.published_at = datetime.now(timezone.utc)
        edition.published_by = actor_id
        edition.version_no += 1
        edition.modified_by = actor_id
        self.db.add(
            EditionVersion(
                id=uuid4(),
                edition_id=edition.edition_id,
                version_no=edition.version_no,
                snapshot_json=self._snapshot(edition),
                change_summary="Published",
                actor_id=actor_id,
            )
        )
        self.db.commit()
        return self._to_response(self.repo.get_by_id(edition_id))  # type: ignore[arg-type]

    def deprecate(
        self, edition_id: UUID, payload: EditionDeprecateRequest, actor_id: UUID
    ) -> EditionResponse:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        self._check_lock(edition, payload.version_no)
        if edition.status != "ACTIVE":
            raise ValidationAppError(
                "Only ACTIVE editions can be deprecated",
                req_id="BR-PF-005",
            )
        edition.status = "DEPRECATED"
        edition.end_of_sale_date = payload.end_of_sale_date
        edition.version_no += 1
        edition.modified_by = actor_id
        self.db.add(
            EditionVersion(
                id=uuid4(),
                edition_id=edition.edition_id,
                version_no=edition.version_no,
                snapshot_json=self._snapshot(edition),
                change_summary=f"Deprecated: {payload.reason}",
                actor_id=actor_id,
            )
        )
        self.db.commit()
        return self._to_response(self.repo.get_by_id(edition_id))  # type: ignore[arg-type]

    def delete(self, edition_id: UUID, actor_id: UUID) -> None:
        edition = self.repo.get_by_id(edition_id)
        if edition is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        if self.repo.is_referenced(edition_id):
            raise ValidationAppError(
                "Edition cannot be deleted while referenced by tenant or subscription",
                req_id="BR-PF-003",
            )
        if edition.status == "DRAFT":
            edition.status = "CANCELLED"
            edition.is_deleted = True
            edition.is_active = False
        elif edition.status in ("DEPRECATED", "ACTIVE"):
            edition.status = "ARCHIVED"
        else:
            raise ValidationAppError(
                f"Cannot delete edition in status {edition.status}",
                req_id="PF-001",
            )
        edition.modified_by = actor_id
        edition.version_no += 1
        self.db.commit()

    def history(self, edition_id: UUID) -> list[EditionVersionOut]:
        if self.repo.get_by_id(edition_id) is None:
            raise NotFoundError("Edition not found", req_id="PF-001")
        return [
            EditionVersionOut.model_validate(v)
            for v in self.repo.list_versions(edition_id)
        ]

    def export_matrix(self) -> list[dict]:
        items, _ = self.repo.list(page=1, page_size=100)
        return [
            {
                "code": e.edition_code,
                "name": e.edition_name,
                "status": e.status,
                "features": [
                    {"code": f.feature_code, "enabled": f.is_enabled}
                    for f in e.features
                ],
                "limits": [
                    {"code": lim.limit_code, "value": str(lim.limit_value)}
                    for lim in e.limits
                ],
            }
            for e in items
        ]

    def tenant_edition(self, edition_id: UUID) -> EditionResponse:
        """Tenant Admin read of own edition (BR: read-only)."""
        return self.get_edition(edition_id)


def require_platform_admin(role_code: str) -> None:
    if role_code != "PLATFORM_ADMIN":
        raise ForbiddenError(
            "Platform Admin role required for edition management",
            req_id="PF-001",
        )
