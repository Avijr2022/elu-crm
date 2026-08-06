from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError, error_body
from app.core.logging import configure_logging
from app.db.base import Base
from app.db.seed import seed_platform
from app.db.session import SessionLocal, engine
from app.middleware.request_id import RequestIdMiddleware
from app.models import pf as _pf_models  # noqa: F401 — register models
from app.models import crm as _crm_models  # noqa: F401 — register CRM models
from app.schemas.pf.auth import HealthResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    # Create schemas + tables for local bootstrap
    with engine.begin() as conn:
        for schema in (
            "core",
            "master",
            "crm",
            "sales",
            "projects",
            "finance",
            "service",
            "integration",
            "shared",
            "audit",
        ):
            conn.exec_driver_sql(f"CREATE SCHEMA IF NOT EXISTS {schema}")
        Base.metadata.create_all(bind=conn)

    db = SessionLocal()
    try:
        seed_platform(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.3.0",
        description=(
            "E-LinkUp multi-tenant CRM/ERP API — PF-001 Edition Management + Auth + CRM"
        ),
        lifespan=lifespan,
        openapi_tags=[
            {"name": "Health", "description": "Liveness"},
            {"name": "Authentication", "description": "JWT login / refresh"},
            {
                "name": "PF-001 Editions",
                "description": "Edition catalogue, feature matrix, limits (ELU-BFS-PF-001)",
            },
            {"name": "CRM Leads", "description": "Lead management"},
            {"name": "CRM Opportunities", "description": "Opportunity pipeline"},
        ],
    )
    app.add_middleware(RequestIdMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.http_status,
            content=error_body(exc, request_id),
        )

    @app.get("/health", response_model=HealthResponse, tags=["Health"])
    def health() -> HealthResponse:
        return HealthResponse(
            status="ok", app=settings.app_name, env=settings.app_env
        )

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app


app = create_app()
