from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
E2E_DOC = ROOT / "03_Implement/frontend/docs/e2e_testing.md"
QA_ISSUE = ROOT / "01_Plans/issues/issue-QA-E2E-USE-01-realistic-user-journey-expansion.md"
PRODUCT_QA_ISSUE = ROOT / "01_Plans/issues/issue-PRODUCT-QA-01-release-readiness-quality-gates.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_e2e_doc_has_plan_execute_verify_proceed_flow_and_self_repair_limit() -> None:
    text = _read(E2E_DOC)
    for token in (
        "Plan → Execute → Verify → Proceed",
        "代表ユーザ操作の回帰レーン",
        "ux_operability_regression.test.ts",
        "自己修復は最大3回",
        "4回目相当は Stop",
    ):
        assert token in text


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
