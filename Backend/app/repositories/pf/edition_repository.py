from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.pf import Edition, EditionFeature, EditionLimit, EditionVersion, FeatureCatalogue


class EditionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_query(self):
        return select(Edition).options(
            selectinload(Edition.features),
            selectinload(Edition.limits),
        )

    def get_by_id(self, edition_id: UUID) -> Optional[Edition]:
        return self.db.scalars(
            self._base_query().where(Edition.id == edition_id)
        ).first()

    def get_by_code(self, code: str) -> Optional[Edition]:
        return self.db.scalars(
            self._base_query().where(Edition.code == code.upper())
        ).first()

    def list(
        self,
        *,
        page: int,
        page_size: int,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> tuple[list[Edition], int]:
        q = self._base_query()
        if status:
            q = q.where(Edition.status == status.upper())
        if search:
            like = f"%{search.strip()}%"
            q = q.where(
                or_(
                    Edition.code.ilike(like),
                    Edition.name.ilike(like),
                )
            )
        total = self.db.scalar(select(func.count()).select_from(q.subquery())) or 0
        items = list(
            self.db.scalars(
                q.order_by(Edition.display_order.asc().nulls_last(), Edition.code)
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )
        return items, int(total)

    def add(self, edition: Edition) -> Edition:
        self.db.add(edition)
        return edition

    def get_feature_catalogue(self, code: str) -> Optional[FeatureCatalogue]:
        return self.db.scalars(
            select(FeatureCatalogue).where(
                FeatureCatalogue.feature_code == code,
                FeatureCatalogue.is_deleted.is_(False),
            )
        ).first()

    def list_versions(self, edition_id: UUID) -> list[EditionVersion]:
        return list(
            self.db.scalars(
                select(EditionVersion)
                .where(EditionVersion.edition_id == edition_id)
                .order_by(EditionVersion.version_no.desc())
            ).all()
        )

    def is_referenced(self, edition_id: UUID) -> bool:
        from app.models.pf import Subscription, Tenant

        tenant_ref = self.db.scalar(
            select(func.count())
            .select_from(Tenant)
            .where(Tenant.edition_id == edition_id, Tenant.is_deleted.is_(False))
        )
        sub_ref = self.db.scalar(
            select(func.count())
            .select_from(Subscription)
            .where(
                Subscription.edition_id == edition_id,
                Subscription.is_deleted.is_(False),
            )
        )
        return bool(tenant_ref or sub_ref)

    def replace_features(
        self, edition: Edition, rows: list[EditionFeature]
    ) -> None:
        edition.features.clear()
        self.db.flush()
        for row in rows:
            edition.features.append(row)

    def replace_limits(self, edition: Edition, rows: list[EditionLimit]) -> None:
        edition.limits.clear()
        self.db.flush()
        for row in rows:
            edition.limits.append(row)
