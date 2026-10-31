"""Shared pytest helpers for RLS-aware DB access (PF-003A / ADR-015)."""

import os
from contextlib import contextmanager
from collections.abc import Iterator

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal, _resolve_database_url
from app.models.pf import Tenant, User

PLATFORM_TENANT_CODE = "EIIP001"


@contextmanager
def platform_session() -> Iterator[Session]:
    """Open a Session with ``app.platform_context=true`` for setup/assertions."""
    db = SessionLocal()
    try:
        bind_rls_context(db, platform=True)
        yield db
    finally:
        clear_rls_context(db)
        db.close()


def platform_admin_select():
    """Select the seeded platform admin **within the platform tenant** (EIIP001).

    ``core.users`` is unique on ``(tenant_id, email)`` (``uk_users_tenant_email``),
    and tenant provisioning seeds ``settings.seed_admin_email`` into *every* newly
    registered tenant. An email-only lookup can therefore return a foreign tenant's
    row: role/password setup then lands on the wrong tenant while the fixture still
    logs in with ``tenant_code="EIIP001"`` (-> 401 -> fixture error), and the
    resulting failed logins increment that tenant's ``failed_login_count``.
    Every test must resolve the administration account through this selector.
    """
    settings = get_settings()
    return (
        select(User)
        .join(Tenant, Tenant.tenant_id == User.tenant_id)
        .where(
            Tenant.tenant_code == PLATFORM_TENANT_CODE,
            User.email == settings.seed_admin_email.lower(),
        )
    )


# NOTE (2026-09-25): a module-scoped autouse fixture that normalised the platform
# admin's login state was DELIBERATELY REMOVED. It opened a platform_session()
# (which issues SET LOCAL ROLE elu_app) during module setup, i.e. BEFORE the app
# lifespan has run the bootstrap DDL that creates the elu_app role on a fresh
# database. In CI that made all 264 tests error with
# `DataError: (psycopg.errors.InvalidParameterValue) role "elu_app" does not exist`
# while passing locally, where the role already exists.
# Rule: keep conftest helpers side-effect free and DB-order-neutral - never touch the
# database outside a TestClient(app) context.


# ---------------------------------------------------------------- C4 isolation guard

DISPOSABLE_DB_SUFFIXES = ("_test", "_tests")
DISPOSABLE_DB_PREFIXES = ("test_", "tmp_")


def _target_database_name() -> str:
    """Database name the test session will talk to (never returns credentials)."""
    url = _resolve_database_url()
    tail = url.rsplit("/", 1)[-1]
    return tail.split("?", 1)[0]


def _is_disposable_database(name: str) -> bool:
    lowered = (name or "").lower()
    return lowered.endswith(DISPOSABLE_DB_SUFFIXES) or lowered.startswith(
        DISPOSABLE_DB_PREFIXES
    )


def pytest_runtest_setup(item):
    """Fail-closed isolation for tests that commit (C4 / REQ-CRM-028).

    Tests marked ``db_write`` create persistent users, overwrite password hashes and
    commit customers / history / audit rows. The suite talks to the database the
    application itself uses (single engine in ``app.db.session``), so such tests must
    never run against a shared development database by accident.

    This is a ``pytest_runtest_setup`` hook rather than a fixture on purpose: hook
    setup runs BEFORE any fixture for the test (including module/session-scoped
    ``TestClient`` fixtures), so a module-scoped ``client`` fixture can no longer be
    instantiated - and therefore the app lifespan (DDL + seed) can no longer start -
    before a shared database is rejected.

    Policy: a ``db_write`` test runs only when the configured database name looks
    disposable (``*_test`` / ``*_tests`` / ``test_*`` / ``tmp_*``). Otherwise it is
    skipped with an explicit reason. Set ``ELU_ALLOW_SHARED_DB_WRITE=1`` to override
    deliberately on a throwaway environment. Unmarked tests are untouched.
    """
    if item.get_closest_marker("db_write") is None:
        return
    if os.environ.get("ELU_ALLOW_SHARED_DB_WRITE") == "1":
        return
    database = _target_database_name()
    if not _is_disposable_database(database):
        pytest.skip(
            f"db_write test skipped: target database {database!r} is not disposable. "
            "Point DATABASE_URL at a *_test database (for example elinkup_test), or "
            "set ELU_ALLOW_SHARED_DB_WRITE=1 to override deliberately."
        )
