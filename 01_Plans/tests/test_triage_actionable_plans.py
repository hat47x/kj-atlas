import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "triage_actionable_plans.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("triage_actionable_plans", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TriageActionablePlansTest(unittest.TestCase):
    def test_collect_finds_ready_and_blocked_items(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-AAA-01-ready.md").write_text(textwrap.dedent("""\
                # Issue Draft: AAA-01
                - Type: Process
                - Status: Open
                - Lifecycle: Draft -> Open -> In Progress -> Done
                - Source Issue: N/A
                - Priority: P1
                - Owner: Architecture Owner
                - Scope: `01_Plans/`
                - Related Backlog: `AAA-01`
                - Related ADR/Spec: `ADR-9999`
                - Expected verification level: `docs-check`
            """), encoding="utf-8")
            (root / "issues" / "issue-BBB-01-blocked.md").write_text(textwrap.dedent("""\
                # Issue Draft: BBB-01
                - Type: Implementation
                - Status: Draft
                - Lifecycle: Draft -> Open -> In Progress -> Done
                - Source Issue: TBD
                - Priority: P2
                - Owner: Frontend Owner
                - Scope: `03_Implement/frontend/`
                - Related Backlog: `BBB-01`
                - Related ADR/Spec: `ADR-9999`
                - Expected verification level: `unit`

                ## 7) 依存関係
                - `issue-AAA-01-ready.md`
            """), encoding="utf-8")
            (root / "adr" / "ADR-9999-sample.md").write_text(textwrap.dedent("""\
                # ADR-9999: sample
                - Status: Accepted
                - Date: 2026-03-21
                - Deciders: Test
                - Scope: `01_Plans/`
                - Source Issue: `01_Plans/issues/issue-AAA-01-ready.md`
                - Related: `ADR-0001`
            """), encoding="utf-8")

            report = MODULE.collect(root)

        self.assertEqual(report["summary"]["active_issue_count"], 2)
        self.assertEqual(report["summary"]["ready_issue_count"], 1)
        self.assertEqual(report["summary"]["blocked_issue_count"], 1)
        ready = report["actionable_issues"][0]
        self.assertTrue(ready["ready"])
        blocked = report["actionable_issues"][1]
        self.assertFalse(blocked["ready"])
        self.assertIn("issues/issue-AAA-01-ready.md", blocked["depends_on"])
        self.assertEqual(report["actionable_adrs"][0]["adr_id"], "ADR-9999")

    def test_collect_rejects_noncanonical_status_without_normalizing(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-invalid.md").write_text(
                "# Issue: invalid\n- Status: Draft (waiting)\n- Priority: P1\n",
                encoding="utf-8",
            )

            report = MODULE.collect(root)

        self.assertEqual(report["summary"]["active_issue_count"], 0)
        self.assertEqual(
            report["errors"],
            [{"path": "issues/issue-invalid.md", "reason": "invalid Status metadata: Draft (waiting)"}],
        )


if __name__ == "__main__":
    unittest.main()
