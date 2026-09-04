import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "triage_actionable_plans.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("triage_actionable_plans_cycles", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_issue(path: Path, *, status: str, priority: str = "P1", dependency: str | None = None) -> None:
    dependency_section = ""
    if dependency is not None:
        dependency_section = f"\n## Dependencies\n- `{dependency}`\n"
    path.write_text(
        textwrap.dedent(
            f"""\
            # Issue: {path.stem}
            - Status: {status}
            - Priority: {priority}
            {dependency_section}
            """
        ),
        encoding="utf-8",
    )


class TriageDependencyCyclesTest(unittest.TestCase):
    def test_active_cycle_is_reported_and_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            write_issue(
                root / "issues" / "issue-A-01.md",
                status="Open",
                dependency="issue-B-01.md",
            )
            write_issue(
                root / "issues" / "issue-B-01.md",
                status="Open",
                dependency="issue-A-01.md",
            )

            report = MODULE.collect(root)

        cycle_errors = [
            error
            for error in report["errors"]
            if error["reason"].startswith("dependency cycle among active issues:")
        ]
        self.assertEqual(len(cycle_errors), 1)
        self.assertIn("issues/issue-A-01.md", cycle_errors[0]["reason"])
        self.assertIn("issues/issue-B-01.md", cycle_errors[0]["reason"])

        issues = {item["backlog_id"]: item for item in report["actionable_issues"]}
        self.assertFalse(issues["A-01"]["ready"])
        self.assertFalse(issues["B-01"]["ready"])
        self.assertEqual(issues["A-01"]["dependency_stage"], 999)
        self.assertEqual(issues["B-01"]["dependency_stage"], 999)

    def test_done_dependency_is_terminal_even_if_its_history_points_back(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues" / "done").mkdir(parents=True)
            write_issue(
                root / "issues" / "issue-ACTIVE-01.md",
                status="Open",
                dependency="issue-DONE-01.md",
            )
            write_issue(
                root / "issues" / "done" / "issue-DONE-01.md",
                status="Done",
                dependency="issue-ACTIVE-01.md",
            )

            report = MODULE.collect(root)

        active = report["actionable_issues"][0]
        self.assertEqual(active["backlog_id"], "ACTIVE-01")
        self.assertTrue(active["ready"])
        self.assertEqual(active["dependency_stage"], 1)
        self.assertEqual(active["unlocks"], ())
        self.assertFalse(
            any(
                error["reason"].startswith("dependency cycle among active issues:")
                for error in report["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
