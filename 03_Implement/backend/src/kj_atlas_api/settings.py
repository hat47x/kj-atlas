import ipaddress
import os
import re
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from kj_atlas_api.database_support import require_verified_database_url


_LLM_HOST_LABEL = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


def _validate_trusted_http_resolver(
    *,
    resolver: str,
    resolver_key: str,
    endpoint: str | None,
    endpoint_key: str,
    api_key: str | None,
    api_key_key: str,
) -> str:
    normalized_resolver = resolver.strip().lower()
    if normalized_resolver not in {"none", "external_http"}:
        raise ValueError(f"{resolver_key} must be one of none|external_http")
    if normalized_resolver == "none":
        if endpoint is not None or api_key is not None:
            raise ValueError(f"{endpoint_key} and {api_key_key} require {resolver_key}=external_http")
        return normalized_resolver

    if endpoint is None:
        raise ValueError(f"{endpoint_key} is required and must be canonical")
    _validate_trusted_http_endpoint(endpoint=endpoint, endpoint_key=endpoint_key)
    _validate_canonical_bearer(api_key=api_key, api_key_key=api_key_key)
    return normalized_resolver


def _validate_trusted_http_endpoint(*, endpoint: str, endpoint_key: str) -> None:
    if (
        not endpoint
        or endpoint.strip() != endpoint
        or "\\" in endpoint
        or "?" in endpoint
        or "#" in endpoint
        or any(character.isspace() for character in endpoint)
        or any(not character.isprintable() for character in endpoint)
    ):
        raise ValueError(f"{endpoint_key} is required and must be canonical")
    parsed_endpoint = urlsplit(endpoint)
    try:
        parsed_endpoint.port
    except ValueError:
        raise ValueError(f"{endpoint_key} has an invalid port") from None
    if (
        parsed_endpoint.scheme not in {"http", "https"}
        or not parsed_endpoint.hostname
        or parsed_endpoint.username is not None
        or parsed_endpoint.password is not None
        or parsed_endpoint.query
        or parsed_endpoint.fragment
    ):
        raise ValueError(
            f"{endpoint_key} must be an http(s) URL without credentials, query, or fragment"
        )
    if parsed_endpoint.scheme == "http" and (
        parsed_endpoint.hostname not in {"localhost", "127.0.0.1", "::1"}
    ):
        raise ValueError(f"{endpoint_key} allows HTTP only for loopback endpoints")


def _validate_canonical_bearer(*, api_key: str | None, api_key_key: str) -> None:
    if api_key is not None and (
        not api_key
        or any(character.isspace() for character in api_key)
        or any(not character.isprintable() for character in api_key)
    ):
        raise ValueError(f"{api_key_key} must be a non-empty canonical bearer value")


def _validate_optional_http_integration(
    *,
    enabled: bool,
    endpoint: str | None,
    endpoint_key: str,
    api_key: str | None,
    api_key_key: str,
) -> None:
    if not enabled:
        if endpoint is not None or api_key is not None:
            raise ValueError(f"{endpoint_key} and {api_key_key} require the HTTP integration")
        return
    if endpoint is None:
        raise ValueError(f"{endpoint_key} is required when the HTTP integration is enabled")
    _validate_trusted_http_endpoint(endpoint=endpoint, endpoint_key=endpoint_key)
    _validate_canonical_bearer(api_key=api_key, api_key_key=api_key_key)


_HEX_KEY_PATTERN = re.compile(r"^[0-9a-f]{64}$")


def _validate_hex_key(*, value: str | None, value_key: str) -> None:
    """64 lowercase hex chars = 32 bytes, for an HMAC signing/hashing key.

    No prior *_SIGNING_KEY/*_HASH_KEY settings exist in this codebase to
    reuse a validator from -- this is new (SAAS-TENANT-SESSION-BINDING-01).
    """
    if value is not None and not _HEX_KEY_PATTERN.fullmatch(value):
        raise ValueError(f"{value_key} must be 64 lowercase hex characters (32 bytes)")


def _validate_optional_header_value(*, value: str | None, value_key: str) -> None:
    if value is not None and (
        not value
        or len(value) > 2048
        or value.strip() != value
        or any(character.isspace() for character in value)
        or any(not character.isprintable() for character in value)
    ):
        raise ValueError(f"{value_key} must be a bounded canonical header value")


