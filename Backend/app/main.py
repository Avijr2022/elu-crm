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
from app.models import prj as _prj_models  # noqa: F401 — register PRJ models
from app.models import fin as _fin_models  # noqa: F401 — register FIN models
from app.models import sal as _sal_models  # noqa: F401 — register SAL models
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
        from app.db.migrate_pf001 import apply_pf001_ddl
        from app.db.migrate_pf002 import apply_pf002_ddl
        from app.db.migrate_pf003 import apply_pf003_ddl
        from app.db.migrate_pf003a import apply_pf003a_ddl
        from app.db.migrate_pf004 import apply_pf004_ddl
        from app.db.rls_context import bind_rls_context, clear_rls_context, set_app_role_enabled

        # Bootstrap DDL + seed as owner/superuser; request sessions use elu_app.
        set_app_role_enabled(False)
        bind_rls_context(db, platform=True)
        apply_pf001_ddl(db)
        apply_pf002_ddl(db)
        apply_pf003_ddl(db)
        apply_pf003a_ddl(db)
        apply_pf004_ddl(db)
        from app.db.migrate_crm import apply_crm_ddl

        apply_crm_ddl(db)
        from app.db.migrate_sal import apply_sal_ddl

        apply_sal_ddl(db)
        from app.db.migrate_fin import apply_fin_ddl

        apply_fin_ddl(db)
        from app.db.migrate_prj import apply_prj_ddl

        apply_prj_ddl(db)
        seed_platform(db)
        clear_rls_context(db)
    finally:
        db.close()
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="0.7.0",
        description=(
            "E-LinkUp multi-tenant CRM/ERP API — PF-001…PF-003A + PF-004 Organizations "
            "+ Auth + CRM"
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
        allow_origins=[
            "http://localhost:8085",
            "http://localhost:8080",
            "http://127.0.0.1:8085",
            "http://127.0.0.1:8080",
            "http://[::1]:8085",  
            "http://[::1]:8080",
        ], #settings.cors_origin_list,
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
