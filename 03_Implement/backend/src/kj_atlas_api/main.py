import re
from contextlib import asynccontextmanager
from pathlib import Path
from secrets import compare_digest
from uuid import uuid4

from alembic.config import Config
from alembic.script import ScriptDirectory
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from kj_atlas_api.access_control import build_access_control_adapter
from kj_atlas_api.audit import build_audit_dispatcher
from kj_atlas_api.db import SessionLocal, init_db
from sqlalchemy import text
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
from kj_atlas_api.logging_config import configure_logging, request_id_var
from kj_atlas_api.request_body_safety import JsonRequestBodySafetyMiddleware
from kj_atlas_api.settings import settings
from kj_atlas_api.oauth_broker_client import ExternalOauthBrokerConfig
from kj_atlas_api.saas_auth_state import DatabaseSaasAuthSessionStore, DatabaseSaasAuthStateStore
from kj_atlas_api.tenant_capability import build_tenant_capability_resolver
from kj_atlas_api.trusted_saas_runtime import (
    TrustedSaasRuntimeComponents,
    TrustedSaasRuntimePolicy,
    initialize_trusted_saas_runtime,
    release_trusted_saas_runtime,
    validate_saas_providers_exist,
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
        database_backend=database_support_for_url(settings.database_url).backend,
        allow_jit_provisioning=settings.allow_jit_provisioning,
        access_control_adapter=settings.access_control_adapter,
        access_control_fail_safe_mode=settings.access_control_fail_safe_mode,
        document_policy_binding_resolver=settings.document_policy_binding_resolver,
        tenant_capability_resolver=settings.tenant_capability_resolver,
        # ADR-0063 D9-6: auth-edge settings
        jwt_algorithms=settings.jwt_algorithms,
        tenant_claim_name=settings.tenant_claim_name,
        # SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074): BFF OAuth broker settings
        saas_oauth_broker_http_authorize_endpoint=settings.saas_oauth_broker_http_authorize_endpoint,
        saas_oauth_broker_http_token_endpoint=settings.saas_oauth_broker_http_token_endpoint,
        saas_oauth_broker_http_redirect_uri=settings.saas_oauth_broker_http_redirect_uri,
        saas_oauth_broker_http_client_id=settings.saas_oauth_broker_http_client_id,
        saas_oauth_broker_http_client_secret=settings.saas_oauth_broker_http_client_secret,
        saas_oauth_broker_http_timeout_seconds=settings.saas_oauth_broker_http_timeout_seconds,
        saas_auth_session_hash_key=settings.saas_auth_session_hash_key,
    )


def _saas_oauth_broker_config() -> ExternalOauthBrokerConfig | None:
    """None when any required field is unset -- handle_callback (oauth_bff.py)
    fails closed with 503 rather than construct a config with missing fields."""
    token_endpoint = settings.saas_oauth_broker_http_token_endpoint
    redirect_uri = settings.saas_oauth_broker_http_redirect_uri
    client_id = settings.saas_oauth_broker_http_client_id
    client_secret = settings.saas_oauth_broker_http_client_secret
    if token_endpoint is None or redirect_uri is None or client_id is None or client_secret is None:
        return None
    return ExternalOauthBrokerConfig(
        token_endpoint=token_endpoint,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        timeout_seconds=settings.saas_oauth_broker_http_timeout_seconds,
    )


def _saas_auth_session_hash_key_bytes() -> bytes | None:
    raw = settings.saas_auth_session_hash_key
    return bytes.fromhex(raw) if raw else None


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
        _saas_auth_session_store.preflight()
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
# /docs is owned by the documents API (GET /docs list + /docs/{id}); the
# interactive API UI is served at /api-docs so the two never collide.
_docs_enabled = settings.runtime_profile in {"local-dev", "evaluation"}
app = FastAPI(
    title="kj-atlas API",
    lifespan=lifespan,
    docs_url="/api-docs" if _docs_enabled else None,
    redoc_url="/api-redoc" if _docs_enabled else None,
    openapi_url="/openapi.json" if _docs_enabled else None,
)

# OPS-OBSERV-01 AC-1: install the JSON formatter before any logger emits, so the
# `extra={...}` payloads (audit dispatch, LLM metadata) are rendered instead of
# silently dropped. Level comes from KJ_ATLAS_LOG_LEVEL.
configure_logging(settings.log_level)

