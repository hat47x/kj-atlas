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
        self.assertEqual(ready["backlog_id"], "AAA-01-ready")
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

    def test_proposed_dependency_adr_blocks_issue_until_accepted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            issue = root / "issues" / "issue-AAA-01-adr-blocked.md"
            issue.write_text(textwrap.dedent("""\
                # Issue: AAA-01
                - Type: Contract
                - Status: Open
                - Source Issue: N/A
                - Priority: P1
                - Owner: Unassigned
                - Related ADR/Spec: `ADR-9999`
                - Expected verification level: `unit`

                ## 依存関係
                - `01_Plans/adr/ADR-9999-sample.md`（採択が前提）
            """), encoding="utf-8")
            adr = root / "adr" / "ADR-9999-sample.md"
            adr.write_text(textwrap.dedent("""\
                # ADR-9999: sample
                - Status: Proposed
                - Date: 2026-08-11
                - Deciders: Maintainer
            """), encoding="utf-8")

            proposed_report = MODULE.collect(root)
            adr.write_text(adr.read_text(encoding="utf-8").replace(
                "Status: Proposed", "Status: Accepted"
            ), encoding="utf-8")
            accepted_report = MODULE.collect(root)

        proposed = proposed_report["actionable_issues"][0]
        self.assertFalse(proposed["ready"])
        self.assertEqual(proposed["blockers"], ("ADR-9999:Proposed",))
        self.assertIn("ADR-9999", proposed["depends_on"])
        self.assertTrue(accepted_report["actionable_issues"][0]["ready"])

    def test_adr_status_normalization_accepts_annotations_but_not_prefix_collisions(self):
        self.assertEqual(MODULE.normalize_adr_status("Accepted (note)"), "Accepted")
        self.assertEqual(MODULE.normalize_adr_status("Accepted（注釈）"), "Accepted")
        self.assertEqual(MODULE.normalize_adr_status("Proposed (note)"), "Proposed")
        self.assertEqual(MODULE.normalize_adr_status("AcceptedButPending"), "AcceptedButPending")

    def test_annotated_accepted_dependency_adr_does_not_block_issue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-AAA-01.md").write_text(textwrap.dedent("""\
                # Issue: AAA-01
                - Type: Contract
                - Status: Open
                - Source Issue: N/A
                - Priority: P1
                - Owner: Maintainer
                - Expected verification level: `unit`

                ## Dependencies
                - `ADR-9999-sample.md`
            """), encoding="utf-8")
            (root / "adr" / "ADR-9999-sample.md").write_text(textwrap.dedent("""\
                # ADR-9999: sample
                - Status: Accepted（2026-09-04、条件付き採択）
                - Date: 2026-09-04
                - Deciders: Maintainer
            """), encoding="utf-8")

            report = MODULE.collect(root)

        issue = report["actionable_issues"][0]
        self.assertTrue(issue["ready"])
        self.assertEqual(issue["blockers"], ())

    def test_annotated_proposed_dependency_adr_still_blocks_issue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-AAA-01.md").write_text(textwrap.dedent("""\
                # Issue: AAA-01
                - Status: Open
                - Priority: P1

                ## Dependencies
                - `ADR-9999-sample.md`
            """), encoding="utf-8")
            (root / "adr" / "ADR-9999-sample.md").write_text(textwrap.dedent("""\
                # ADR-9999: sample
                - Status: Proposed (review pending)
                - Date: 2026-09-04
            """), encoding="utf-8")

            report = MODULE.collect(root)

        issue = report["actionable_issues"][0]
        self.assertFalse(issue["ready"])
        self.assertEqual(issue["blockers"], ("ADR-9999:Proposed",))

    def test_missing_dependency_adr_is_a_triage_error(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-AAA-01-missing-adr.md").write_text(
                textwrap.dedent("""\
                    # Issue: AAA-01
                    - Status: Open
                    - Priority: P1

                    ## Dependencies
                    - `ADR-9999-missing.md`
                """),
                encoding="utf-8",
            )

            report = MODULE.collect(root)

        self.assertIn(
            {
                "path": "issues/issue-AAA-01-missing-adr.md",
                "reason": "dependency ADR not found: ADR-9999",
            },
            report["errors"],
        )

    def test_dependency_section_after_line_120_still_blocks_issue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            dependency = root / "issues" / "issue-DEP-01.md"
            dependency.write_text(
                "# Issue: DEP-01\n- Status: Draft\n- Priority: P2\n",
                encoding="utf-8",
            )
            issue = root / "issues" / "issue-LONG-01.md"
            filler = "\n".join(f"checkpoint {index}" for index in range(130))
            issue.write_text(
                "# Issue: LONG-01\n"
                "- Status: Open\n"
                "- Priority: P2\n\n"
                "## Implementation log\n"
                f"{filler}\n\n"
                "## Dependencies\n"
                "- `issue-DEP-01.md`\n",
                encoding="utf-8",
            )

            report = MODULE.collect(root)

        long_issue = next(
            item for item in report["actionable_issues"] if item["backlog_id"] == "LONG-01"
        )
        self.assertFalse(long_issue["ready"])
        self.assertEqual(long_issue["blockers"], ("DEP-01:Draft",))
        self.assertIn("issues/issue-DEP-01.md", long_issue["depends_on"])


if __name__ == "__main__":
    unittest.main()
