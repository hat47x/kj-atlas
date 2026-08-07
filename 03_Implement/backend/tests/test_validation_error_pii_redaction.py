"""SEC-VALIDATION-LEAK-01: 422 validation responses must not echo rejected PII.

The global RequestValidationError handler previously returned exc.errors()
unchanged, which (pydantic v2 default) includes the rejected raw value
under `input`. For /ai/* endpoints that accept a DocumentV1, an
opaque-id violation in reviewAttribution.reviewerRef (e.g. an email)
was therefore reflected back verbatim in the 422 body.
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from kj_atlas_api.main import app

# Email addresses and provider-prefixed identifiers are rejected by the
# opaque-id validator on ReviewAttribution.reviewerRef / ownerRef.
PII_REVIEWER = "alice@example.com"
PII_OWNER = "sso:alice@example.com"


def _sample_doc(doc_id: str, reviewer_ref: str, owner_ref: str) -> dict:
    return {
        "version": 1,
        "id": doc_id,
        "title": "validation-error-pii",
        "createdAt": "2026-02-11T00:00:00Z",
        "updatedAt": "2026-02-11T00:00:00Z",
        "transform": {"panX": 0, "panY": 0, "zoom": 1},
        "cards": [{"id": "card-1", "text": "alpha", "x": 0, "y": 0}],
        "edges": [],
        "islands": [{"id": "island-1", "cardIds": ["card-1"]}],
        "reviewAttribution": {
            "schemaVersion": "1.0.0",
            "reviewState": "human_reviewed",
            "reviewedAt": "2026-02-11T00:02:00Z",
            "reviewerRef": reviewer_ref,
            "ownerRef": owner_ref,
            "auditRecordedAt": "2026-02-11T00:02:00Z",
        },
    }


def test_check_narrative_422_does_not_echo_rejected_pii() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/ai/check-narrative",
            json={
                "doc": _sample_doc("doc-pii-check-narrative", PII_REVIEWER, PII_OWNER),
            },
        )

        assert response.status_code == 422
        body_text = response.text
        assert PII_REVIEWER not in body_text
        assert PII_OWNER not in body_text
        # The rejection must still be reported (with location), just without input.
        assert "reviewerRef" in body_text or "reviewAttribution" in body_text


def test_generate_narrative_422_does_not_echo_rejected_pii() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/ai/generate-narrative",
            json={
                "doc": _sample_doc("doc-pii-generate-narrative", PII_REVIEWER, PII_OWNER),
            },
        )

        assert response.status_code == 422
        body_text = response.text
        assert PII_REVIEWER not in body_text
        assert PII_OWNER not in body_text


def test_ai_validation_error_detail_is_structured_without_input() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/ai/check-narrative",
            json={"doc": _sample_doc("doc-pii-structure", PII_REVIEWER, PII_OWNER)},
        )

        assert response.status_code == 422
        detail = response.json()["detail"]
        assert isinstance(detail, list)
        for error in detail:
            assert "input" not in error
            assert "loc" in error
