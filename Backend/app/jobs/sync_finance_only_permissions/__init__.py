"""BR-CRM-047 / REQ-CRM-028 — ``customer.suspend`` backfill across ALL tenants.

``seed_platform`` only re-seeds the platform tenant (EIIP001) and the Community demo
tenant (COMU001). Tenants that predate the ``customer.suspend`` catalogue entry are
therefore never healed by startup seeding, which leaves two failure modes:

  * a tenant whose FINANCE_USER does not hold the grain (suspension always 403), and
  * a tenant whose TENANT_ADMIN / PLATFORM_ADMIN still hold it from the old
    whole-catalogue grant (BR-CRM-047 violated at grant level).

This module is the deliberate, operator-invoked all-tenants synchronization. It is
NOT wired into application startup, so it cannot perform a bulk write by accident.

Run::

    python -m app.jobs.sync_finance_only_permissions                      # dry run
    python -m app.jobs.sync_finance_only_permissions --apply               # write
    python -m app.jobs.sync_finance_only_permissions --apply --tenant EIIP001

The work is delegated to ``app.db.seed.sync_finance_only_permissions``, which reuses
the existing tenant-scoped seed helpers (``_grant_role_permissions`` and
``_revoke_permission_from_other_roles``). The operation is idempotent: a second run
reports zero tenants changed.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.seed import sync_finance_only_permissions
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class FinanceOnlySyncResult:
    """Summary of one synchronization run (changed and skipped are separate)."""

    apply: bool
    tenants_scanned: int
    tenants_changed: int
    tenants_eligible: int = 0
    tenants_skipped: int = 0
    skip_reasons: dict[str, int] = field(default_factory=dict)
    results: list[dict] = field(default_factory=list)


def run_sync_finance_only_permissions(
    *,
    apply: bool = False,
    tenant_codes: tuple[str, ...] | None = None,
    db: Session | None = None,
) -> FinanceOnlySyncResult:
    """Synchronise ``customer.suspend`` to FINANCE_USER-only for every tenant.

    ``apply=False`` is a dry run and writes nothing. When a caller supplies ``db``,
    transaction control (commit/rollback) stays with the caller.

    Ineligible tenants (soft-deleted, inactive, not ``ACTIVE``/``TRIAL``, not
    provisioned, or without a ``FINANCE_USER`` role) are reported under
    ``skip_reasons`` and are never written to, in either mode.
    """
    owns_session = db is None
    session = db or SessionLocal()
    try:
        bind_rls_context(session, platform=True)
        summary = sync_finance_only_permissions(
            session, tenant_codes=tenant_codes, apply=apply
        )
        if owns_session:
            if apply:
                session.commit()
            else:
                session.rollback()
        logger.info(
            "customer.suspend sync apply=%s tenants_scanned=%s tenants_eligible=%s "
            "tenants_changed=%s tenants_skipped=%s skip_reasons=%s",
            summary["apply"],
            summary["tenants_scanned"],
            summary["tenants_eligible"],
            summary["tenants_changed"],
            summary["tenants_skipped"],
            summary["skip_reasons"],
        )
        return FinanceOnlySyncResult(
            apply=bool(summary["apply"]),
            tenants_scanned=int(summary["tenants_scanned"]),
            tenants_changed=int(summary["tenants_changed"]),
            tenants_eligible=int(summary["tenants_eligible"]),
            tenants_skipped=int(summary["tenants_skipped"]),
            skip_reasons=dict(summary["skip_reasons"]),
            results=summary["results"],
        )
    finally:
        clear_rls_context(session)
        if owns_session:
            session.close()
