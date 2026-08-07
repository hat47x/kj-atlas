from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.engine import make_url

from kj_atlas_api.access_control import build_access_control_adapter
from kj_atlas_api.audit import build_audit_dispatcher
from kj_atlas_api.db import init_db
from kj_atlas_api.document_policy_binding import build_document_policy_binding_resolver
from kj_atlas_api.routes.ai import router as ai_router
from kj_atlas_api.routes.ai_relations import router as ai_relations_router
from kj_atlas_api.routes.admin import router as admin_router
from kj_atlas_api.routes.docs import router as docs_router
from kj_atlas_api.routes.context import router as context_router
from kj_atlas_api.routes.document_access_admin import (
    router as document_access_admin_router,
)
from kj_atlas_api.routes.inquiry_bundles import router as inquiry_bundles_router
from kj_atlas_api.routes.session import router as session_router
from kj_atlas_api.request_body_safety import JsonRequestBodySafetyMiddleware
from kj_atlas_api.settings import settings
from kj_atlas_api.tenant_capability import build_tenant_capability_resolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeComponents,
    TrustedSaasRuntimePolicy,
    initialize_trusted_saas_runtime,
    release_trusted_saas_runtime,
    validate_trusted_saas_runtime_preflight,
)


def _assert_linear_migration_history() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Migration conflict detected; expected single head but got {heads}")


def _trusted_saas_runtime_policy() -> TrustedSaasRuntimePolicy:
    return TrustedSaasRuntimePolicy(
        database_backend=make_url(settings.database_url).get_backend_name(),
        allow_jit_provisioning=settings.allow_jit_provisioning,
        access_control_adapter=settings.access_control_adapter,
        access_control_fail_safe_mode=settings.access_control_fail_safe_mode,
        document_policy_binding_resolver=settings.document_policy_binding_resolver,
        tenant_capability_resolver=settings.tenant_capability_resolver,
    )


def _trusted_saas_runtime_components() -> TrustedSaasRuntimeComponents:
    return TrustedSaasRuntimeComponents(
        access_control_adapter=build_access_control_adapter(
            adapter_name=settings.access_control_adapter
        ),
        tenant_capability_resolver=build_tenant_capability_resolver(),
        document_policy_binding_resolver=build_document_policy_binding_resolver(),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    _assert_linear_migration_history()
    runtime_policy = _trusted_saas_runtime_policy()
    runtime_components = _trusted_saas_runtime_components()
    validate_trusted_saas_runtime_preflight(
        app,
        runtime_profile=settings.runtime_profile,
        runtime_policy=runtime_policy,
        runtime_components=runtime_components,
    )
    init_db()
    app.state.runtime_profile = settings.runtime_profile
    app.state.audit_dispatcher = build_audit_dispatcher()
    app.state.access_control_adapter = runtime_components.access_control_adapter
    app.state.access_control_fail_safe_mode = settings.access_control_fail_safe_mode
    app.state.tenant_capability_resolver = runtime_components.tenant_capability_resolver
    initialize_trusted_saas_runtime(
        app,
        runtime_profile=app.state.runtime_profile,
        runtime_policy=runtime_policy,
        runtime_components=runtime_components,
    )
    try:
        yield
    finally:
        release_trusted_saas_runtime(app)


app = FastAPI(title="kj-atlas API", lifespan=lifespan)
app.add_middleware(JsonRequestBodySafetyMiddleware)


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


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


@app.exception_handler(RequestValidationError)
def handle_validation_error(_, exc: RequestValidationError) -> JSONResponse:
    # SEC-VALIDATION-LEAK-01: pydantic v2's error dict includes the rejected raw
    # value under `input` (PII leak) and a non-serializable exception under `ctx`
    # (would break the response). Return only the safe serializable fields —
    # type/loc/msg — matching the routes/docs.py A1ErrorResponse pattern.
    errors = [
        {key: error[key] for key in ("type", "loc", "msg") if key in error}
        for error in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(docs_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(ai_relations_router)
app.include_router(context_router)
app.include_router(document_access_admin_router)
app.include_router(inquiry_bundles_router)
app.include_router(session_router)
