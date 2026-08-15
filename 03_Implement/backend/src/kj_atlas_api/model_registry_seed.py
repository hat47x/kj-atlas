"""AI-MODEL-GOVERNANCE-01 U4: seed the env-configured provider into the registry.

Runs at startup. If `KJ_ATLAS_LLM_PROVIDER` is `deepseek` or `local`, the
corresponding provider + its default model are merged into the registry so the
admin surface can see/manage what env vars configured. Idempotent (db.merge).
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from kj_atlas_api.db import SessionLocal
from kj_atlas_api.model_registry_repository import register_model, register_provider
from kj_atlas_api.settings import settings

logger = logging.getLogger(__name__)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def seed_registry_from_env(session_factory=SessionLocal) -> None:
    """Seed the env-configured provider/model into the registry.

    `session_factory` is injectable for tests (default: the app engine).
    """
    provider = settings.llm_provider.strip().lower()
    if provider not in {"deepseek", "local", "local_http"}:
        return

    occurred_at = _now_iso()
    try:
        db = session_factory()
        try:
            if provider == "deepseek":
                provider_id = "deepseek"
                register_provider(
                    db,
                    provider_id=provider_id,
                    provider_kind="deepseek",
                    display_name="DeepSeek (env)",
                    base_url=settings.deepseek_base_url,
                    api_key_ref="KJ_ATLAS_DEEPSEEK_API_KEY",
                    occurred_at=occurred_at,
                )
                register_model(
                    db,
                    model_id=settings.deepseek_model,
                    provider_id=provider_id,
                    display_name=settings.deepseek_model,
                    capabilities="intermediate,generate",
                    occurred_at=occurred_at,
                )
            else:
                provider_id = "local"
                register_provider(
                    db,
                    provider_id=provider_id,
                    provider_kind="local",
                    display_name="Local LLM (env)",
                    base_url=settings.local_llm_base_url,
                    api_key_ref=None,
                    occurred_at=occurred_at,
                )
                default_model = settings.local_llm_model or "default"
                register_model(
                    db,
                    model_id=default_model,
                    provider_id=provider_id,
                    display_name=default_model,
                    capabilities="intermediate,generate",
                    occurred_at=occurred_at,
                )
            db.commit()
        finally:
            db.close()
    except Exception as exc:  # seeding must never block startup
        logger.warning("model registry env seeding failed; continuing", extra={"error": str(exc)})
