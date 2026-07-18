from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kj_atlas_api.access_control import build_access_control_adapter
from kj_atlas_api.audit import build_audit_dispatcher
from kj_atlas_api.db import init_db
from kj_atlas_api.document_access_resource import SingleTenantHeaderResourceResolver
from kj_atlas_api.routes.ai import router as ai_router
from kj_atlas_api.routes.ai_relations import router as ai_relations_router
from kj_atlas_api.routes.admin import router as admin_router
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.context import router as context_router
from kj_atlas_api.routes.document_access_admin import (
    router as document_access_admin_router,
)
from kj_atlas_api.routes.session import router as session_router
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_capability import build_tenant_capability_resolver
from kj_atlas_api.tenant_context import SingleTenantContextResolver


def _assert_linear_migration_history() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Migration conflict detected; expected single head but got {heads}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    _assert_linear_migration_history()
    init_db()
    app.state.runtime_profile = settings.runtime_profile
    app.state.audit_dispatcher = build_audit_dispatcher()
    app.state.access_control_adapter = build_access_control_adapter(adapter_name=settings.access_control_adapter)
    app.state.access_control_fail_safe_mode = settings.access_control_fail_safe_mode
    app.state.tenant_context_resolver = SingleTenantContextResolver()
    app.state.document_access_resource_resolver = SingleTenantHeaderResourceResolver()
    app.state.saas_identity_context_resolver = None
    app.state.tenant_capability_resolver = build_tenant_capability_resolver()
    app.state.active_tenant_session_persister = None
    yield


app = FastAPI(title="kj-atlas API", lifespan=lifespan)


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path == "/healthz":
        return await call_next(request)

    if settings.api_key:
        provided_key = request.headers.get("x-api-key")
        normalized_key = provided_key.strip() if provided_key is not None else None
        if not normalized_key or not compare_digest(normalized_key, settings.api_key):
            return JSONResponse(status_code=401, content={"detail": "Unauthorized"})

    return await call_next(request)


@app.exception_handler(RequestValidationError)
def handle_validation_error(_, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(docs_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(ai_relations_router)
app.include_router(context_router)
app.include_router(document_access_admin_router)
app.include_router(session_router)
