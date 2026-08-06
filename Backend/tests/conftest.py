"""Shared pytest helpers for RLS-aware DB access (PF-003A / ADR-015)."""

from contextlib import contextmanager
from collections.abc import Iterator

from sqlalchemy.orm import Session

from app.db.rls_context import bind_rls_context, clear_rls_context
from app.db.session import SessionLocal


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
