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
from fastapi.testclient import TestClient

from kj_atlas_api.llm.provider import LLMCallMetadata, LLMResponse
from kj_atlas_api.main import app
from kj_atlas_api.models_ai import (
    RefineCardTextRequest,
    SuggestIslandSummaryRequest,
)
from kj_atlas_api.models import DocumentV1
from kj_atlas_api.routes import ai

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "ai_eval_kj_document.json"


def _stub_metadata() -> LLMCallMetadata:
    return LLMCallMetadata(
        provider_kind="deepseek",
        provider_name="deepseek",
        model_id="deepseek-chat",
        transport="http",
        requested_at="2026-08-11T00:00:00Z",
        trace_id="llm-eval-mock",
    )


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


# --- Mock endpoint-level evaluation flow (L2 criterion ③ rehearsal) ---
#
# These tests stub the LLM provider with fixed responses and exercise the
# actual /ai/ endpoints, proving that the evaluation procedure in
# ai_eval_results.md will work end-to-end once a real DeepSeek key is set.
# They do NOT call the real API.


def test_refine_card_text_endpoint_mock_eval(monkeypatch: pytest.MonkeyPatch, eval_doc: DocumentV1) -> None:
    """POST /ai/refine-card-text returns a parsed refined text from the stub."""

    def _fake_generate(req):
        assert req.task == "refine_card_text"
        return LLMResponse(
            raw_text='{"refinedText": "高齢者が買い物に出られない", "reasoning": "主語と動作を明確にした"}',
            metadata=_stub_metadata(),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    card = eval_doc.cards[0]
    with TestClient(app) as client:
        resp = client.post("/ai/refine-card-text", json={"cardText": card.text})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["refinedText"] == "高齢者が買い物に出られない"
    assert body["reasoning"]


def test_refine_card_text_eval_covers_all_fixture_cards(
    monkeypatch: pytest.MonkeyPatch, eval_doc: DocumentV1
) -> None:
    """The 10-sample eval set can be driven through the endpoint for every card."""
    calls: list[str] = []

    def _fake_generate(req):
        calls.append(req.prompt)
        return LLMResponse(
            raw_text='{"refinedText": "改善されたカード文", "reasoning": "mock"}',
            metadata=_stub_metadata(),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    with TestClient(app) as client:
        for card in eval_doc.cards[:10]:
            resp = client.post("/ai/refine-card-text", json={"cardText": card.text})
            assert resp.status_code == 200, resp.text
    assert len(calls) == 10


def test_suggest_island_summary_endpoint_mock_eval(
    monkeypatch: pytest.MonkeyPatch, eval_doc: DocumentV1
) -> None:
    """POST /ai/suggest-island-summary returns a summary text from the stub."""

    def _fake_generate(req):
        assert req.task == "suggest_island_summary"
        return LLMResponse(
            raw_text='{"summaryText": "高齢者の買い物困難が深刻化している", "groundingIds": ["c01", "c02", "c03"], "warnings": []}',
            metadata=_stub_metadata(),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    payload = {"doc": eval_doc.model_dump(mode="json"), "islandId": "i1"}
    with TestClient(app) as client:
        resp = client.post("/ai/suggest-island-summary", json=payload)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["summaryText"] == "高齢者の買い物困難が深刻化している"
    assert body["groundingIds"] == ["c01", "c02", "c03"]


def test_suggest_island_summary_eval_covers_all_fixture_islands(
    monkeypatch: pytest.MonkeyPatch, eval_doc: DocumentV1
) -> None:
    """The 4-island eval set can be driven through the endpoint for every island."""
    calls: list[str] = []

    # The summary's groundingIds must be members of the requested island.
    # Stub echoes the island's own member cards so the validation passes.
    island_members = {island.id: island.cardIds for island in eval_doc.islands}

    def _fake_generate(req):
        calls.append(req.prompt)
        # Parse islandId from the request payload (added to prompt by builder)
        island_id = req.prompt.split('id="', 1)[1].split('"', 1)[0] if 'id="' in req.prompt else island_members["i1"][0]
        member = island_members.get(island_id, ["c01"])[0]
        return LLMResponse(
            raw_text=f'{{"summaryText": "島の表札候補", "groundingIds": ["{member}"], "warnings": []}}',
            metadata=_stub_metadata(),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    doc_json = eval_doc.model_dump(mode="json")
    with TestClient(app) as client:
        for island in eval_doc.islands:
            payload = {"doc": doc_json, "islandId": island.id}
            resp = client.post("/ai/suggest-island-summary", json=payload)
            assert resp.status_code == 200, resp.text
    assert len(calls) == 4
