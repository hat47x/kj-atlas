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


class HistoryDocumentCheckTest(unittest.TestCase):
    def _write_clean_pair(self, root: Path) -> tuple[Path, Path]:
        architecture = root / "02_Architecture"
        history_dir = architecture / "history"
        history_dir.mkdir(parents=True)
        current = architecture / "current.md"
        history = history_dir / "formation.md"
        current.write_text(
            "# Current contract\n\n[Formation history](history/formation.md)\n",
            encoding="utf-8",
        )
        history.write_text(textwrap.dedent("""\
            # Formation history

            Status: Informative history

            Source document: [Current contract](../current.md)

            Source anchors: former §2

            Covered period: 2026-01-01 to 2026-01-02

            Snapshot / source revision: `abc123`

            Retention reason: Preserve the decision sequence without overriding current values.

            Current normative anchors:

            - [Current contract](../current.md#current-contract)

            ## Former execution record
            """), encoding="utf-8")
        index = history_dir / "README.md"
        index.write_text("# History\n\n[Formation](formation.md)\n", encoding="utf-8")
        return history, index

    def test_accepts_complete_metadata_current_anchor_and_bidirectional_routes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            history, index = self._write_clean_pair(root)

            findings = MODULE.check_history_documents(root, [history], index)

        self.assertEqual(findings, [])

    def test_reports_missing_metadata_and_noncanonical_status(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            history, index = self._write_clean_pair(root)
            history.write_text("# History\n\nStatus: Current\n", encoding="utf-8")

            findings = MODULE.check_history_documents(root, [history], index)

        rendered = "\n".join(finding.render() for finding in findings)
        self.assertIn("DC-HIS-001 02_Architecture/history/formation.md:1", rendered)
        self.assertIn("Source document", rendered)
        self.assertIn("Snapshot / source revision", rendered)
        self.assertIn("must be exactly 'Informative history'", rendered)

    def test_reports_missing_current_anchor_reverse_link_and_index_entry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            history, index = self._write_clean_pair(root)
            current = root / "02_Architecture" / "current.md"
            current.write_text("# Current contract\n", encoding="utf-8")
            index.write_text("# History\n", encoding="utf-8")
            text = history.read_text(encoding="utf-8")
            history.write_text(
                text.replace("- [Current contract](../current.md#current-contract)", "No current link."),
                encoding="utf-8",
            )

            findings = MODULE.check_history_documents(root, [history], index)

        messages = "\n".join(finding.message for finding in findings)
        self.assertIn("Current normative anchors", messages)
        self.assertIn("does not link back", messages)
        self.assertIn("missing from the history index", messages)


class RequiredRouteCheckTest(unittest.TestCase):
    def test_accepts_markdown_link_and_literal_command_routes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "tools").mkdir()
            (root / "docs" / "target.md").write_text("# Target\n", encoding="utf-8")
            (root / "tools" / "check.py").write_text("# tool\n", encoding="utf-8")
            (root / "README.md").write_text(
                "[Target](docs/target.md)\n\n`python tools/check.py`\n",
                encoding="utf-8",
            )
            requirements = [
                MODULE.RequiredRoute(
                    Path("README.md"), Path("docs/target.md"), "docs/target.md", True
                ),
                MODULE.RequiredRoute(
                    Path("README.md"), Path("tools/check.py"), "python tools/check.py", False
                ),
            ]

            findings = MODULE.check_required_routes(root, requirements)

        self.assertEqual(findings, [])

    def test_reports_missing_route_with_rule_source_target_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "docs" / "target.md").write_text("# Target\n", encoding="utf-8")
            (root / "README.md").write_text("# Entry\n", encoding="utf-8")
            requirement = MODULE.RequiredRoute(
                Path("README.md"), Path("docs/target.md"), "docs/target.md", True
            )

            findings = MODULE.check_required_routes(root, [requirement])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-RTE-001")
        self.assertEqual(findings[0].path, "README.md")
        self.assertEqual(findings[0].target, "docs/target.md")
        self.assertIn("Markdown link", findings[0].fix_hint)
        self.assertIn("DC-RTE-001 README.md:1", findings[0].render())


