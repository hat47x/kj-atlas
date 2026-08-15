import logging
from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import text

from kj_atlas_api.access_control import build_access_control_adapter
from kj_atlas_api.audit import build_audit_dispatcher
from kj_atlas_api.db import SessionLocal, init_db
from kj_atlas_api.database_content_store import DocumentRevisionDivergence
from kj_atlas_api.database_support import database_support_for_url
from kj_atlas_api.document_policy_binding import build_document_policy_binding_resolver
from kj_atlas_api.generation_repository import (
    GenerationBlobConflict,
    GenerationBlobUnavailable,
    RevisionHeadConflict,
)
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
from kj_atlas_api.observability import (
    INBOUND_TRACE_HEADER,
    REQUEST_ID_HEADER,
    configure_logging,
    new_request_id,
    request_id_var,
    resolve_inbound_request_id,
)
from kj_atlas_api.request_body_safety import JsonRequestBodySafetyMiddleware
from kj_atlas_api.settings import settings
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthStateStore
from kj_atlas_api.tenant_capability import build_tenant_capability_resolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeComponents,
    TrustedSaasRuntimePolicy,
    initialize_trusted_saas_runtime,
    release_trusted_saas_runtime,
    validate_saas_providers_exist,
    validate_trusted_saas_runtime_preflight,
)


configure_logging(level=settings.log_level, json_format=settings.log_json)

logger = logging.getLogger(__name__)


def _migration_script_heads() -> tuple[str, ...]:
    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    return tuple(script.get_heads())


def _assert_linear_migration_history() -> None:
    heads = _migration_script_heads()
    if len(heads) != 1:
        raise RuntimeError(f"Migration conflict detected; expected single head but got {heads}")