def _validate_trusted_proxies(raw: str) -> str:
    """Validate comma-separated CIDR ranges. Returns normalized form."""
    if not raw.strip():
        return ""
    cidrs = [cidr.strip() for cidr in raw.split(",") if cidr.strip()]
    if not cidrs:
        return ""
    for cidr in cidrs:
        try:
            ipaddress.ip_network(cidr, strict=False)
        except ValueError:
            raise ValueError(
                f"KJ_ATLAS_TRUSTED_PROXIES contains invalid CIDR: {cidr}"
            ) from None
    return ",".join(cidrs)


def _validate_optional_llm_model_id(*, value: str | None, value_key: str) -> None:
    if value is not None and (
        not value
        or len(value) > 256
        or value.strip() != value
        or "\\" in value
        or any(character.isspace() for character in value)
        or any(not character.isprintable() for character in value)
    ):
        raise ValueError(f"{value_key} must be a bounded canonical model identifier")


def _normalize_llm_allowlist(raw_allowlist: str | None) -> str | None:
    if raw_allowlist is None:
        return None
    raw_hosts = raw_allowlist.split(",")
    if not raw_hosts or any(not host.strip() for host in raw_hosts):
        raise ValueError("KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST must contain canonical hosts")

    normalized_hosts: list[str] = []
    for raw_host in raw_hosts:
        host = raw_host.strip().lower()
        try:
            normalized_host = str(ipaddress.ip_address(host))
        except ValueError:
            labels = host.split(".")
            if (
                len(host) > 253
                or not labels
                or any(not _LLM_HOST_LABEL.fullmatch(label) for label in labels)
            ):
                raise ValueError(
                    "KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST must contain canonical hosts"
                ) from None
            normalized_host = host
        if normalized_host in normalized_hosts:
            raise ValueError(
                "KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST must not contain duplicate hosts"
            )
        normalized_hosts.append(normalized_host)
    return ",".join(normalized_hosts)


LEGACY_ENV_KEYS = {
    "RUNTIME_PROFILE",
    "DATABASE_URL",
    "LLM_PROVIDER",
    "LOCAL_LLM_BASE_URL",
    "LOCAL_LLM_MODEL",
    "LARGE_SCALE_LLM_BASE_URL",
    "LARGE_SCALE_LLM_MODEL",
    "LLM_ESCALATION_ENABLED",
    "LLM_LARGE_SCALE_OPT_IN",
    "LARGE_SCALE_LLM_ALLOWLIST",
    "LLM_FALLBACK_TO_NONE",
    "DEEPSEEK_API_KEY",
    "DEEPSEEK_BASE_URL",
    "DEEPSEEK_MODEL",
    "API_KEY",
    "AUDIT_EXPORT_ENABLED",
    "AUDIT_TRANSPORT",
    "AUDIT_HTTP_ENDPOINT",
    "AUDIT_HTTP_API_KEY",
    "AUDIT_HTTP_TIMEOUT_SECONDS",
    "AUDIT_QUEUE_SIZE",
    "AUDIT_ALLOW_IN_SAFE_MODE",
    "ACCESS_CONTROL_ADAPTER",
    "ACCESS_CONTROL_FAIL_SAFE_MODE",
    "ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
    "ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS",
    "ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE",
    "ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
    "ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER",
    "DOCUMENT_POLICY_BINDING_RESOLVER",
    "DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT",
    "DOCUMENT_POLICY_BINDING_HTTP_API_KEY",
    "DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS",
    "TENANT_CAPABILITY_RESOLVER",
    "TENANT_CAPABILITY_HTTP_ENDPOINT",
    "TENANT_CAPABILITY_HTTP_API_KEY",
    "TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS",
    "ALLOW_JIT_PROVISIONING",
    "AUTH_PROVIDER_FIELD",
    "AUTH_USER_FIELD",
    "AUTH_EMAIL_FIELD",
    "AUTH_NAME_FIELD",
    "AUTH_SUBJECT_FIELD",
    "REVIEWER_REF_RESOLVER_ADAPTER",
    "CE4_EQUIVALENCE_MODE",
    "CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT",
    "CE4_AUDIT_REQUIRE_ALL_EVENTS",
    "CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK",
    "CE4_STUB_UNRESOLVED_CONTRACTS",
}


