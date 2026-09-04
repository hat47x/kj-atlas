import importlib.util
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "triage_actionable_plans.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("triage_actionable_plans_ambiguous", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_issue(
    path: Path,
    *,
    status: str,
    dependency: str | None = None,
    priority: str = "P1",
) -> None:
    lines = [
        f"# Issue: {path.stem}",
        f"- Status: {status}",
        f"- Priority: {priority}",
    ]
    if dependency is not None:
        lines.extend(["", "## Dependencies", f"- `{dependency}`"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


class TriageAmbiguousDependencyTest(unittest.TestCase):
    def test_ambiguous_basename_fallback_is_reported_and_blocks_ready(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            write_issue(
                root / "issues" / "issue-APP-01.md",
                status="Open",
                dependency="issue-DEP-01.md",
            )
            write_issue(
                root / "issues" / "done" / "issue-DEP-01.md",
                status="Done",
            )
            write_issue(
                root / "issues" / "archive" / "issue-DEP-01.md",
                status="Done",
            )

            report = MODULE.collect(root)

        app = next(
            item for item in report["actionable_issues"] if item["backlog_id"] == "APP-01"
        )
        self.assertFalse(app["ready"])
        self.assertEqual(app["blockers"], ("DEP-01:Ambiguous",))
        self.assertEqual(app["dependency_stage"], 999)
        self.assertEqual(app["depends_on"], ("issues/issue-DEP-01.md",))

        ambiguity_errors = [
            error
            for error in report["errors"]
            if error["reason"].startswith("ambiguous dependency basename:")
        ]
        self.assertEqual(len(ambiguity_errors), 1)
        reason = ambiguity_errors[0]["reason"]
        self.assertIn("issue-DEP-01.md", reason)
        self.assertIn("issues/archive/issue-DEP-01.md", reason)
        self.assertIn("issues/done/issue-DEP-01.md", reason)
        self.assertNotIn(
            {"path": "issues/issue-APP-01.md", "reason": "dependency path not found: issues/issue-DEP-01.md"},
            report["errors"],
        )

    def test_exact_path_wins_before_basename_fallback(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "adr").mkdir()
            (root / "issues").mkdir()
            write_issue(
                root / "issues" / "issue-APP-01.md",
                status="Open",
                dependency="issue-DEP-01.md",
            )
            write_issue(
                root / "issues" / "issue-DEP-01.md",
                status="Open",
            )
            write_issue(
                root / "issues" / "done" / "issue-DEP-01.md",
                status="Done",
            )

            report = MODULE.collect(root)

        app = next(
            item for item in report["actionable_issues"] if item["backlog_id"] == "APP-01"
        )
        self.assertFalse(app["ready"])
        self.assertEqual(app["blockers"], ("DEP-01:Open",))
        self.assertEqual(app["dependency_stage"], 1)
        self.assertFalse(
            any(
                error["reason"].startswith("ambiguous dependency basename:")
                for error in report["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
