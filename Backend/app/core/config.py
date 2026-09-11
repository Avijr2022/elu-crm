from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env", "../.env.example"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "E-LinkUp"
    app_env: str = "local"
    api_v1_prefix: str = "/api/v1"

    # Host-run default (Docker maps Postgres to localhost:55432).
    # Inside Compose, set DATABASE_URL=...@postgres:5432/elinkup.
    database_url: str = (
        "postgresql+psycopg://elinkup:elinkup_local@localhost:55432/elinkup"
    )
    database_url_host: str | None = None

    jwt_secret_key: str = "change-me-elinkup-dev-secret-key-min-32-chars"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    cors_origins: str = (
        "http://localhost:8080,http://127.0.0.1:8080,http://localhost:3000,"
        "http://localhost:8085,http://127.0.0.1:8085,http://[::1]:8080,http://[::1]:8085"
    )

    default_currency: str = "INR"
    default_timezone: str = "Asia/Kolkata"
    default_fy_start_month: int = 4
    default_fy_start_day: int = 1
    default_locale: str = "en_IN"
    default_language: str = "en"
    default_date_format: str = "dd/MM/yyyy"

    seed_admin_email: str = "admin@euphoriainfotech.com"
    seed_admin_password: str = "Admin@12345"

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