def _trusted_saas_runtime_policy() -> TrustedSaasRuntimePolicy:
    return TrustedSaasRuntimePolicy(
        database_backend=database_support_for_url(settings.database_url).backend,
        allow_jit_provisioning=settings.allow_jit_provisioning,
        access_control_adapter=settings.access_control_adapter,
        access_control_fail_safe_mode=settings.access_control_fail_safe_mode,
        document_policy_binding_resolver=settings.document_policy_binding_resolver,
        tenant_capability_resolver=settings.tenant_capability_resolver,
        # ADR-0063 D9-6: auth-edge settings
        jwt_algorithms=settings.jwt_algorithms,
        tenant_claim_name=settings.tenant_claim_name,
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
    if settings.runtime_profile == "saas-multitenant":
        _saas_auth_state_store.preflight()
    # ADR-0063 D9-6: post-DB-init check for active identity providers.
    if settings.runtime_profile == "saas-multitenant":
        validate_saas_providers_exist()
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


# SEC-HEADERS-01 (option a): the FastAPI interactive docs and the OpenAPI
# schema are a recon surface (every route + payload shape) with no API-key
# protection in the default compose deploy. Keep them for dev/evaluation
# convenience but disable them on production profiles (enterprise-production,
# saas-multitenant) so the surface is not reachable there.
_docs_enabled = settings.runtime_profile in {"local-dev", "evaluation"}
app = FastAPI(
    title="kj-atlas API",
    lifespan=lifespan,
    docs_url="/docs" if _docs_enabled else None,
    redoc_url="/redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)
_saas_auth_state_store = DatabaseSaasAuthStateStore(SessionLocal)

# ADR-0063 D9-6: install the trusted SaaS runtime adapter bundle at module
# scope so that initialize_trusted_saas_runtime() can find it during lifespan.
# The bundle is only installed for saas-multitenant; other profiles are unaffected.
if settings.runtime_profile == "saas-multitenant":
    from kj_atlas_api.active_tenant_session import (
        DatabaseActiveTenantSessionPersister,
        tenant_session_cookie_is_secure,
    )
    from kj_atlas_api.jwks_store import JwksStore
    from kj_atlas_api.tenant_context import ClaimBasedTenantContextResolver
    from kj_atlas_api.trusted_auth_edge import JwtSaasIdentityContextResolver
    from kj_atlas_api.trusted_saas_runtime import (
        TrustedSaasRuntimeAdapters,
        install_trusted_saas_runtime,
    )

    install_trusted_saas_runtime(
        app,
        TrustedSaasRuntimeAdapters(
            identity_context_resolver=JwtSaasIdentityContextResolver(
                jwks_store=JwksStore(),
            ),
            tenant_context_resolver=ClaimBasedTenantContextResolver(),
            active_tenant_session_persister=DatabaseActiveTenantSessionPersister(
                store=_saas_auth_state_store,
                secure_cookie=tenant_session_cookie_is_secure(
                    settings.runtime_profile,
                ),
            ),
        ),
    )

app.add_middleware(JsonRequestBodySafetyMiddleware)


@app.middleware("http")
async def assign_request_id(request: Request, call_next):
    """OPS-OBSERV-01: mint a correlation id for every request.

    Registered last so it runs first (Starlette applies middleware in reverse
    registration order), which means rejections from the body-safety and API-key
    middlewares are correlated too -- those are exactly the failures an operator
    gets asked about.

    An inbound `x-trace-id` is honoured when it is a safe opaque token so that a
    caller-side id survives into our logs; otherwise a server id is minted. The
    id is echoed in the response header and, for the error handlers below, in the
    body: without it the user has nothing to quote and the operator has nothing
    to grep.
    """
    inbound = resolve_inbound_request_id(request.headers.get(INBOUND_TRACE_HEADER))
    request_id = inbound or new_request_id()
    token = request_id_var.set(request_id)
    request.state.request_id = request_id
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers[REQUEST_ID_HEADER] = request_id
    return response


#: Unauthenticated operational endpoints. A probe must work before credentials
#: are configured, and none of these expose tenant data: /healthz is a constant,
#: /readyz reports dependency state plus Alembic revision ids, /version reports
#: the build revision and the bootstrap-mode-equivalent profile name.
_UNAUTHENTICATED_PATHS = frozenset({"/healthz", "/readyz", "/version"})


@app.middleware("http")
async def require_api_key(request: Request, call_next):
    if request.url.path in _UNAUTHENTICATED_PATHS:
        return await call_next(request)

    if settings.api_key:
        provided_key = request.headers.get("x-api-key")
        normalized_key = provided_key.strip() if provided_key is not None else None
        if not normalized_key or not compare_digest(normalized_key, settings.api_key):
            return JSONResponse(status_code=401, content=_error_body("Unauthorized"))

    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


def _error_body(detail: object) -> dict[str, object]:
    """Attach the correlation id to an error body.

    OPS-OBSERV-01: the user's screen showed only a status and a message, so a
    report could not be joined to a log line. The id is server-minted and opaque,
    carries no user content, and is already in the X-Request-Id response header --
    putting it in the body is what makes it quotable.
    """
    body: dict[str, object] = {"detail": detail}
    request_id = request_id_var.get()
    if request_id:
        body["requestId"] = request_id
    return body


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
    return JSONResponse(status_code=422, content=_error_body(errors))


@app.exception_handler(RevisionHeadConflict)
def handle_revision_head_conflict(_, _exc: RevisionHeadConflict) -> JSONResponse:
    return JSONResponse(status_code=409, content=_error_body("Document changed concurrently"))


@app.exception_handler(DocumentRevisionDivergence)
@app.exception_handler(GenerationBlobUnavailable)
@app.exception_handler(GenerationBlobConflict)
def handle_revision_storage_failure(_, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content=_error_body("Document revision storage failed integrity verification"),
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    """Liveness only: the process is up and serving.

    OPS-OBSERV-01: this deliberately checks nothing, and that is now documented
    rather than implied. It previously returned a constant while every runbook
    presented it as *the* API health check, so a backend that had lost its
    database still answered `{"status": "ok"}` -- and `docker-compose.yml` gated
    the web container on it. Use `/readyz` for dependency state.
    """
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> JSONResponse:
    """Readiness: the database is reachable and its schema is the expected one.

    The schema comparison closes a second gap. `_assert_linear_migration_history`
    runs at startup but inspects only the Alembic *script* directory -- it never
    reads `alembic_version` from the database -- so an application booted against
    a stale schema started cleanly and failed later at query time.

    Reports `not_ready` rather than raising: a readiness probe must answer with a
    status code, and the reason must not echo connection strings or driver text.
    """
    checks: dict[str, str] = {}

    try:
        expected_heads = set(_migration_script_heads())
    except Exception:
        expected_heads = set()
        checks["migrations"] = "unavailable"

    session = SessionLocal()
    try:
        session.execute(text("SELECT 1"))
        checks["database"] = "ok"

        if expected_heads:
            applied = {
                row[0]
                for row in session.execute(text("SELECT version_num FROM alembic_version"))
            }
            if applied == expected_heads:
                checks["schema"] = "ok"
            else:
                # Neither value is secret -- both are Alembic revision ids -- and
                # an operator cannot decide roll-forward vs restore without them.
                checks["schema"] = "mismatch"
                checks["schemaExpected"] = ",".join(sorted(expected_heads))
                checks["schemaApplied"] = ",".join(sorted(applied)) or "none"
    except Exception:
        logger.warning("readiness check failed", extra={"check": "database"})
        checks["database"] = "unreachable"
    finally:
        session.close()

    ready = checks.get("database") == "ok" and checks.get("schema") == "ok"
    return JSONResponse(
        status_code=200 if ready else 503,
        content={"status": "ready" if ready else "not_ready", "checks": checks},
    )


@app.get("/version")
def version() -> dict[str, str]:
    """What is actually deployed.

    OPS-OBSERV-01: there was no way to ask a running instance what it was running
    -- no git tags exist, no build metadata is baked into either image, and the
    support diagnostics bundle reported `revision: "unknown"` because
    `KJ_ATLAS_APP_REVISION` was never wired through the frontend build. An
    operator handling a report could not tell which build produced it.
    """
    return {
        "revision": settings.app_revision or "unknown",
        "runtimeProfile": app.state.runtime_profile
        if hasattr(app.state, "runtime_profile")
        else settings.runtime_profile,
    }


app.include_router(docs_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(ai_relations_router)
app.include_router(context_router)
app.include_router(document_access_admin_router)
app.include_router(inquiry_bundles_router)
app.include_router(session_router)
