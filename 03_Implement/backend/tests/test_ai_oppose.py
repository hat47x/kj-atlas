"""AI-OPPOSE-01 (M4): opposing-viewpoint / evidence-gap proposal (proposal-only).

Covers the proposal route's happy path (returns a proposal-only observation
grounded in the doc's structure), the SafeMode unreviewed boundary, and the
invalid-target rejection. The LLM is stubbed at generate_with_fallback so no
provider or network is needed.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from kj_atlas_api.model_registry_repository import register_model, register_provider
from kj_atlas_api.routes import ai
from kj_atlas_api.db import get_db
from kj_atlas_api.llm.provider import LLMResponse
from kj_atlas_api.main import app
from kj_atlas_api.models import Base, TenantRow
from kj_atlas_api.settings import settings

_NOW = "2026-08-15T00:00:00+00:00"


def _doc(target_id: str = "c-claim") -> dict:
    return {
        "version": 1,
        "id": "oppose-doc",
        "title": "opposing viewpoint test",
        "createdAt": "2026-08-15T00:00:00Z",
        "updatedAt": "2026-08-15T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [
            {"id": "c-claim", "text": "待ち時間が長いと利用者は離れる", "x": 0, "y": 0, "textReviewed": True},
            {"id": "c-counter", "text": "待ち時間が長くても常連は残る", "x": 200, "y": 0, "textReviewed": True},
        ],
        "edges": [{"id": "e1", "fromId": "c-claim", "toId": "c-counter", "type": "negate"}],
        "islands": [{"id": "i1", "cardIds": ["c-claim", "c-counter"]}],
        "readingOrder": ["i1"],
        "evidenceLinks": [{"id": "ev-1", "fromCardId": "c-claim", "toCardId": "c-counter", "type": "contradicts"}],
    }


@contextmanager
def _client(tmp_path) -> Iterator[TestClient]:
    engine = create_engine(f"sqlite:///{tmp_path / 'ai_oppose.sqlite3'}")
    session_local = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)
    with session_local() as db:
        db.add(TenantRow(id="local-default", display_name="Local Default", lifecycle_state="active", created_at=_NOW, updated_at=_NOW))
        # AI-MODEL-GOVERNANCE-02: the AI route resolves the default model and
        # _assert_model_allowed now requires an active registered model, so the
        # fixture must register the provider + default model (as the env seed
        # does in production).
        register_provider(
            db,
            provider_id="local",
            provider_kind="local",
            display_name="Local LLM (test)",
            base_url="http://127.0.0.1:11434",
            api_key_ref=None,
            occurred_at=_NOW,
        )
        register_model(db, model_id="default", provider_id="local", display_name="default", capabilities="intermediate,generate", occurred_at=_NOW)
        db.commit()

    def _get_test_db():
        db = session_local()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_test_db
    # AI-MODEL-GOVERNANCE-02 provider-match check: the runtime provider must be
    # the registered one (local). Default llm_provider is "none", which would
    # make every _assert_model_allowed call 503 model_provider_unavailable.
    original_provider = settings.llm_provider
    settings.llm_provider = "local"
    try:
        with TestClient(app) as client:
            yield client
    finally:
        settings.llm_provider = original_provider
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def _stub_response(monkeypatch, raw_text: str) -> None:
    """Patch generate_with_fallback via monkeypatch so it auto-restores and
    never leaks into other test modules in the same pytest process."""
    from kj_atlas_api.llm.provider import _new_metadata

    def _fake_generate(_req):
        return LLMResponse(raw_text=raw_text, metadata=_new_metadata(provider_kind="local", provider_name="local", model_id="default", transport="none"))
    import kj_atlas_api.routes.ai as ai_module
    monkeypatch.setattr(ai_module, "generate_with_fallback", _fake_generate)


def _put_doc(client: TestClient, doc: dict) -> None:
    put = client.put("/docs/oppose-doc", json=doc)
    assert put.status_code == 200, put.text


def test_propose_opposing_viewpoint_returns_proposal_only(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", None)
    _stub_response(monkeypatch, 
        '{"opposingText":"逆の状況でも同じ帰結が起きる可能性があり、根拠の一般性が不足しています。","evidenceGap":true,"rationale":"反例カードが根拠として接続されていません。","warnings":[]}'
    )
    with _client(tmp_path) as client:
        _put_doc(client, _doc())
        resp = client.post("/ai/proposals/opposing-viewpoint", json={"doc": _doc(), "targetCardId": "c-claim"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["type"] == "opposing_viewpoint"
    assert body["status"] == "proposed"  # proposal-only: never applied
    assert body["reviewState"] == "unreviewed"
    assert body["targetCardId"] == "c-claim"
    assert body["evidenceGap"] is True
    assert body["opposingText"]




def test_route_sends_target_ir_and_human_contradiction_state(tmp_path, monkeypatch) -> None:
    """production routeが対象周辺IRをpromptとLLMRequest.inputsの両方へ渡す。"""
    monkeypatch.setattr(settings, "api_key", None)
    doc = _doc()
    raw_target_text = "  待ち時間が長いと\t利用者は離れる  "
    doc["cards"][0]["text"] = raw_target_text
    doc["evidenceLinks"][0]["contradictionState"] = "held"
    captured = {}

    from kj_atlas_api.llm.provider import _new_metadata

    def _fake_generate(req):
        captured["request"] = req
        return LLMResponse(
            raw_text='{"opposingText":"対象主張への別視点です。","evidenceGap":false,"rationale":"記録済み構造を参照。","warnings":[]}',
            metadata=_new_metadata(
                provider_kind="local",
                provider_name="local",
                model_id="default",
                transport="none",
            ),
        )

    monkeypatch.setattr(ai, "generate_with_fallback", _fake_generate)
    with _client(tmp_path) as client:
        _put_doc(client, doc)
        resp = client.post(
            "/ai/proposals/opposing-viewpoint",
            json={"doc": doc, "targetCardId": "c-claim"},
        )

    assert resp.status_code == 200, resp.text
    request = captured["request"]
    assert request.inputs is not None
    assert {card["id"] for card in request.inputs["cards"]} >= {"c-claim", "c-counter"}
    target_ir_text = next(
        card["text"] for card in request.inputs["cards"] if card["id"] == "c-claim"
    )
    assert target_ir_text == raw_target_text.replace("\t", "")
    assert target_ir_text != raw_target_text
    assert (
        "Target card: " + json.dumps({"id": "c-claim", "text": target_ir_text})
        in request.prompt
    )
    assert json.dumps({"id": "c-claim", "text": raw_target_text}) not in request.prompt
    assert "contradictionState=held" in request.prompt
    assert "existing HUMAN judgement" in request.prompt

def test_propose_opposing_viewpoint_rejects_unreviewed(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", None)
    _stub_response(monkeypatch, '{"opposingText":"x","evidenceGap":false,"rationale":"r","warnings":[]}')
    doc = _doc()
    doc["cards"][0]["textReviewed"] = None  # unreviewed -> fail-closed
    with _client(tmp_path) as client:
        _put_doc(client, doc)
        resp = client.post("/ai/proposals/opposing-viewpoint", json={"doc": doc, "targetCardId": "c-claim"})
    assert resp.status_code == 422, resp.text
    assert resp.json()["detail"]["code"] == "unreviewed_text_not_allowed"


def test_propose_opposing_viewpoint_rejects_unknown_target(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "api_key", None)
    _stub_response(monkeypatch, '{"opposingText":"x","evidenceGap":false,"rationale":"r","warnings":[]}')
    with _client(tmp_path) as client:
        _put_doc(client, _doc())
        resp = client.post("/ai/proposals/opposing-viewpoint", json={"doc": _doc(), "targetCardId": "does-not-exist"})
    assert resp.status_code == 422, resp.text


def test_opposing_viewpoint_prompt_is_grounded_in_doc() -> None:
    """The prompt must carry the target card, all cards, and evidence links, so
    the model proposes only from the doc's structure (M4)."""
    from kj_atlas_api.models import DocumentV1
    from kj_atlas_api.models_ai import ProposeOpposingViewpointRequest

    payload = ProposeOpposingViewpointRequest.model_validate({"doc": DocumentV1.model_validate(_doc()), "targetCardId": "c-claim"})
    built = ai._build_opposing_viewpoint_prompt(payload)
    assert "c-claim" in built
    assert "c-counter" in built
    assert "contradicts" in built
