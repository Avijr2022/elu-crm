from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


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


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
