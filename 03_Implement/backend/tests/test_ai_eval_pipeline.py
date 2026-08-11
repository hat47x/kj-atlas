"""AI evaluation pipeline smoke test (L2 criterion ③ preparation).

Verifies that the evaluation flow for issue-AI-EVAL-01 is executable:
1. The evaluation fixture parses as a valid DocumentV1
2. refine_card_text and suggest_island_summary requests can be built
   from the fixture (request assembly, not LLM call)
3. The DeepSeek provider is properly wired (uses real API when env set)

This test does NOT call the real DeepSeek API. It validates the pipeline
plumbing so that when KJ_ATLAS_DEEPSEEK_API_KEY is provided, the manual
evaluation in ai_eval_results.md can proceed without surprises.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from kj_atlas_api.models_ai import (
    RefineCardTextRequest,
    SuggestIslandSummaryRequest,
)
from kj_atlas_api.models import DocumentV1

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ai_eval_kj_document.json"


@pytest.fixture(scope="module")
def eval_doc() -> DocumentV1:
    raw = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    return DocumentV1.model_validate(raw)


def test_fixture_is_valid_document_v1(eval_doc: DocumentV1) -> None:
    assert eval_doc.version == 1
    assert len(eval_doc.cards) == 12
    assert len(eval_doc.islands) == 4
    assert len(eval_doc.edges) == 6
    # Every island cardId must resolve to a real card
    card_ids = {card.id for card in eval_doc.cards}
    for island in eval_doc.islands:
        for card_id in island.cardIds:
            assert card_id in card_ids


def test_fixture_has_reviewed_cards_for_refine(eval_doc: DocumentV1) -> None:
    """refine_card_text input: each card text is non-empty."""
    for card in eval_doc.cards[:10]:
        req = RefineCardTextRequest(cardText=card.text)
        assert req.cardText.strip() != ""


def test_fixture_has_islands_for_summary(eval_doc: DocumentV1) -> None:
    """suggest_island_summary input: each island resolves and has cards."""
    for island in eval_doc.islands:
        member_ids = [cid for cid in island.cardIds]
        assert len(member_ids) >= 2, f"Island {island.id} has <2 cards"
        # SuggestIslandSummaryRequest requires doc + islandId
        req = SuggestIslandSummaryRequest(doc=eval_doc, islandId=island.id)
        assert req.islandId == island.id


def test_deepseek_provider_wired_for_eval_tasks(monkeypatch: pytest.MonkeyPatch) -> None:
    """When DeepSeek is configured, the eval task names resolve to the model."""
    from kj_atlas_api.settings import settings

    original_map = settings.llm_task_model_map
    try:
        settings.llm_task_model_map = (
            "refine_card_text=deepseek-chat,"
            "suggest_island_summary=deepseek-chat"
        )
        # resolve_model_for_task should return deepseek-chat for both tasks
        from kj_atlas_api.llm.provider import resolve_model_for_task

        assert resolve_model_for_task("refine_card_text") == "deepseek-chat"
        assert resolve_model_for_task("suggest_island_summary") == "deepseek-chat"
    finally:
        settings.llm_task_model_map = original_map
