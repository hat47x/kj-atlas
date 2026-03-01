from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./kj_atlas.db",
        alias="DATABASE_URL",
    )
    llm_provider: str = Field(
        default="none",
        alias="LLM_PROVIDER",
    )
    local_llm_base_url: str | None = Field(
        default=None,
        alias="LOCAL_LLM_BASE_URL",
    )
    local_llm_model: str | None = Field(
        default=None,
        alias="LOCAL_LLM_MODEL",
    )
    large_scale_llm_base_url: str | None = Field(
        default=None,
        alias="LARGE_SCALE_LLM_BASE_URL",
    )
    large_scale_llm_model: str | None = Field(
        default=None,
        alias="LARGE_SCALE_LLM_MODEL",
    )
    llm_escalation_enabled: bool = Field(
        default=False,
        alias="LLM_ESCALATION_ENABLED",
    )
    llm_large_scale_opt_in: bool = Field(
        default=False,
        alias="LLM_LARGE_SCALE_OPT_IN",
    )
    large_scale_llm_allowlist: str | None = Field(
        default=None,
        alias="LARGE_SCALE_LLM_ALLOWLIST",
    )
    llm_fallback_to_none: bool = Field(
        default=True,
        alias="LLM_FALLBACK_TO_NONE",
    )
    api_key: str | None = Field(
        default=None,
        alias="API_KEY",
    )
    audit_export_enabled: bool = Field(
        default=False,
        alias="AUDIT_EXPORT_ENABLED",
    )
    audit_transport: str = Field(
        default="noop",
        alias="AUDIT_TRANSPORT",
    )
    audit_http_endpoint: str | None = Field(
        default=None,
        alias="AUDIT_HTTP_ENDPOINT",
    )
    audit_http_api_key: str | None = Field(
        default=None,
        alias="AUDIT_HTTP_API_KEY",
    )
    audit_http_timeout_seconds: float = Field(
        default=2.0,
        alias="AUDIT_HTTP_TIMEOUT_SECONDS",
    )
    audit_queue_size: int = Field(
        default=100,
        alias="AUDIT_QUEUE_SIZE",
    )
    audit_allow_in_safe_mode: bool = Field(
        default=False,
        alias="AUDIT_ALLOW_IN_SAFE_MODE",
    )
    access_control_adapter: str = Field(
        default="noop",
        alias="ACCESS_CONTROL_ADAPTER",
    )
    access_control_fail_safe_mode: str = Field(
        default="read_only",
        alias="ACCESS_CONTROL_FAIL_SAFE_MODE",
    )
    access_control_http_endpoint: str | None = Field(
        default=None,
        alias="ACCESS_CONTROL_HTTP_ENDPOINT",
    )
    access_control_http_api_key: str | None = Field(
        default=None,
        alias="ACCESS_CONTROL_HTTP_API_KEY",
    )
    access_control_http_timeout_seconds: float = Field(
        default=2.0,
        alias="ACCESS_CONTROL_HTTP_TIMEOUT_SECONDS",
    )
    access_control_mock_allow: bool = Field(
        default=True,
        alias="ACCESS_CONTROL_MOCK_ALLOW",
    )
    access_control_mock_reason: str | None = Field(
        default=None,
        alias="ACCESS_CONTROL_MOCK_REASON",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @model_validator(mode="after")
    def validate_llm_provider_guards(self) -> "Settings":
        provider = self.llm_provider.strip().lower()
        if provider not in {"none", "local", "local_http", "large-scale", "large_scale", "external"}:
            raise ValueError(f"Unsupported LLM_PROVIDER: {self.llm_provider}")

        if provider in {"large-scale", "large_scale", "external"}:
            if not self.llm_large_scale_opt_in:
                raise ValueError("LLM_PROVIDER=large-scale requires LLM_LARGE_SCALE_OPT_IN=true")
            if not self.llm_escalation_enabled:
                raise ValueError("LLM_PROVIDER=large-scale requires LLM_ESCALATION_ENABLED=true")

        return self


settings = Settings()
