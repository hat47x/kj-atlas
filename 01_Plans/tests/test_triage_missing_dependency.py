from __future__ import annotations

import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "triage_actionable_plans.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("triage_actionable_plans_missing_dep", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TriageMissingDependencyTest(unittest.TestCase):
    def make_root(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "adr").mkdir()
        (root / "issues").mkdir()
        return td, root

    def test_missing_issue_dependency_is_reported_and_blocks_ready(self) -> None:
        td, root = self.make_root()
        with td:
            (root / "issues" / "issue-APP-01.md").write_text(
                textwrap.dedent("""\
                    # Issue: APP-01
                    - Status: Open
                    - Priority: P1

                    ## Dependencies
                    - `issue-DEP-404.md`
                """),
                encoding="utf-8",
            )
            report = MODULE.collect(root)

        self.assertIn(
            {
                "path": "issues/issue-APP-01.md",
                "reason": "dependency path not found: issues/issue-DEP-404.md",
            },
            report["errors"],
        )
        issue = report["actionable_issues"][0]
        self.assertFalse(issue["ready"])
        self.assertEqual(("DEP-404:Missing",), issue["blockers"])
        self.assertEqual(999, issue["dependency_stage"])

    def test_missing_adr_dependency_is_reported_and_blocks_ready(self) -> None:
        td, root = self.make_root()
        with td:
            (root / "issues" / "issue-APP-02.md").write_text(
                textwrap.dedent("""\
                    # Issue: APP-02
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
                "path": "issues/issue-APP-02.md",
                "reason": "dependency ADR not found: ADR-9999",
            },
            report["errors"],
        )
        issue = report["actionable_issues"][0]
        self.assertFalse(issue["ready"])
        self.assertEqual(("ADR-9999:Missing",), issue["blockers"])


if __name__ == "__main__":
    unittest.main()
