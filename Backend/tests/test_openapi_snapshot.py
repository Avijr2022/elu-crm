"""OpenAPI snapshot drift guard (finding M3).

``Backend/openapi/openapi.json`` is the published API contract, yet nothing read
it: the PF-00x suites only fetch the *live* ``/openapi.json`` endpoint, and no CI
step ever compared the two.  The artefact therefore drifted silently - still
declaring ``info.version`` 0.5.0 / 39 paths / 50 schemas while the application
served 0.7.0 / 129 paths / 185 schemas - with the whole suite still green.

This module closes that gap. It rebuilds the document in-process and compares it
with the committed artefact, so the snapshot can no longer rot unnoticed.

Design constraints (all deliberate):

* No ``TestClient`` and no application ``lifespan``. ``app.openapi()`` is pure
  schema introspection, so the guard opens no PostgreSQL connection and mutates
  no database state. The engine in ``app.db.session`` is created lazily and is
  only ever touched by the lifespan.
* The snapshot path is derived from ``__file__``, never from the working
  directory, so the guard behaves identically however pytest is launched.
* Serialisation matches the artefact exactly: ``json.dumps(..., indent=2)`` with
  insertion order preserved, default ``ensure_ascii=True`` and no trailing newline.
  Only line endings and end-of-file newlines are normalised, because those depend
  on checkout/editor settings and cannot express contract drift.
"""

from __future__ import annotations

import difflib
import json
from pathlib import Path

import pytest

from app.main import app

# tests/test_openapi_snapshot.py -> tests -> Backend
BACKEND_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = BACKEND_ROOT / "openapi" / "openapi.json"

# How much of the unified diff to inline before truncating.
_DIFF_LINE_BUDGET = 40

_REGENERATE_HINT = (
    "Regenerate the committed artefact (review the diff before committing - it "
    "must be additive apart from genuine contract changes):\n"
    "  cd D:/CRM/Backend\n"
    "  $env:PYTHONPATH = 'D:/CRM/Backend'\n"
    "  ./.venv/Scripts/python.exe -c \"import json,pathlib; from app.main import app; "
    "pathlib.Path('openapi/openapi.json').write_text("
    "json.dumps(app.openapi(), indent=2), encoding='utf-8', newline='')\"\n"
    "  git -C D:/CRM diff --numstat -- Backend/openapi/openapi.json"
)


def _normalise(raw: bytes) -> bytes:
    """Strip checkout/editor artefacts that carry no contract meaning.

    The committed blob is LF, but a Windows clone without an ``.gitattributes``
    eol rule may place CRLF on disk, and editors add a trailing newline on save.
    ``json.dumps`` emits LF and no trailing newline, so normalising both sides
    keeps the comparison exact without producing false drift reports.
    """
    return raw.replace(b"\r\n", b"\n").rstrip(b"\n")


def _live_document() -> bytes:
    """Serialise the document exactly as the committed artefact is formatted."""
    return json.dumps(app.openapi(), indent=2).encode("utf-8")


def _shape(raw: bytes, label: str) -> str:
    """One-line summary of a document, for the failure report."""
    try:
        document = json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover - corrupt artefact
        return f"  {label}: not valid JSON ({exc})"
    info = document.get("info") or {}
    paths = document.get("paths") or {}
    schemas = ((document.get("components") or {}).get("schemas")) or {}
    return (
        f"  {label}: info.version={info.get('version')!r}, "
        f"paths={len(paths)}, schemas={len(schemas)}"
    )


def _drift_report(committed: bytes, live: bytes) -> str:
    """Build an actionable failure message describing the drift."""
    diff = list(
        difflib.unified_diff(
            committed.decode("utf-8").splitlines(),
            live.decode("utf-8").splitlines(),
            fromfile="Backend/openapi/openapi.json (committed snapshot)",
            tofile="app.openapi() (live application)",
            lineterm="",
            n=1,
        )
    )
    added = sum(
        1 for line in diff if line.startswith("+") and not line.startswith("+++")
    )
    removed = sum(
        1 for line in diff if line.startswith("-") and not line.startswith("---")
    )

    lines = [
        "OpenAPI snapshot is stale: Backend/openapi/openapi.json no longer matches",
        "the document the application serves.",
        "",
        _shape(committed, "committed snapshot"),
        _shape(live, "live application  "),
        f"  unified diff      : +{added} / -{removed} lines",
        "",
    ]

    shown = diff[:_DIFF_LINE_BUDGET]
    lines.extend(shown)
    if len(diff) > len(shown):
        lines.append(
            f"... {len(diff) - len(shown)} further diff lines suppressed "
            "(rerun `git diff` after regenerating for the full picture)."
        )

    lines.extend(["", _REGENERATE_HINT])
    return "\n".join(lines)


def test_openapi_snapshot_matches_live_document() -> None:
    """The committed artefact must match ``app.openapi()`` after line-ending
    normalisation."""
    if not SNAPSHOT_PATH.is_file():
        pytest.fail(
            f"OpenAPI snapshot missing at {SNAPSHOT_PATH}.\n\n{_REGENERATE_HINT}",
            pytrace=False,
        )

    committed = _normalise(SNAPSHOT_PATH.read_bytes())
    live = _normalise(_live_document())

    if committed == live:
        return

    pytest.fail(_drift_report(committed, live), pytrace=False)
