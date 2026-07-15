from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E2E_DOC = ROOT / "03_Implement/frontend/docs/e2e_testing.md"
QA_ISSUE = ROOT / "01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md"
PRODUCT_QA_ISSUE = ROOT / "01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_e2e_doc_has_current_runbook_invariants() -> None:
    """DX-E2E-08: verify the current-facing runbook, not a retired Stream/QA-gate process."""
    text = _read(E2E_DOC)
    for token in (
        "npm run e2e",
        "npm run e2e:mock",
        "npm run test:regression-guards",
        "代表ユーザ操作の回帰レーン",
        "ux_operability_regression.test.ts",
        "標準経路はDocker Compose",
        "R-01",
        "SafeMode",
        "失敗時に残す情報",
        "ADR-0019",
    ):
        assert token in text, f"missing current-runbook invariant: {token}"

    for retired_token in (
        "Plan → Execute → Verify → Proceed",
        "自己修復は最大3回",
        "4回目相当は Stop",
        "Stream E",
        "Stream F",
        "Stream G",
        "--files",
        "直列実装順",
        "Draft群 Open化",
    ):
        assert retired_token not in text, f"retired Stream/self-repair token reappeared: {retired_token}"


def test_qa_issue_keeps_execution_hold_and_open_gate_contract_tokens() -> None:
    text = _read(QA_ISSUE)
    for token in (
        "Execution: Hold",
        "AC-O1",
        "AC-O2",
        "AC-O3",
        "AC-O4",
        "DoD-O1",
        "DoD-O2",
        "DoD-O3",
        "代表ユーザ操作証跡レーン",
        "Path-USE-A",
    ):
        assert token in text


def test_product_qa_issue_has_release_decision_contract() -> None:
    text = _read(PRODUCT_QA_ISSUE)
    for token in (
        "Go / Conditional Go / No-Go",
        "Blocker",
        "Major",
        "Minor",
        "Gate Record",
        "representative user-operation evidence lane",
    ):
        assert token in text
