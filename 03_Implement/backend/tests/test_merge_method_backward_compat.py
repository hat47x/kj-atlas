from pydantic import ValidationError

from kj_atlas_api.models import MergeSuggestionDecision


def _decision_payload() -> dict[str, object]:
    return {
        "id": "d1",
        "groupId": "g1",
        "decision": "accept",
        "decidedAt": "2026-09-04T00:00:00Z",
        "cardIds": ["c1", "c2"],
        "mergedTextDraft": "共通する意味を保った統合案",
        "editedText": "共通する意味を保った統合案",
    }


def test_legacy_merge_decision_without_method_still_round_trips_without_inference() -> None:
    decision = MergeSuggestionDecision.model_validate(_decision_payload())
    dumped = decision.model_dump(mode="json")

    assert decision.mergeMethod is None
    assert "mergeMethod" not in dumped


def test_new_merge_decision_preserves_kernel_fusion_method() -> None:
    payload = _decision_payload()
    payload["mergeMethod"] = "kernel_fusion"

    decision = MergeSuggestionDecision.model_validate(payload)
    dumped = decision.model_dump(mode="json")

    assert decision.mergeMethod == "kernel_fusion"
    assert dumped["mergeMethod"] == "kernel_fusion"


def test_unknown_merge_method_is_rejected() -> None:
    payload = _decision_payload()
    payload["mergeMethod"] = "semantic_similarity"

    try:
        MergeSuggestionDecision.model_validate(payload)
    except ValidationError:
        pass
    else:
        raise AssertionError("unknown mergeMethod must be rejected")
