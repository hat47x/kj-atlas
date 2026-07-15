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


class E2eRunbookCurrentHistoryBoundaryTest(unittest.TestCase):
    def test_e2e_runbook_is_a_default_current_only_path(self):
        self.assertIn(Path("03_Implement/frontend/docs/e2e_testing.md"), MODULE.CURRENT_ONLY_PATHS)

    def test_reports_reintroduced_stream_heading_in_the_e2e_runbook_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for relative_path in MODULE.CURRENT_ONLY_PATHS:
                (root / relative_path).parent.mkdir(parents=True, exist_ok=True)
                (root / relative_path).write_text("# Current\n", encoding="utf-8")
            (root / "03_Implement/frontend/docs/e2e_testing.md").write_text(
                textwrap.dedent("""\
                    # E2E Testing
                    ## Stream H (2026-08-01): reintroduced formation history
                """),
                encoding="utf-8",
            )

            findings = MODULE.check_current_history_headings(root)

        self.assertTrue(
            any(
                f.rule_id == "DC-CUR-001" and f.path == "03_Implement/frontend/docs/e2e_testing.md"
                for f in findings
            )
        )


class DocumentContractBaselineTest(unittest.TestCase):
    def _write_fixtures(self, root, schemas_text, api_text="DocumentV1 CRUD.\n", data_model_text="DocumentV1 support table.\n"):
        (root / "02_Architecture").mkdir(parents=True, exist_ok=True)
        (root / "02_Architecture" / "schemas.md").write_text(schemas_text, encoding="utf-8")
        (root / "02_Architecture" / "api.md").write_text(api_text, encoding="utf-8")
        (root / "02_Architecture" / "data_model_operations_overview.md").write_text(data_model_text, encoding="utf-8")

    def test_accepts_the_single_documentv1_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                textwrap.dedent("""\
                    # schemas
                    ```ts
                    export type DocumentV1 = {
                      version: 1;
                      id: string;
                    };
                    ```
                """),
            )

            findings = MODULE.check_document_contract_baseline(root)

        self.assertEqual(findings, [])

    def test_reports_duplicate_document_type_definitions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                textwrap.dedent("""\
                    # schemas
                    ```ts
                    export type DocumentV1 = {
                      version: 1;
                      id: string;
                    };
                    ```
                    ```ts
                    export type DocumentV1 = {
                      version: 1;
                      id: string;
                      islands: unknown[];
                    };
                    ```
                """),
            )

            findings = MODULE.check_document_contract_baseline(root)

        self.assertTrue(any(f.rule_id == "DC-ARC-001" and f.target == "Document" for f in findings))
        self.assertTrue(any("found 2" in f.message for f in findings))

    def test_reports_reintroduced_documentv2_and_legacy_normalization(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                textwrap.dedent("""\
                    # schemas
                    ```ts
                    export type DocumentV1 = {
                      version: 1;
                      id: string;
                    };

                    export type DocumentV2 = {
                      version: 2;
                      id: string;
                    };
                    ```

                    Legacy version-1 data is normalized to DocumentV2 on read.
                """),
            )

            findings = MODULE.check_document_contract_baseline(root)

        rule_ids_and_targets = {(f.rule_id, f.target) for f in findings}
        self.assertIn(("DC-ARC-001", "DocumentV2"), rule_ids_and_targets)
        self.assertIn(("DC-ARC-001", "Legacy"), rule_ids_and_targets)
        # Two Document type defs (V1 and V2) also trips the single-definition check.
        self.assertTrue(any(f.target == "Document" for f in findings))

    def test_reports_wrong_type_name_or_version_on_the_sole_document_type(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                textwrap.dedent("""\
                    # schemas
                    ```ts
                    export type DocumentV3 = {
                      version: 3;
                      id: string;
                    };
                    ```
                """),
            )

            findings = MODULE.check_document_contract_baseline(root)

        self.assertTrue(any(f.rule_id == "DC-ARC-001" and f.target == "DocumentV3" for f in findings))
        self.assertTrue(any("must be `DocumentV1`" in f.message for f in findings))

    def test_reports_missing_documentv1_reference_in_api_or_data_model_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                textwrap.dedent("""\
                    # schemas
                    ```ts
                    export type DocumentV1 = {
                      version: 1;
                      id: string;
                    };
                    ```
                """),
                api_text="No document type mentioned here.\n",
                data_model_text="No document type mentioned here.\n",
            )

            findings = MODULE.check_document_contract_baseline(root)

        paths_with_findings = {f.path for f in findings}
        self.assertIn("02_Architecture/api.md", paths_with_findings)
        self.assertIn("02_Architecture/data_model_operations_overview.md", paths_with_findings)


class HistoryMetadataTest(unittest.TestCase):
    def test_accepts_complete_metadata_and_reverse_link(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "architecture" / "history").mkdir(parents=True)
            current = root / "architecture" / "current.md"
            current.write_text("# Current\n\n[Formation history](history/sample.md)\n", encoding="utf-8")
            history = root / "architecture" / "history" / "sample.md"
            history.write_text(textwrap.dedent("""\
                # Sample history
                Status: Informative history
                Source document: [current](../current.md)
                Source anchors: former section
                Covered period: 2026-01
                Snapshot / source revision: `abc123`
                Retention reason: preserve formation context
                Current normative anchors:
                - [Current](../current.md#contract)
            """), encoding="utf-8")

            findings = MODULE.check_history_metadata(
                root, [Path("architecture/history/sample.md")]
            )

        self.assertEqual(findings, [])

    def test_reports_missing_metadata_anchor_and_reverse_link(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "architecture" / "history").mkdir(parents=True)
            (root / "architecture" / "current.md").write_text("# Current\n", encoding="utf-8")
            history = root / "architecture" / "history" / "sample.md"
            history.write_text(textwrap.dedent("""\
                # Sample history
                Status: Informative history
                Source document: [current](../current.md)
                Source anchors: former section
                Covered period: 2026-01
                Snapshot / source revision: `abc123`
                Current normative anchors:
            """), encoding="utf-8")

            findings = MODULE.check_history_metadata(
                root, [Path("architecture/history/sample.md")]
            )

        self.assertTrue(all(finding.rule_id == "DC-HIS-001" for finding in findings))
        self.assertTrue(any(finding.target == "Retention reason:" for finding in findings))
        self.assertTrue(any("no current normative anchor" in finding.message for finding in findings))
        self.assertTrue(any("does not link back" in finding.message for finding in findings))


if __name__ == "__main__":
    unittest.main()