class Settings(BaseSettings):
    runtime_profile: str = Field(
        default="local-dev",
        validation_alias="KJ_ATLAS_RUNTIME_PROFILE",
    )
    database_url: str = Field(
        default="sqlite:///./kj_atlas.db",
        validation_alias="KJ_ATLAS_DATABASE_URL",
    )
    llm_provider: str = Field(
        default="none",
        validation_alias="KJ_ATLAS_LLM_PROVIDER",
    )
    local_llm_base_url: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LOCAL_LLM_BASE_URL",
    )
    local_llm_model: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LOCAL_LLM_MODEL",
    )
    large_scale_llm_base_url: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL",
    )
    large_scale_llm_model: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LARGE_SCALE_LLM_MODEL",
    )
    llm_escalation_enabled: bool = Field(
        default=False,
        validation_alias="KJ_ATLAS_LLM_ESCALATION_ENABLED",
    )
    llm_large_scale_opt_in: bool = Field(
        default=False,
        validation_alias="KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN",
    )
    large_scale_llm_allowlist: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST",
    )
    llm_fallback_to_none: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_LLM_FALLBACK_TO_NONE",
    )
    # DeepSeek API settings (OpenAI-compatible)
    deepseek_api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_DEEPSEEK_API_KEY",
    )
    deepseek_base_url: str = Field(
        default="https://api.deepseek.com",
        validation_alias="KJ_ATLAS_DEEPSEEK_BASE_URL",
    )
    deepseek_model: str = Field(
        default="deepseek-chat",
        validation_alias="KJ_ATLAS_DEEPSEEK_MODEL",
    )
    # AI-ROUTE-01 MMR-04: high-reasoning model for final_judgement tasks
    # (check_narrative, detect_contradiction).
    llm_high_reasoning_model: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_LLM_HIGH_REASONING_MODEL",
    )
    # OPS-OBSERV-01: no logging configuration existed, so `extra={...}` payloads
    # were silently discarded by the default formatter. These two keys install
    # one.
    log_level: str = Field(
        default="INFO",
        validation_alias="KJ_ATLAS_LOG_LEVEL",
    )
    log_json: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_LOG_JSON",
    )
    api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_API_KEY",
    )
    # ADR-0072 D1=A: the control-plane bootstrap credential. Deliberately a
    # separate key from `api_key` (the business plane): SEC-ADMIN-PLANE-01 found
    # that one shared static key protected document, AI, and provisioning
    # surfaces alike, so anyone able to read a document could also register a
    # trusted JWT issuer. Bootstrap-only by intent -- normal operation goes
    # through the capability claim (D1=B).
    admin_api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_ADMIN_API_KEY",
    )
    audit_export_enabled: bool = Field(
        default=False,
        validation_alias="KJ_ATLAS_AUDIT_EXPORT_ENABLED",
    )
    audit_transport: str = Field(
        default="noop",
        validation_alias="KJ_ATLAS_AUDIT_TRANSPORT",
    )
    audit_http_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_AUDIT_HTTP_ENDPOINT",
    )
    audit_http_api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_AUDIT_HTTP_API_KEY",
    )
    audit_http_timeout_seconds: float = Field(
        default=2.0,
        gt=0,
        le=30,
        validation_alias="KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS",
    )
    audit_queue_size: int = Field(
        default=100,
        gt=0,
        validation_alias="KJ_ATLAS_AUDIT_QUEUE_SIZE",
    )
    audit_dedup_window_seconds: float = Field(
        default=5.0,
        ge=0,
        validation_alias="KJ_ATLAS_AUDIT_DEDUP_WINDOW_SECONDS",
    )
    audit_allow_in_safe_mode: bool = Field(
        default=False,
        validation_alias="KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE",
    )
    access_control_adapter: str = Field(
        default="noop",
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_ADAPTER",
    )
    access_control_fail_safe_mode: str = Field(
        default="read_only",
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE",
    )
    access_control_external_http_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
    )
    access_control_external_http_timeout_seconds: float = Field(
        default=1.5,
        gt=0,
        le=30,
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS",
    )
    access_control_external_http_auth_mode: str = Field(
        default="none",
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE",
    )
    access_control_external_http_static_bearer_token: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
    )
    access_control_external_http_idp_issuer: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER",
    )
    document_policy_binding_resolver: str = Field(
        default="none",
        validation_alias="KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER",
    )
    document_policy_binding_http_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT",
    )
    document_policy_binding_http_api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY",
    )
    document_policy_binding_http_timeout_seconds: float = Field(
        default=1.5,
        gt=0,
        le=30,
        validation_alias="KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_TIMEOUT_SECONDS",
    )
    tenant_capability_resolver: str = Field(
        default="none",
        validation_alias="KJ_ATLAS_TENANT_CAPABILITY_RESOLVER",
    )
    tenant_capability_http_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT",
    )
    tenant_capability_http_api_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY",
    )
    tenant_capability_http_timeout_seconds: float = Field(
        default=1.5,
        gt=0,
        le=30,
        validation_alias="KJ_ATLAS_TENANT_CAPABILITY_HTTP_TIMEOUT_SECONDS",
    )
    # SAAS-TENANT-SESSION-BINDING-01 AC-1 (ADR-0074): confidential-client OAuth
    # broker used by the BFF to exchange an authorization code for tokens.
    # Format-only validated here (like local_llm_base_url); requiredness for
    # saas-multitenant lives solely in TrustedSaasRuntimePolicy (ADR-0063 D9-6
    # comment at the top of validate_llm_provider_guards) -- no runtime_profile
    # branch is added here.
    saas_oauth_broker_http_authorize_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT",
    )
    saas_oauth_broker_http_token_endpoint: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT",
    )
    saas_oauth_broker_http_redirect_uri: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI",
    )
    saas_oauth_broker_http_client_id: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID",
    )
    saas_oauth_broker_http_client_secret: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET",
    )
    saas_oauth_broker_http_timeout_seconds: float = Field(
        default=5.0,
        gt=0,
        le=30,
        validation_alias="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TIMEOUT_SECONDS",
    )
    # Keyed HMAC-SHA256 key for hashing the opaque auth-session cookie value
    # before it is stored (ADR-0074 decision 2: never persist the raw value).
    # 64 lowercase hex chars = 32 bytes. Rotation procedure: set a new key and
    # restart the fleet; every existing session_key_hash stops matching and
    # every browser is forced through a fresh GET /session/login. A seamless
    # dual-key rollover is a distinct future feature, not part of AC-1.
    saas_auth_session_hash_key: str | None = Field(
        default=None,
        validation_alias="KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY",
    )
    app_revision: str = Field(
        # OPS-OBSERV-01 AC-4: build revision surfaced by /version and attached to
        # structured log records so diagnostics bundles become addressable
        # server-side. Wired from the Docker build; "unknown" when unset.
        default="unknown",
        validation_alias="KJ_ATLAS_APP_REVISION",
    )
    allow_jit_provisioning: bool = Field(
        # SEC-RATE-LIMIT-01: fail-closed by default. The default-True config
        # let an unauthenticated request with an unknown x-forwarded-user
        # header auto-create a user (verified 2026-08-12). Production already
        # recommends False (deploy/broker/README.md); local-dev / evaluation
        # that want header-originated users must set it True explicitly.
        default=False,
        validation_alias="KJ_ATLAS_ALLOW_JIT_PROVISIONING",
    )
    max_document_bytes: int = Field(
        # SEC-DOC-BOUND-01: bound DocumentV1 payload size, matching the inquiry
        # bundle's 20 MiB cap. Verified live: ~2MB / 20,000 cards were accepted
        # unbounded before this. Configurable for organizations that need a
        # different ceiling.
        default=20 * 1024 * 1024,
        validation_alias="KJ_ATLAS_MAX_DOCUMENT_BYTES",
    )
    max_document_cards: int = Field(
        # SEC-DOC-BOUND-01: bound card count as a secondary defense (the byte
        # ceiling already bounds total size; this bounds pathological card
        # counts that stay under 20 MiB via tiny card texts). Generous default
        # (10,000) — realistic KJ canvases are tens to low hundreds of cards.
        default=10_000,
        validation_alias="KJ_ATLAS_MAX_DOCUMENT_CARDS",
    )
    allow_unreviewed_ai_text: bool = Field(
        # SEC-AI-SAFEMODE-01 (ADR-0068 D1=C): gate the allowUnreviewedText
        # relaxation. The request may ASK to relax, but it is only honored when
        # this profile setting is true; otherwise the request's relaxation is
        # ignored and unreviewed text is still rejected (fail-closed).
        default=False,
        validation_alias="KJ_ATLAS_ALLOW_UNREVIEWED_AI_TEXT",
    )
    auth_provider_field: str = Field(
        default="x-auth-provider",
        validation_alias="KJ_ATLAS_AUTH_PROVIDER_FIELD",
    )
    auth_user_field: str = Field(
        default="x-forwarded-user",
        validation_alias="KJ_ATLAS_AUTH_USER_FIELD",
    )
    auth_email_field: str = Field(
        default="x-forwarded-email",
        validation_alias="KJ_ATLAS_AUTH_EMAIL_FIELD",
    )
    auth_name_field: str = Field(
        default="x-forwarded-name",
        validation_alias="KJ_ATLAS_AUTH_NAME_FIELD",
    )
    auth_subject_field: str = Field(
        default="x-auth-subject",
        validation_alias="KJ_ATLAS_AUTH_SUBJECT_FIELD",
    )
    # ADR-0065: per-task model override (comma-separated task=model pairs).
    # Example: "re_layout=deepseek-chat,generate_narrative=deepseek-reasoner"
    # Unlisted tasks use the default model (local_llm_model).
    llm_task_model_map: str = Field(
        default="",
        validation_alias="KJ_ATLAS_LLM_TASK_MODEL_MAP",
    )
    # ADR-0063 correction #2: CIDR-based trusted proxy allowlist for
    # header-based auth (single-tenant / legacy header mode). When empty,
    # all origins are allowed with a startup warning (backward compat).
    # When set, only requests from listed CIDRs can use forwarded auth headers.
    # Comma-separated IPv4/IPv6 CIDR ranges, e.g. "10.0.0.0/8,172.16.0.0/12".
    trusted_proxies: str = Field(
        default="",
        validation_alias="KJ_ATLAS_TRUSTED_PROXIES",
    )
    reviewer_ref_resolver_adapter: str = Field(
        default="user_id",
        validation_alias="KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER",
    )
    ce4_equivalence_mode: str = Field(
        default="equivalence_and_bundle_hash",
        validation_alias="KJ_ATLAS_CE4_EQUIVALENCE_MODE",
    )
    ce4_dry_run_enforce_no_side_effect: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT",
    )
    ce4_audit_require_all_events: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS",
    )
    ce4_source_bundle_hash_allow_mock: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_CE4_SOURCE_BUNDLE_HASH_ALLOW_MOCK",
    )
    ce4_stub_unresolved_contracts: bool = Field(
        default=True,
        validation_alias="KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS",
    )
    # ADR-0063 D4: JWT algorithm allowlist (comma-separated). Default RS256,ES256.
    # HMAC and 'none' are always rejected regardless of this setting.
    jwt_algorithms: str = Field(
        default="RS256,ES256",
        validation_alias="KJ_ATLAS_JWT_ALGORITHMS",
    )
    # ADR-0063 D8: JWT claim name that carries the external tenant/organization
    # reference. The claim value is matched against
    # tenant_identity_providers.external_tenant_ref to resolve tenant_id.
    tenant_claim_name: str = Field(
        default="tenant_ref",
        validation_alias="KJ_ATLAS_TENANT_CLAIM_NAME",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        hide_input_in_errors=True,
    )

    #: Profiles that must not start without an authentication means configured.
    #: ADR-0072 D3=A applies ADR-0062's fail-fast rule ("explicitly selected but
    #: unconfigured means refuse to start") to authentication itself.
    _AUTH_REQUIRED_PROFILES = ("enterprise-production", "saas-multitenant")

    def _validate_production_authentication_configured(self, profile: str) -> None:
        """ADR-0072 D3=A: refuse to start a production profile with no auth.

        SEC-ADMIN-PLANE-01: `enterprise-production` started fully unauthenticated
        at defaults, because `api_key` defaults to None and the middleware simply
        passes through when it is unset. A deployment mistake therefore exposed
        every surface rather than failing closed.

        The two profiles differ in what "authentication is configured" means:

        - `enterprise-production` resolves business-plane identity from proxy
          headers, so the shared `api_key` is the only thing standing between the
          internet and the document API. It is required.
        - `saas-multitenant` authenticates the business plane through the trusted
          auth edge (verified JWT), which `TrustedSaasRuntimePolicy.validate()`
          already enforces at startup, so `api_key` is not the gate there.

        Both need the control plane credential: it is the bootstrap path that
        exists precisely for the state where no IdP is registered yet.
        """
        if profile not in self._AUTH_REQUIRED_PROFILES:
            return

        missing: list[str] = []
        if self.admin_api_key is None:
            missing.append("KJ_ATLAS_ADMIN_API_KEY")
        if profile == "enterprise-production" and self.api_key is None:
            missing.append("KJ_ATLAS_API_KEY")

        if missing:
            raise ValueError(
                f"KJ_ATLAS_RUNTIME_PROFILE={profile} requires an authentication "
                f"means to be configured, but these are unset: {', '.join(missing)}. "
                "Set them, or select local-dev/evaluation for an unauthenticated "
                "runtime (ADR-0072 D3)."
            )

    @model_validator(mode="after")
    def validate_llm_provider_guards(self) -> "Settings":
        detected_legacy = sorted(key for key in LEGACY_ENV_KEYS if key in os.environ)
        if detected_legacy:
            joined = ", ".join(detected_legacy)
            raise ValueError(
                "Legacy env keys are no longer supported. Use KJ_ATLAS_* only: "
                f"{joined}"
            )

        normalized_runtime_profile = self.runtime_profile.strip().lower()
        supported_runtime_profiles = {
            "local-dev",
            "evaluation",
            "enterprise-production",
            "saas-multitenant",
        }
        if normalized_runtime_profile not in supported_runtime_profiles:
            raise ValueError(
                "KJ_ATLAS_RUNTIME_PROFILE must be one of "
                "local-dev|evaluation|enterprise-production|saas-multitenant"
            )
        # ADR-0063 D9-6: saas-multitenant is no longer unconditionally blocked.
        # Startup validation is handled by TrustedSaasRuntimePolicy.validate() and
        # validate_trusted_saas_runtime_preflight() in main.py lifespan.
        self.runtime_profile = normalized_runtime_profile

        _validate_canonical_bearer(
            api_key=self.admin_api_key, api_key_key="KJ_ATLAS_ADMIN_API_KEY"
        )
        if (
            self.api_key is not None
            and self.admin_api_key is not None
            and self.api_key == self.admin_api_key
        ):
            raise ValueError(
                "KJ_ATLAS_API_KEY and KJ_ATLAS_ADMIN_API_KEY must be distinct "
                "credentials so the business plane cannot authorize control-plane operations."
            )
        self._validate_production_authentication_configured(normalized_runtime_profile)

        # A SQLAlchemy dialect being importable does not mean kj-atlas migrations
        # and safety invariants are verified for it. Candidate databases remain
        # fail-closed until their real-DB matrix is complete.
        require_verified_database_url(self.database_url)

        provider = self.llm_provider.strip().lower()
        if provider not in {"none", "local", "local_http", "large-scale", "large_scale", "external", "deepseek"}:
            raise ValueError(f"Unsupported KJ_ATLAS_LLM_PROVIDER: {self.llm_provider}")

        if provider == "deepseek":
            if not self.deepseek_api_key:
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=deepseek requires KJ_ATLAS_DEEPSEEK_API_KEY"
                )
            _validate_trusted_http_endpoint(
                endpoint=self.deepseek_base_url,
                endpoint_key="KJ_ATLAS_DEEPSEEK_BASE_URL",
            )

        if provider in {"large-scale", "large_scale", "external"}:
            if not self.llm_large_scale_opt_in:
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=large-scale requires KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true"
                )
            if not self.llm_escalation_enabled:
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=large-scale requires KJ_ATLAS_LLM_ESCALATION_ENABLED=true"
                )

        if self.local_llm_base_url is not None:
            _validate_trusted_http_endpoint(
                endpoint=self.local_llm_base_url,
                endpoint_key="KJ_ATLAS_LOCAL_LLM_BASE_URL",
            )
        if self.large_scale_llm_base_url is not None:
            _validate_trusted_http_endpoint(
                endpoint=self.large_scale_llm_base_url,
                endpoint_key="KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL",
            )
        _validate_optional_llm_model_id(
            value=self.local_llm_model,
            value_key="KJ_ATLAS_LOCAL_LLM_MODEL",
        )
        _validate_optional_llm_model_id(
            value=self.large_scale_llm_model,
            value_key="KJ_ATLAS_LARGE_SCALE_LLM_MODEL",
        )
        self.large_scale_llm_allowlist = _normalize_llm_allowlist(
            self.large_scale_llm_allowlist
        )
        if provider in {"large-scale", "large_scale", "external"}:
            if (
                self.large_scale_llm_base_url is None
                or self.large_scale_llm_model is None
                or self.large_scale_llm_allowlist is None
            ):
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=large-scale requires its base URL, model, and allowlist"
                )
            large_scale_hostname = (
                urlsplit(self.large_scale_llm_base_url).hostname or ""
            ).lower()
            if large_scale_hostname not in self.large_scale_llm_allowlist.split(","):
                raise ValueError(
                    "KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL host must be in "
                    "KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST"
                )

        self.llm_provider = provider

        normalized_auth_mode = self.access_control_external_http_auth_mode.strip().lower()
        if normalized_auth_mode not in {"none", "oidc", "saml"}:
            raise ValueError(
                "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE must be one of none|oidc|saml"
            )
        self.access_control_external_http_auth_mode = normalized_auth_mode

        normalized_access_control_adapter = self.access_control_adapter.strip().lower()
        if normalized_access_control_adapter not in {"noop", "mock", "external_http"}:
            raise ValueError(
                "KJ_ATLAS_ACCESS_CONTROL_ADAPTER must be one of noop|mock|external_http"
            )
        self.access_control_adapter = normalized_access_control_adapter

        normalized_audit_transport = self.audit_transport.strip().lower()
        if normalized_audit_transport not in {"noop", "http"}:
            raise ValueError("KJ_ATLAS_AUDIT_TRANSPORT must be one of noop|http")
        self.audit_transport = normalized_audit_transport

        _validate_optional_http_integration(
            enabled=normalized_audit_transport == "http",
            endpoint=self.audit_http_endpoint,
            endpoint_key="KJ_ATLAS_AUDIT_HTTP_ENDPOINT",
            api_key=self.audit_http_api_key,
            api_key_key="KJ_ATLAS_AUDIT_HTTP_API_KEY",
        )
        _validate_optional_http_integration(
            enabled=normalized_access_control_adapter == "external_http",
            endpoint=self.access_control_external_http_endpoint,
            endpoint_key="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT",
            api_key=self.access_control_external_http_static_bearer_token,
            api_key_key="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
        )
        if self.access_control_external_http_idp_issuer is not None and (
            normalized_access_control_adapter != "external_http"
            or self.access_control_external_http_endpoint is None
        ):
            raise ValueError(
                "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER requires "
                "KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http and its endpoint"
            )
        _validate_optional_header_value(
            value=self.access_control_external_http_idp_issuer,
            value_key="KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER",
        )
        _validate_optional_header_value(
            value=self.auth_provider_field,
            value_key="KJ_ATLAS_AUTH_PROVIDER_FIELD",
        )
        _validate_optional_header_value(
            value=self.auth_user_field,
            value_key="KJ_ATLAS_AUTH_USER_FIELD",
        )
        _validate_optional_header_value(
            value=self.auth_email_field,
            value_key="KJ_ATLAS_AUTH_EMAIL_FIELD",
        )
        _validate_optional_header_value(
            value=self.auth_name_field,
            value_key="KJ_ATLAS_AUTH_NAME_FIELD",
        )
        _validate_optional_header_value(
            value=self.auth_subject_field,
            value_key="KJ_ATLAS_AUTH_SUBJECT_FIELD",
        )

        normalized_fail_safe_mode = self.access_control_fail_safe_mode.strip().lower()
        if normalized_fail_safe_mode not in {"read_only", "deny"}:
            raise ValueError(
                "KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE must be one of read_only|deny"
            )
        self.access_control_fail_safe_mode = normalized_fail_safe_mode

        self.document_policy_binding_resolver = _validate_trusted_http_resolver(
            resolver=self.document_policy_binding_resolver,
            resolver_key="KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER",
            endpoint=self.document_policy_binding_http_endpoint,
            endpoint_key="KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT",
            api_key=self.document_policy_binding_http_api_key,
            api_key_key="KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_API_KEY",
        )
        self.tenant_capability_resolver = _validate_trusted_http_resolver(
            resolver=self.tenant_capability_resolver,
            resolver_key="KJ_ATLAS_TENANT_CAPABILITY_RESOLVER",
            endpoint=self.tenant_capability_http_endpoint,
            endpoint_key="KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT",
            api_key=self.tenant_capability_http_api_key,
            api_key_key="KJ_ATLAS_TENANT_CAPABILITY_HTTP_API_KEY",
        )

        # SAAS-TENANT-SESSION-BINDING-01 AC-1: format-only, like
        # local_llm_base_url above -- requiredness for saas-multitenant is
        # TrustedSaasRuntimePolicy's job (ADR-0063 D9-6), not Settings'.
        if self.saas_oauth_broker_http_authorize_endpoint is not None:
            _validate_trusted_http_endpoint(
                endpoint=self.saas_oauth_broker_http_authorize_endpoint,
                endpoint_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT",
            )
        if self.saas_oauth_broker_http_token_endpoint is not None:
            _validate_trusted_http_endpoint(
                endpoint=self.saas_oauth_broker_http_token_endpoint,
                endpoint_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT",
            )
        if self.saas_oauth_broker_http_redirect_uri is not None:
            _validate_trusted_http_endpoint(
                endpoint=self.saas_oauth_broker_http_redirect_uri,
                endpoint_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI",
            )
            if urlsplit(self.saas_oauth_broker_http_redirect_uri).path != "/session/callback":
                raise ValueError(
                    "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI path must be "
                    "/session/callback"
                )
        _validate_optional_header_value(
            value=self.saas_oauth_broker_http_client_id,
            value_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID",
        )
        _validate_canonical_bearer(
            api_key=self.saas_oauth_broker_http_client_secret,
            api_key_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET",
        )
        _validate_hex_key(
            value=self.saas_auth_session_hash_key,
            value_key="KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY",
        )

        normalized_reviewer_ref_adapter = self.reviewer_ref_resolver_adapter.strip().lower()
        if normalized_reviewer_ref_adapter not in {"user_id", "sso_subject"}:
            raise ValueError(
                "KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER must be one of user_id|sso_subject"
            )
        self.reviewer_ref_resolver_adapter = normalized_reviewer_ref_adapter

        if self.ce4_equivalence_mode != "equivalence_and_bundle_hash":
            raise ValueError(
                "KJ_ATLAS_CE4_EQUIVALENCE_MODE must be equivalence_and_bundle_hash"
            )
        if not self.ce4_dry_run_enforce_no_side_effect:
            raise ValueError(
                "KJ_ATLAS_CE4_DRY_RUN_ENFORCE_NO_SIDE_EFFECT must remain true in CE4"
            )
        if not self.ce4_audit_require_all_events:
            raise ValueError(
                "KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS must remain true in CE4"
            )

        # ADR-0063 D4: validate JWT algorithm allowlist.
        _KNOWN_JWT_ALGORITHMS = frozenset(
            {"RS256", "RS384", "RS512", "ES256", "ES384", "ES512", "PS256", "PS384", "PS512"}
        )
        raw_algorithms = [
            alg.strip() for alg in self.jwt_algorithms.split(",") if alg.strip()
        ]
        if not raw_algorithms:
            raise ValueError("KJ_ATLAS_JWT_ALGORITHMS must contain at least one algorithm")
        if any(alg.startswith("HS") for alg in raw_algorithms):
            raise ValueError(
                "KJ_ATLAS_JWT_ALGORITHMS must not contain HMAC algorithms (HS256/HS384/HS512)"
            )
        unknown = [alg for alg in raw_algorithms if alg not in _KNOWN_JWT_ALGORITHMS]
        if unknown:
            raise ValueError(
                "KJ_ATLAS_JWT_ALGORITHMS contains unknown algorithms: "
                + ", ".join(unknown)
            )
        self.jwt_algorithms = ",".join(raw_algorithms)

        # ADR-0063 D8: validate tenant claim name.
        claim_name = self.tenant_claim_name.strip()
        if not claim_name:
            raise ValueError("KJ_ATLAS_TENANT_CLAIM_NAME must not be empty")
        if len(claim_name) > 256:
            raise ValueError("KJ_ATLAS_TENANT_CLAIM_NAME must be ≤ 256 characters")
        if claim_name != self.tenant_claim_name:
            raise ValueError("KJ_ATLAS_TENANT_CLAIM_NAME must not have leading/trailing whitespace")
        if any(not c.isprintable() for c in claim_name):
            raise ValueError("KJ_ATLAS_TENANT_CLAIM_NAME must be printable")
        if " " in claim_name:
            raise ValueError("KJ_ATLAS_TENANT_CLAIM_NAME must not contain spaces")
        self.tenant_claim_name = claim_name

        # ADR-0063 correction #2: validate trusted proxy CIDRs.
        normalized_proxies = _validate_trusted_proxies(self.trusted_proxies)
        self.trusted_proxies = normalized_proxies

        return self


settings = Settings()
