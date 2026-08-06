from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.rls_context import clear_rls_context, register_rls_session_listener


def _resolve_database_url() -> str:
    settings = get_settings()
    # .env ships DATABASE_URL for in-compose use (@postgres). Prefer HOST URL on the Windows/macOS host.
    if settings.database_url_host and "@postgres:" in settings.database_url:
        return settings.database_url_host
    return settings.database_url


engine = create_engine(
    _resolve_database_url(),
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)
register_rls_session_listener()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    clear_rls_context(db)
    try:
        yield db
    finally:
        clear_rls_context(db)
        db.close()
