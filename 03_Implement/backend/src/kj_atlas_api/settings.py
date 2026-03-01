from pydantic import Field
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
    llm_fallback_to_none: bool = Field(
        default=True,
        alias="LLM_FALLBACK_TO_NONE",
    )
    api_key: str | None = Field(
        default=None,
        alias="API_KEY",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