_saas_auth_state_store = DatabaseSaasAuthStateStore(SessionLocal)
_saas_auth_session_store = DatabaseSaasAuthSessionStore(SessionLocal)

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

    # SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074): oauth_bff.py's
    # handle_callback and the resolver's cookie-fallback branch must agree on
    # this key -- computed once and shared, matching ac1_final_design.md SS7.
    _saas_auth_session_hash_key = _saas_auth_session_hash_key_bytes()
    app.state.saas_oauth_broker_config = _saas_oauth_broker_config()
    app.state.saas_auth_session_store = _saas_auth_session_store
    app.state.saas_auth_state_store = _saas_auth_state_store
    app.state.saas_auth_session_hash_key = _saas_auth_session_hash_key

    install_trusted_saas_runtime(
        app,
        TrustedSaasRuntimeAdapters(
            identity_context_resolver=JwtSaasIdentityContextResolver(
                jwks_store=JwksStore(),
                auth_session_store=_saas_auth_session_store,
                auth_session_hash_key=_saas_auth_session_hash_key,
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
async def require_api_key(request: Request, call_next):
    # SEC-ADMIN-PLANE-02 (D-a): the /admin/* control plane is authorized solely
    # by require_control_plane_authorization (X-Admin-Api-Key or a provision
    # capability), never by the business-plane X-API-Key. Skipping /admin/*
    # here is what makes "admin key alone" work when BOTH keys are configured —
    # otherwise the business-key middleware re-couples the control plane to the
    # business plane, the exact separation ADR-0072 established. Every
    # /admin/provision/* route must carry the control-plane dependency.
    # /healthz and /readyz are liveness/readiness probes used by orchestration
    # (compose healthchecks), so they are unauthenticated like /admin/* is
    # control-plane-only. /version remains gated by the business key.
    if request.url.path in {"/healthz", "/readyz"} or request.url.path.startswith("/admin/"):
        return await call_next(request)

    if settings.api_key:
        provided_key = request.headers.get("x-api-key")
        normalized_key = provided_key.strip() if provided_key is not None else None
        if not normalized_key or not compare_digest(normalized_key, settings.api_key):
            # OPS-OBSERV-01 AC-2: the 401 body carries the same request ID that
            # appears in the log record and the X-Request-Id header.
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized", "requestId": request_id_var.get()},
            )

    return await call_next(request)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


#: OPS-OBSERV-01 AC-2: a safe, bounded opaque request-ID form. Inbound
#: x-trace-id is respected only when it matches this — anything else is replaced
#: with a fresh ID rather than echoed (header-injection safe).
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    # Registered last so it is the outermost middleware: the correlation ID is
    # minted before the api-key check and the route run, every log record during
    # the request carries it (via the contextvar), and every response echoes it
    # so the client can tie a reported failure to a server-side log line.
    inbound = request.headers.get("x-trace-id")
    request_id = inbound if inbound and _REQUEST_ID_PATTERN.fullmatch(inbound) else uuid4().hex
    token = request_id_var.set(request_id)
    try:
        response = await call_next(request)
    finally:
        request_id_var.reset(token)
    response.headers["X-Request-Id"] = request_id
    return response


def _with_request_id(content: dict[str, object]) -> dict[str, object]:
    """OPS-OBSERV-01 AC-2: tag an error body with the in-flight request ID so the
    client can join a reported failure to the server-side log line."""
    merged = dict(content)
    request_id = request_id_var.get()
    if request_id:
        merged["requestId"] = request_id
    return merged


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
    return JSONResponse(status_code=422, content=_with_request_id({"detail": errors}))


@app.exception_handler(RevisionHeadConflict)
def handle_revision_head_conflict(_, _exc: RevisionHeadConflict) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content=_with_request_id({"detail": "Document changed concurrently"}),
    )


@app.exception_handler(DocumentRevisionDivergence)
@app.exception_handler(GenerationBlobUnavailable)
@app.exception_handler(GenerationBlobConflict)
def handle_revision_storage_failure(_, _exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=503,
        content=_with_request_id(
            {"detail": "Document revision storage failed integrity verification"}
        ),
    )


@app.exception_handler(Exception)
def handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
    # OPS-OBSERV-01: a catch-all 500 that logs the exception (with the request
    # ID) and returns a generic body tagged with the same ID. The request ID is
    # how an operator joins this response to the structured log line.
    import logging

    logging.getLogger(__name__).exception("unhandled error", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content=_with_request_id({"detail": "Internal server error"}),
    )


def _migration_heads() -> list[str]:
    backend_dir = Path(__file__).resolve().parents[2]
    cfg = Config(str(backend_dir / "alembic.ini"))
    cfg.set_main_option("script_location", str(backend_dir / "alembic"))
    return sorted(ScriptDirectory.from_config(cfg).get_heads())


@app.get("/healthz")
def healthz() -> dict[str, str]:
    # OPS-OBSERV-01 AC-3: liveness ONLY — the process is up. It deliberately does
    # not probe the DB; use /readyz for dependency readiness.
    return {"status": "ok"}


@app.get("/readyz")
def readyz() -> JSONResponse:
    # OPS-OBSERV-01 AC-3: readiness — DB reachable AND the schema is at the
    # migration head (so a stale-DB backend does not answer "ok" and then fail
    # on the first query).
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
            applied = (
                db.execute(text("SELECT version_num FROM alembic_version"))
                .scalars()
                .all()
            )
    except Exception as exc:  # noqa: BLE001 - readiness must not 500
        import logging

        logging.getLogger(__name__).warning(
            "readyz database check failed",
            exc_info=exc,
            extra={"error": str(exc)},
        )
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "database_unavailable",
                "requestId": request_id_var.get(),
            },
        )
    expected = set(_migration_heads())
    if set(applied) != expected:
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "reason": "schema_mismatch",
                "applied": sorted(applied),
                "expected": sorted(expected),
                "requestId": request_id_var.get(),
            },
        )
    return JSONResponse(status_code=200, content={"status": "ready"})


@app.get("/version")
def version() -> dict[str, str]:
    # OPS-OBSERV-01 AC-4: build revision so a diagnostics bundle or an operator
    # can address exactly which build is serving.
    return {"revision": settings.app_revision, "runtimeProfile": settings.runtime_profile}


app.include_router(docs_router)
app.include_router(admin_router)
app.include_router(ai_router)
app.include_router(ai_relations_router)
app.include_router(context_router)
app.include_router(document_access_admin_router)
app.include_router(inquiry_bundles_router)
app.include_router(session_router)
