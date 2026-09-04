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


class TriageAmbiguousAdrRefTest(unittest.TestCase):
    def _write_issue(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            textwrap.dedent(
                """\
                # Issue: SAME-01
                - Status: Open
                - Priority: P1
                """
            ),
            encoding="utf-8",
        )

    def _write_adr(self, path: Path, source_issue: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            textwrap.dedent(
                f"""\
                # ADR-9999: sample
                - Status: Proposed
                - Date: 2026-09-04
                - Source Issue: `{source_issue}`
                """
            ),
            encoding="utf-8",
        )

    def test_ambiguous_basename_is_not_guessed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_issue(root / "issues" / "team-a" / "issue-SAME-01.md")
            self._write_issue(root / "issues" / "team-b" / "issue-SAME-01.md")
            self._write_adr(
                root / "adr" / "ADR-9999-sample.md",
                "01_Plans/issues/issue-SAME-01.md",
            )

            report = MODULE.collect(root)

        self.assertEqual(report["actionable_adrs"], [])
        self.assertIn(
            {
                "path": "adr/ADR-9999-sample.md",
                "reason": (
                    "ambiguous active issue basename: issue-SAME-01.md -> "
                    "issues/team-a/issue-SAME-01.md, issues/team-b/issue-SAME-01.md"
                ),
            },
            report["errors"],
        )

    def test_exact_path_wins_even_when_same_basename_exists_elsewhere(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_issue(root / "issues" / "team-a" / "issue-SAME-01.md")
            self._write_issue(root / "issues" / "team-b" / "issue-SAME-01.md")
            self._write_adr(
                root / "adr" / "ADR-9999-sample.md",
                "01_Plans/issues/team-a/issue-SAME-01.md",
            )

            report = MODULE.collect(root)

        self.assertEqual(len(report["actionable_adrs"]), 1)
        self.assertEqual(
            report["actionable_adrs"][0]["active_issue_refs"],
            ("issues/team-a/issue-SAME-01.md",),
        )
        self.assertFalse(
            any(
                error["path"] == "adr/ADR-9999-sample.md"
                and error["reason"].startswith("ambiguous active issue basename:")
                for error in report["errors"]
            )
        )

    def test_unique_basename_fallback_still_resolves_moved_issue(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_issue(root / "issues" / "team-a" / "issue-SAME-01.md")
            self._write_adr(
                root / "adr" / "ADR-9999-sample.md",
                "01_Plans/issues/issue-SAME-01.md",
            )

            report = MODULE.collect(root)

        self.assertEqual(len(report["actionable_adrs"]), 1)
        self.assertEqual(
            report["actionable_adrs"][0]["active_issue_refs"],
            ("issues/team-a/issue-SAME-01.md",),
        )
        self.assertEqual(report["errors"], [])


if __name__ == "__main__":
    unittest.main()