class PublicUiCatalogCheckTest(unittest.TestCase):
    def _write_clean_documents(self, root: Path) -> tuple[Path, Path]:
        catalog = root / "04_Documentation" / "ui_catalog.md"
        ledger = root / "04_Documentation" / "assets" / "screenshots" / "README.md"
        ledger.parent.mkdir(parents=True)
        catalog.write_text(
            "# UI catalog\n"
            + "\n".join(MODULE.PUBLIC_CATALOG_REQUIRED)
            + "\n",
            encoding="utf-8",
        )
        ledger.write_text(
            "# Screenshot ledger\n"
            + "\n".join(MODULE.SCREENSHOT_LEDGER_REQUIRED)
            + "\n",
            encoding="utf-8",
        )
        return catalog, ledger

    def test_accepts_public_boundary_and_complete_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            catalog, ledger = self._write_clean_documents(root)

            findings = MODULE.check_public_ui_catalog(root, catalog, ledger)

        self.assertEqual(findings, [])

    def test_reports_internal_reference_with_rule_file_line_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            catalog, ledger = self._write_clean_documents(root)
            catalog.write_text(
                catalog.read_text(encoding="utf-8") + "\nSee ADR-0044 for internal progress.\n",
                encoding="utf-8",
            )

            findings = MODULE.check_public_ui_catalog(root, catalog, ledger)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-PUB-001")
        self.assertEqual(findings[0].path, "04_Documentation/ui_catalog.md")
        self.assertEqual(findings[0].target, "ADR-0044")
        self.assertIn("02_Architecture/design", findings[0].fix_hint)

    def test_reports_missing_catalog_and_ledger_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            catalog, ledger = self._write_clean_documents(root)
            catalog.write_text("# UI catalog\n", encoding="utf-8")
            ledger.write_text("# Ledger\n", encoding="utf-8")

            findings = MODULE.check_public_ui_catalog(root, catalog, ledger)

        targets = {finding.target for finding in findings}
        self.assertIn("確認対象revision", targets)
        self.assertIn("Source revision:", targets)
        self.assertIn("Stale triggers checked:", targets)


class ConflictMarkerCheckTest(unittest.TestCase):
    def test_reports_conflict_boundaries_with_rule_file_line_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "guide.md"
            source.write_text(
                "# Guide\n\n<<<<<<< HEAD\ncurrent\n=======\nincoming\n>>>>>>> main\n",
                encoding="utf-8",
            )

            findings = MODULE.check_conflict_markers(root, [source])

        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0].rule_id, "DC-FMT-001")
        self.assertEqual(findings[0].path, "guide.md")
        self.assertEqual(findings[0].line, 3)
        self.assertEqual(findings[1].line, 7)
        self.assertIn("git diff --check", findings[0].fix_hint)

    def test_ignores_setext_heading_and_fenced_example(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "guide.md"
            source.write_text(textwrap.dedent("""\
                Guide
                =====

                ```text
                <<<<<<< HEAD
                >>>>>>> main
                ```
            """), encoding="utf-8")

            findings = MODULE.check_conflict_markers(root, [source])

        self.assertEqual(findings, [])


class SafetyInvariantRouteCheckTest(unittest.TestCase):
    def _complete_entry(self) -> str:
        return textwrap.dedent("""\
            # Agent entry

            - SafeModeは既定ON。
            - AI出力はproposal-onlyで、自動適用しない。
            - `human_reviewed` は人間だけが設定する。
            - `KJ_ATLAS_LLM_PROVIDER=none` でも主要価値が成立する。
            - share/exportで未レビュー情報や秘密情報を意図せず共有しない。
        """)

    def test_accepts_all_five_safety_invariants(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = root / "AGENTS.md"
            entry.write_text(self._complete_entry(), encoding="utf-8")

            findings = MODULE.check_safety_invariant_route(root, entry)

        self.assertEqual(findings, [])

    def test_reports_missing_invariant_with_rule_entry_and_fix(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            entry = root / "AGENTS.md"
            entry.write_text(
                self._complete_entry().replace("- SafeModeは既定ON。\n", ""),
                encoding="utf-8",
            )

            findings = MODULE.check_safety_invariant_route(root, entry)

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-SAF-001")
        self.assertEqual(findings[0].path, "AGENTS.md")
        self.assertEqual(findings[0].target, "SafeMode default ON")
        self.assertIn("AGENTS.md safety section", findings[0].fix_hint)


if __name__ == "__main__":
    unittest.main()
