import importlib.util
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_contract_checks.py"
SPEC = importlib.util.spec_from_file_location("docs_contract_checks", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RelativeLinkCheckTest(unittest.TestCase):
    def test_reports_missing_target_with_rule_file_line_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            source = root / "docs" / "guide.md"
            source.write_text("# Guide\n\n[missing](missing.md)\n", encoding="utf-8")

            findings = MODULE.check_relative_links(root, [source])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-LNK-001")
        self.assertEqual(finding.path, "docs/guide.md")
        self.assertEqual(finding.line, 3)
        self.assertEqual(finding.target, "missing.md")
        self.assertIn("relative target does not exist", finding.message)
        self.assertIn("docs", finding.fix_hint)
        self.assertIn("DC-LNK-001 docs/guide.md:3", finding.render())

    def test_accepts_existing_relative_root_and_percent_encoded_targets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "reference").mkdir()
            (root / "reference" / "guide with space.md").write_text("# Target\n", encoding="utf-8")
            source = root / "docs" / "guide.md"
            source.write_text(textwrap.dedent("""\
                [relative](../reference/guide%20with%20space.md#section)
                [root](/reference/guide%20with%20space.md)
            """), encoding="utf-8")

            findings = MODULE.check_relative_links(root, [Path("docs/guide.md")])

        self.assertEqual(findings, [])

    def test_ignores_code_external_urls_and_page_anchors(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "guide.md"
            source.write_text(textwrap.dedent("""\
                `[inline](missing-inline.md)`

                ```md
                [fenced](missing-fenced.md)
                ```

                [web](https://example.com/missing)
                [mail](mailto:test@example.com)
                [anchor](#local-heading)
            """), encoding="utf-8")

            findings = MODULE.check_relative_links(root, [source])

        self.assertEqual(findings, [])

    def test_reports_target_that_escapes_repository(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "repo"
            root.mkdir()
            source = root / "guide.md"
            source.write_text("[outside](../outside.md)\n", encoding="utf-8")

            findings = MODULE.check_relative_links(root, [source])

        self.assertEqual(len(findings), 1)
        self.assertIn("escapes the repository", findings[0].message)

    def test_tracked_markdown_paths_excludes_untracked_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "tracked.md").write_text("# Tracked\n", encoding="utf-8")
            (root / "untracked.md").write_text("# Untracked\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.md"], check=True)

            paths = MODULE.tracked_markdown_paths(root)

        self.assertEqual(paths, [Path("tracked.md")])


class CurrentHistoryBoundaryTest(unittest.TestCase):
    def test_reports_execution_history_heading_with_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "current.md"
            source.write_text("# Contract\n\n## Stream D execution checkpoint\n", encoding="utf-8")

            findings = MODULE.check_current_history_headings(root, (Path("current.md"),))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-CUR-001")
        self.assertEqual(findings[0].line, 3)
        self.assertIn("02_Architecture/history", findings[0].fix_hint)

    def test_accepts_normative_headings_and_ignores_code(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "current.md"
            source.write_text(textwrap.dedent("""\
                # Current contract
                ## Execution constraints
                ## downstream signature catalog
                `## Stream A checkpoint`

                ```md
                ## rerun log
                ```
            """), encoding="utf-8")

            findings = MODULE.check_current_history_headings(root, (Path("current.md"),))

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
