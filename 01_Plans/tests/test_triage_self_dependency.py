import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "triage_actionable_plans.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("triage_actionable_plans_self_dep", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class TriageSelfDependencyTest(unittest.TestCase):
    def test_self_dependency_is_error_and_blocker(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            (root / "issues" / "issue-SELF-01.md").write_text(
                textwrap.dedent("""\
                    # Issue: SELF-01
                    - Status: Open
                    - Priority: P1

                    ## Dependencies
                    - `issue-SELF-01.md`
                """),
                encoding="utf-8",
            )

            report = MODULE.collect(root)

        issue = report["actionable_issues"][0]
        self.assertFalse(issue["ready"])
        self.assertEqual(issue["classification"], "Blocked")
        self.assertEqual(issue["dependency_stage"], 999)
        self.assertIn("SELF-01:SelfDependency", issue["blockers"])
        self.assertIn(
            {
                "path": "issues/issue-SELF-01.md",
                "reason": "self dependency: issues/issue-SELF-01.md",
            },
            report["errors"],
        )


if __name__ == "__main__":
    unittest.main()
