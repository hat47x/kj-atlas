from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

LEGACY_ENV_COMPAT_DEADLINE = date(2026, 12, 31)


def _current_utc_date() -> date:
    return datetime.now(timezone.utc).date()


def _alias(name: str) -> AliasChoices:
    return AliasChoices(f"KJ_ATLAS_{name}", name)


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./kj_atlas.db",
        validation_alias=AliasChoices("KJ_ATLAS_DATABASE_URL", "DATABASE_URL"),
    )
    llm_provider: str = Field(
        default="none",
        validation_alias=AliasChoices("KJ_ATLAS_LLM_PROVIDER", "LLM_PROVIDER"),
    )
    local_llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_LOCAL_LLM_BASE_URL", "LOCAL_LLM_BASE_URL"),
    )
    local_llm_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_LOCAL_LLM_MODEL", "LOCAL_LLM_MODEL"),
    )
    large_scale_llm_base_url: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_LARGE_SCALE_LLM_BASE_URL", "LARGE_SCALE_LLM_BASE_URL"),
    )
    large_scale_llm_model: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_LARGE_SCALE_LLM_MODEL", "LARGE_SCALE_LLM_MODEL"),
    )
    llm_escalation_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("KJ_ATLAS_LLM_ESCALATION_ENABLED", "LLM_ESCALATION_ENABLED"),
    )
    llm_large_scale_opt_in: bool = Field(
        default=False,
        validation_alias=AliasChoices("KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN", "LLM_LARGE_SCALE_OPT_IN"),
    )
    large_scale_llm_allowlist: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_LARGE_SCALE_LLM_ALLOWLIST", "LARGE_SCALE_LLM_ALLOWLIST"),
    )
    llm_fallback_to_none: bool = Field(
        default=True,
        validation_alias=AliasChoices("KJ_ATLAS_LLM_FALLBACK_TO_NONE", "LLM_FALLBACK_TO_NONE"),
    )
    api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_API_KEY", "API_KEY"),
    )
    audit_export_enabled: bool = Field(
        default=False,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_EXPORT_ENABLED", "AUDIT_EXPORT_ENABLED"),
    )
    audit_transport: str = Field(
        default="noop",
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_TRANSPORT", "AUDIT_TRANSPORT"),
    )
    audit_http_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_HTTP_ENDPOINT", "AUDIT_HTTP_ENDPOINT"),
    )
    audit_http_api_key: str | None = Field(
        default=None,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_HTTP_API_KEY", "AUDIT_HTTP_API_KEY"),
    )
    audit_http_timeout_seconds: float = Field(
        default=2.0,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_HTTP_TIMEOUT_SECONDS", "AUDIT_HTTP_TIMEOUT_SECONDS"),
    )
    audit_queue_size: int = Field(
        default=100,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_QUEUE_SIZE", "AUDIT_QUEUE_SIZE"),
    )
    audit_allow_in_safe_mode: bool = Field(
        default=False,
        validation_alias=AliasChoices("KJ_ATLAS_AUDIT_ALLOW_IN_SAFE_MODE", "AUDIT_ALLOW_IN_SAFE_MODE"),
    )
    access_control_adapter: str = Field(
        default="noop",
        validation_alias=AliasChoices("KJ_ATLAS_ACCESS_CONTROL_ADAPTER", "ACCESS_CONTROL_ADAPTER"),
    )
    access_control_fail_safe_mode: str = Field(
        default="read_only",
        validation_alias=AliasChoices("KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE", "ACCESS_CONTROL_FAIL_SAFE_MODE"),
    )
    access_control_external_http_endpoint: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT", "ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT"
        ),
    )
    access_control_external_http_timeout_seconds: float = Field(
        default=1.5,
        validation_alias=AliasChoices(
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS",
            "ACCESS_CONTROL_EXTERNAL_HTTP_TIMEOUT_SECONDS",
        ),
    )
    access_control_external_http_auth_mode: str = Field(
        default="none",
        validation_alias=AliasChoices(
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE", "ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE"
        ),
    )
    access_control_external_http_static_bearer_token: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
            "ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
        ),
    )
    access_control_external_http_idp_issuer: str | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER", "ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER"
        ),
    )
    allow_jit_provisioning: bool = Field(
        default=True,
        validation_alias=AliasChoices("KJ_ATLAS_ALLOW_JIT_PROVISIONING", "ALLOW_JIT_PROVISIONING"),
    )
    auth_provider_field: str = Field(
        default="x-auth-provider",
        validation_alias=AliasChoices("KJ_ATLAS_AUTH_PROVIDER_FIELD", "AUTH_PROVIDER_FIELD"),
    )
    auth_user_field: str = Field(
        default="x-forwarded-user",
        validation_alias=AliasChoices("KJ_ATLAS_AUTH_USER_FIELD", "AUTH_USER_FIELD"),
    )
    auth_email_field: str = Field(
        default="x-forwarded-email",
        validation_alias=AliasChoices("KJ_ATLAS_AUTH_EMAIL_FIELD", "AUTH_EMAIL_FIELD"),
    )
    auth_name_field: str = Field(
        default="x-forwarded-name",
        validation_alias=AliasChoices("KJ_ATLAS_AUTH_NAME_FIELD", "AUTH_NAME_FIELD"),
    )
    auth_subject_field: str = Field(
        default="x-auth-subject",
        validation_alias=AliasChoices("KJ_ATLAS_AUTH_SUBJECT_FIELD", "AUTH_SUBJECT_FIELD"),
    )
    reviewer_ref_resolver_adapter: str = Field(
        default="user_id",
        validation_alias=AliasChoices(
            "KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER", "REVIEWER_REF_RESOLVER_ADAPTER"
        ),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_legacy_env_compatibility_window(self) -> "Settings":
        if _current_utc_date() <= LEGACY_ENV_COMPAT_DEADLINE:
            return self

        for field in type(self).model_fields.values():
            validation_alias = field.validation_alias
            if not isinstance(validation_alias, AliasChoices):
                continue
            choices = list(validation_alias.choices)
            if len(choices) < 2:
                continue
            canonical_key = str(choices[0])
            legacy_key = str(choices[1])
            if legacy_key in environ and canonical_key not in environ:
                raise ValueError(
                    f"{legacy_key} is deprecated after {LEGACY_ENV_COMPAT_DEADLINE.isoformat()}; "
                    f"use {canonical_key}"
                )
        return self

    @model_validator(mode="after")
    def validate_llm_provider_guards(self) -> "Settings":
        provider = self.llm_provider.strip().lower()
        if provider not in {"none", "local", "local_http", "large-scale", "large_scale", "external"}:
            raise ValueError(f"Unsupported KJ_ATLAS_LLM_PROVIDER: {self.llm_provider}")

        if provider in {"large-scale", "large_scale", "external"}:
            if not self.llm_large_scale_opt_in:
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=large-scale requires KJ_ATLAS_LLM_LARGE_SCALE_OPT_IN=true"
                )
            if not self.llm_escalation_enabled:
                raise ValueError(
                    "KJ_ATLAS_LLM_PROVIDER=large-scale requires KJ_ATLAS_LLM_ESCALATION_ENABLED=true"
                )

        if self.access_control_external_http_auth_mode not in {"none", "oidc", "saml"}:
            raise ValueError(
                "KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE must be one of none|oidc|saml"
            )

        if self.reviewer_ref_resolver_adapter not in {"user_id", "sso_subject"}:
            raise ValueError(
                "KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER must be one of user_id|sso_subject"
            )

        return self


settings = Settings()
