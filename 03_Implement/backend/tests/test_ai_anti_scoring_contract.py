from pathlib import Path

from kj_atlas_api.main import app


REPOSITORY_ROOT = Path(__file__).resolve().parents[3]


def test_card_importance_scoring_surface_is_absent() -> None:
    route_paths = {route.path for route in app.routes}
    assert "/ai/assess-card-importance" not in route_paths

    models_source = (
        REPOSITORY_ROOT
        / "03_Implement/backend/src/kj_atlas_api/models_ai.py"
    ).read_text(encoding="utf-8")
    routes_source = (
        REPOSITORY_ROOT
        / "03_Implement/backend/src/kj_atlas_api/routes/ai.py"
    ).read_text(encoding="utf-8")
    demo_source = (
        REPOSITORY_ROOT
        / "03_Implement/deploy/tools/kj_canvas_demo.py"
    ).read_text(encoding="utf-8")

    forbidden = (
        "AssessCardImportanceRequest",
        "AssessCardImportanceResponse",
        "_CardAssessment",
        "assess_card_importance",
        "assess-card-importance",
    )
    for token in forbidden:
        assert token not in models_source
        assert token not in routes_source
        assert token not in demo_source


def test_domain_keeps_explicit_anti_scoring_invariant() -> None:
    domain = (REPOSITORY_ROOT / "00_Prompt/domain.md").read_text(encoding="utf-8")
    assert "AIは内容を採点せず" in domain
