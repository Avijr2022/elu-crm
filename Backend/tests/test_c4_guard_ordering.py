"""C4 ordering proof: the guard must run before ANY fixture is set up (REQ-CRM-028).

The ``db_write`` guard lives in ``conftest.pytest_runtest_setup``, which pytest
invokes before it sets up fixtures for the test - including module-scoped ones. To
prove that ordering, the module-scoped fixture below writes a sentinel file at exactly
the point where a module-scoped ``TestClient(app)`` would start the application
lifespan (schema DDL + seed).

* Shared database: the hook skips the test, the module-scoped fixture never runs and
  the sentinel is never created.
* Disposable database: the test runs and the fixture must already have run.

The sentinel location is supplied through ``C4_GUARD_SENTINEL``; when it is unset the
fixture is inert and the test skips.
"""

import os

import pytest

SENTINEL_ENV = "C4_GUARD_SENTINEL"
SENTINEL_PATH = os.environ.get(SENTINEL_ENV, "")


@pytest.fixture(scope="module", autouse=True)
def module_scoped_probe():
    """Stand-in for a module-scoped ``TestClient`` fixture."""
    if SENTINEL_PATH:
        with open(SENTINEL_PATH, "w", encoding="utf-8") as handle:
            handle.write("module-scoped fixture started")
    yield


@pytest.mark.db_write
def test_guard_runs_before_module_scoped_fixtures():
    """Reachable only on a disposable database - and then the fixture has run."""
    if not SENTINEL_PATH:
        pytest.skip("C4_GUARD_SENTINEL not set - ordering probe needs the caller")
    assert os.path.exists(SENTINEL_PATH), (
        "module-scoped fixture did not run - guard/fixture ordering changed"
    )
