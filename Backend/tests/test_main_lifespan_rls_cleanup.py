"""Startup RLS-context cleanup in ``app.main.lifespan``.

The bootstrap block disables the ``elu_app`` role switch and binds a platform RLS
context so migrations/seed run as the owner. That binding MUST be undone in the
``finally`` block, otherwise a failed startup leaks two things into every later
session of the process:

* ``set_app_role_enabled(False)`` leaves the ``_app_role_cv`` ContextVar False, so
  request sessions would never issue ``SET LOCAL ROLE elu_app`` (RLS bypassed);
* ``bind_rls_context(platform=True)`` leaves ``Session.info`` carrying a platform
  context, so new sessions would read across tenants.

These tests drive ``lifespan`` with a fake engine and a fake session: no database,
no ``db_write`` marker and no disposable-database guard needed.
"""

import asyncio
from contextlib import contextmanager
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI

import app.main as main_module
from app.db import rls_context
from app.db.rls_context import app_role_enabled, set_app_role_enabled

#: Bootstrap DDL steps, in the order ``app.main.lifespan`` imports/calls them.
_BOOTSTRAP_STEPS: tuple[tuple[str, str], ...] = (
    ("app.db.migrate_pf001", "apply_pf001_ddl"),
    ("app.db.migrate_pf002", "apply_pf002_ddl"),
    ("app.db.migrate_pf003", "apply_pf003_ddl"),
    ("app.db.migrate_pf004", "apply_pf004_ddl"),
    ("app.db.migrate_pf005", "apply_pf005_ddl"),
    ("app.db.migrate_pf006", "apply_pf006_ddl"),
    ("app.db.migrate_pf007", "apply_pf007_ddl"),
    ("app.db.migrate_pf008", "apply_pf008_ddl"),
    ("app.db.migrate_pf009", "apply_pf009_ddl"),
    ("app.db.migrate_pf010", "apply_pf010_ddl"),
    ("app.db.migrate_pf011", "apply_pf011_ddl"),
    ("app.db.migrate_crm", "apply_crm_ddl"),
    ("app.db.migrate_sal", "apply_sal_ddl"),
    ("app.db.migrate_fin", "apply_fin_ddl"),
    ("app.db.migrate_prj", "apply_prj_ddl"),
)


@contextmanager
def _fake_begin():
    yield MagicMock()


class _FakeEngine:
    """Stands in for ``app.db.session.engine`` so no connection is opened."""

    def begin(self):
        return _fake_begin()


@pytest.fixture(autouse=True)
def _restore_app_role() -> None:
    """Never let a failing assertion leave the global role flag disabled."""
    yield
    set_app_role_enabled(True)


@pytest.mark.parametrize(
    "failure_point",
    ["first_migration", "last_migration", "seed"],
)
def test_lifespan_clears_rls_context_and_closes_session_on_failure(
    monkeypatch: pytest.MonkeyPatch, failure_point: str
) -> None:
    events: list[str] = []

    fake_db = MagicMock()
    fake_db.info = {}
    fake_db.close.side_effect = lambda: events.append("close")

    monkeypatch.setattr(main_module, "engine", _FakeEngine())
    monkeypatch.setattr(main_module.Base.metadata, "create_all", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "SessionLocal", lambda: fake_db)

    real_bind = rls_context.bind_rls_context
    real_clear = rls_context.clear_rls_context

    def spy_bind(db, **kwargs):
        events.append("bind")
        return real_bind(db, **kwargs)

    def spy_clear(db=None):
        events.append("clear")
        assert db is fake_db, "cleanup must target the bootstrap session"
        return real_clear(db)

    # ``lifespan`` imports these names at call time, so module attributes are used.
    monkeypatch.setattr(rls_context, "bind_rls_context", spy_bind)
    monkeypatch.setattr(rls_context, "clear_rls_context", spy_clear)

    for module_name, func_name in _BOOTSTRAP_STEPS:
        monkeypatch.setattr(f"{module_name}.{func_name}", lambda db: None)
    monkeypatch.setattr("app.db.migrate_pf009.backfill_user_role", lambda db: None)

    def boom(db=None):
        events.append("boom")
        raise RuntimeError("bootstrap boom")

    if failure_point == "first_migration":
        monkeypatch.setattr("app.db.migrate_pf001.apply_pf001_ddl", boom)
    elif failure_point == "last_migration":
        monkeypatch.setattr("app.db.migrate_prj.apply_prj_ddl", boom)
    else:
        monkeypatch.setattr(main_module, "seed_platform", boom)

    async def _enter_lifespan() -> None:
        contexts = main_module.lifespan(FastAPI())
        with pytest.raises(RuntimeError, match="bootstrap boom"):
            await contexts.__aenter__()

    asyncio.run(_enter_lifespan())

    assert events == ["bind", "boom", "clear", "close"], events
    assert fake_db.close.called, "bootstrap session must always be closed"
    assert app_role_enabled() is True, (
        "elu_app role switch must be restored after a failed startup"
    )
    assert fake_db.info == {"elu_tenant_id": None, "elu_platform": False}, (
        "platform RLS context must not survive a failed startup"
    )


def test_lifespan_clears_rls_context_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The happy path keeps the same ordering: cleanup, then close, then yield."""
    events: list[str] = []

    fake_db = MagicMock()
    fake_db.info = {}
    fake_db.close.side_effect = lambda: events.append("close")

    monkeypatch.setattr(main_module, "engine", _FakeEngine())
    monkeypatch.setattr(main_module.Base.metadata, "create_all", lambda *a, **k: None)
    monkeypatch.setattr(main_module, "SessionLocal", lambda: fake_db)

    real_clear = rls_context.clear_rls_context

    def spy_clear(db=None):
        events.append("clear")
        return real_clear(db)

    monkeypatch.setattr(rls_context, "clear_rls_context", spy_clear)

    for module_name, func_name in _BOOTSTRAP_STEPS:
        monkeypatch.setattr(f"{module_name}.{func_name}", lambda db: None)
    monkeypatch.setattr(main_module, "seed_platform", lambda db: None)
    monkeypatch.setattr("app.db.migrate_pf009.backfill_user_role", lambda db: None)

    async def _run_lifespan() -> None:
        contexts = main_module.lifespan(FastAPI())
        await contexts.__aenter__()
        events.append("yield")
        await contexts.__aexit__(None, None, None)

    asyncio.run(_run_lifespan())

    assert events == ["clear", "close", "yield"], (
        "cleanup and close must happen before the application starts serving"
    )
    assert app_role_enabled() is True
    assert fake_db.info == {"elu_tenant_id": None, "elu_platform": False}
