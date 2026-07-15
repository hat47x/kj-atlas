import importlib.util
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


class CurrentOnlyHeadingCheckTest(unittest.TestCase):
    def test_reports_execution_history_heading_with_rule_file_line_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "current.md"
            source.write_text("# Current contract\n\n## Stream B execution log\n", encoding="utf-8")

            findings = MODULE.check_current_only_headings(root, [source])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CUR-001")
        self.assertEqual(finding.path, "current.md")
        self.assertEqual(finding.line, 3)
        self.assertEqual(finding.target, "Stream B execution log")
        self.assertIn("current-only", finding.message)
        self.assertIn("history document", finding.fix_hint)
        self.assertIn("DC-CUR-001 current.md:3", finding.render())

    def test_reports_japanese_history_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "current.md"
            source.write_text("# 現行手順\n\n### 過去件数と解消済みキュー\n", encoding="utf-8")

            findings = MODULE.check_current_only_headings(root, [source])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].line, 3)

    def test_ignores_body_fenced_code_inline_code_and_downstream_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "current.md"
            source.write_text(textwrap.dedent("""\
                # Current contract

                A prior Stream is mentioned here only to explain the current boundary.

                ## Downstream signature catalog

                ## `Stream` field contract

                ```md
                ## Rerun checkpoint
                ```
            """), encoding="utf-8")

            findings = MODULE.check_current_only_headings(root, [source])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
