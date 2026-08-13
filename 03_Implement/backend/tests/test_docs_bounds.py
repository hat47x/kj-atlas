"""SEC-DOC-BOUND-01: document size + card count bounds on PUT /docs."""

from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app
from kj_atlas_api.settings import settings


def _payload(doc_id: str, cards: int) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "bounds",
        "createdAt": "2026-08-12T00:00:00Z",
        "updatedAt": "2026-08-12T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": f"c{i}", "text": "x", "x": i, "y": 0} for i in range(cards)],
        "edges": [],
        "islands": [],
    }


def test_put_rejects_document_over_card_count_limit(monkeypatch) -> None:
    monkeypatch.setattr(settings, "max_document_cards", 3)
    with TestClient(app) as client:
        resp = client.put("/docs/bounds-cc", json=_payload("bounds-cc", 4))
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "document_too_many_cards"


def test_put_rejects_document_over_byte_limit(monkeypatch) -> None:
    # A tiny byte ceiling forces the size check without a huge payload.
    monkeypatch.setattr(settings, "max_document_bytes", 200)
    with TestClient(app) as client:
        resp = client.put("/docs/bounds-bytes", json=_payload("bounds-bytes", 3))
    assert resp.status_code == 413
    assert resp.json()["detail"]["code"] == "document_too_large"


def test_put_accepts_document_under_limits(monkeypatch) -> None:
    monkeypatch.setattr(settings, "max_document_cards", 10_000)
    monkeypatch.setattr(settings, "max_document_bytes", 20 * 1024 * 1024)
    with TestClient(app) as client:
        resp = client.put("/docs/bounds-ok", json=_payload("bounds-ok", 3))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["cards"]) == 3


def test_settings_defaults_are_bounded() -> None:
    # The defaults must be sane: byte ceiling matches the inquiry bundle (20 MiB)
    # and the card ceiling is generous but finite.
    assert settings.max_document_bytes == 20 * 1024 * 1024
    assert settings.max_document_cards > 0
