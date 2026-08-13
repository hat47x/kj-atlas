from pathlib import Path

from kj_atlas_api.main import app


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


#: Files the scoring surface must not reappear in. `llm/provider.py` was added
#: after AI-IMPORTANCE-SCORING-01's removal was found incomplete: the task had
#: been deleted from routes and models but survived in the MMR-04 routing table,
#: so `routing_stage_for_task("assess_card_importance")` still answered
#: "final_judgement" for a task that no longer exists.
_GUARDED_SOURCES = (
    "03_Implement/backend/src/kj_atlas_api/models_ai.py",
    "03_Implement/backend/src/kj_atlas_api/routes/ai.py",
    "03_Implement/backend/src/kj_atlas_api/llm/provider.py",
    "03_Implement/deploy/tools/kj_canvas_demo.py",
)

#: Design-canon documents. A removed-on-principle capability that keeps its
#: contract in the canon reads as "not built yet" to anyone (or any drift
#: checker) that compares docs against code, which is how the 2026-08-12
#: "未実装（計画）" annotation got written into api.md. See DX-CANON-INTENT-01.
_GUARDED_CANON = (
    "02_Architecture/api.md",
    "02_Architecture/runtime_parameter_registry.md",
)

_FORBIDDEN_TOKENS = (
    "AssessCardImportanceRequest",
    "AssessCardImportanceResponse",
    "_CardAssessment",
    "assess_card_importance",
)


def test_card_importance_scoring_surface_is_absent() -> None:
    route_paths = {route.path for route in app.routes}
    assert "/ai/assess-card-importance" not in route_paths

    for relative_path in _GUARDED_SOURCES:
        source = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for token in (*_FORBIDDEN_TOKENS, "assess-card-importance"):
            assert token not in source, (
                f"{relative_path} references the removed card-importance scoring "
                f"surface ('{token}'). AI-IMPORTANCE-SCORING-01 removed it as a "
                "violation of the unconditional invariant in 00_Prompt/domain.md."
            )


def test_design_canon_does_not_advertise_the_removed_scoring_contract() -> None:
    """The canon may record the removal, but must not carry a usable contract.

    api.md is what an implementer and every drift checker treat as the source of
    truth for what the API should be. Leaving the request/response shapes there
    is what let a well-meaning correction re-label a deliberately removed
    capability as merely unimplemented.
    """
    for relative_path in _GUARDED_CANON:
        canon = (REPOSITORY_ROOT / relative_path).read_text(encoding="utf-8")
        for token in _FORBIDDEN_TOKENS:
            assert token not in canon, (
                f"{relative_path} still carries the '{token}' contract for the "
                "removed card-importance scoring endpoint. Record the removal in "
                "prose instead of leaving an implementable schema."
            )


def test_domain_keeps_explicit_anti_scoring_invariant() -> None:
    domain = (REPOSITORY_ROOT / "00_Prompt/domain.md").read_text(encoding="utf-8")
    assert "AIは内容を採点せず" in domain
