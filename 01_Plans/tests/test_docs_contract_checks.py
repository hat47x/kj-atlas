import importlib.util
import io
import subprocess
import sys
import tempfile
import textwrap
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_contract_checks.py"
SPEC = importlib.util.spec_from_file_location("docs_contract_checks", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class MainWiringTest(unittest.TestCase):
    CHECKS_WITH_PATHS = (
        "check_relative_links",
        "check_adr_id_uniqueness",
        "check_adr_traceability_paths",
        "check_npm_script_commands",
        "check_compose_service_commands",
        "check_runtime_parameter_key_commands",
        "check_repository_path_commands",
        "check_cli_option_commands",
        "check_localhost_probe_commands",
    )
    CHECKS_WITH_ROOT = (
        "check_current_history_headings",
        "check_document_contract_baseline",
        "check_documented_response_models",
        "check_history_metadata",
        "check_public_boundary",
        "check_safety_routes",
        "check_ci_job_timeouts",
    )

    def _run_main(self, root: Path, *, finding=None):
        markdown_paths = [Path("README.md"), Path("04_Documentation/guide.md")]
        html_paths = [Path("02_Architecture/view.html")]
        mocks = {}
        with ExitStack() as stack:
            tracked = stack.enter_context(
                patch.object(MODULE, "tracked_markdown_paths", return_value=markdown_paths)
            )
            tracked_html = stack.enter_context(
                patch.object(MODULE, "tracked_documentation_html_paths", return_value=html_paths)
            )
            for name in self.CHECKS_WITH_PATHS + self.CHECKS_WITH_ROOT:
                return_value = [finding] if name == "check_safety_routes" and finding else []
                mocks[name] = stack.enter_context(
                    patch.object(MODULE, name, return_value=return_value)
                )
            stack.enter_context(patch.object(sys, "argv", ["docs_contract_checks.py", "--root", str(root)]))
            output = io.StringIO()
            with redirect_stdout(output):
                exit_code = MODULE.main()

        tracked.assert_called_once_with(root.resolve())
        tracked_html.assert_called_once_with(root.resolve())
        for name in self.CHECKS_WITH_PATHS:
            if name == "check_relative_links":
                # Link checking also covers documentation HTML (DX-DOC-07).
                mocks[name].assert_called_once_with(root.resolve(), markdown_paths + html_paths)
            else:
                mocks[name].assert_called_once_with(root.resolve(), markdown_paths)
        for name in self.CHECKS_WITH_ROOT:
            mocks[name].assert_called_once_with(root.resolve())
        return exit_code, output.getvalue()

    def test_main_runs_every_check_and_reports_success(self):
        with tempfile.TemporaryDirectory() as td:
            exit_code, output = self._run_main(Path(td))

        self.assertEqual(exit_code, 0)
        self.assertEqual(output, "ok: checked 2 tracked Markdown files\n")

    def test_main_aggregates_findings_and_returns_failure(self):
        finding = MODULE.DocsCheckFinding(
            rule_id="DC-TEST-001",
            path="README.md",
            line=3,
            target="unsafe-target",
            message="test finding",
            fix_hint="fix it",
        )
        with tempfile.TemporaryDirectory() as td:
            exit_code, output = self._run_main(Path(td), finding=finding)

        self.assertEqual(exit_code, 1)
        self.assertIn("documentation contract validation failed:", output)
        self.assertIn(finding.render(), output)


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

    def test_reports_missing_target_in_documentation_html(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "02_Architecture").mkdir()
            source = root / "02_Architecture" / "view.html"
            source.write_text(textwrap.dedent("""\
                <!doctype html>
                <html><body>
                <p><a href="missing.md">gone</a></p>
                </body></html>
            """), encoding="utf-8")

            findings = MODULE.check_relative_links(root, [Path("02_Architecture/view.html")])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-LNK-001")
        self.assertEqual(findings[0].path, "02_Architecture/view.html")
        # The anchor sits on line 3 of the file; normalization must not shift it.
        self.assertEqual(findings[0].line, 3)
        self.assertEqual(findings[0].target, "missing.md")

    def test_accepts_existing_target_in_documentation_html(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "02_Architecture").mkdir()
            (root / "02_Architecture" / "source.md").write_text("# Source\n", encoding="utf-8")
            source = root / "02_Architecture" / "view.html"
            source.write_text('<a href="source.md">source</a>\n', encoding="utf-8")

            findings = MODULE.check_relative_links(root, [Path("02_Architecture/view.html")])

        self.assertEqual(findings, [])

    def test_ignores_html_code_scripts_and_external_targets(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "02_Architecture").mkdir()
            source = root / "02_Architecture" / "view.html"
            source.write_text(textwrap.dedent("""\
                <code>[inline](missing-inline.md)</code>
                <script src="https://cdn.example.com/x.js"></script>
                <script>var link = "[js](missing-js.md)";</script>
                <a href="https://example.com/missing">web</a>
                <a href="#section">anchor</a>
                <img src="missing-image.png">
            """), encoding="utf-8")

            findings = MODULE.check_relative_links(root, [Path("02_Architecture/view.html")])

        # <code> is stripped like inline code, script bodies are dropped, and
        # external/anchor targets are skipped. src attributes are not link
        # targets for this rule, which only reads anchors.
        self.assertEqual(findings, [])

    def test_html_to_markdownish_preserves_line_numbers_and_shapes(self):
        raw = textwrap.dedent("""\
            <p>intro</p>
            <script>
            dropped
            </script>
            <a href="t.md">label</a>
            <code>01_Plans/x.md</code>
        """)

        text = MODULE.html_to_markdownish(raw)

        self.assertEqual(text.count("\n"), raw.count("\n"))
        self.assertIn("[label](t.md)", text)
        self.assertIn("`01_Plans/x.md`", text)
        self.assertNotIn("dropped", text)

    def test_tracked_documentation_html_paths_excludes_application_html(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "02_Architecture").mkdir()
            (root / "03_Implement" / "frontend").mkdir(parents=True)
            (root / "02_Architecture" / "view.html").write_text("<p>doc</p>\n", encoding="utf-8")
            (root / "03_Implement" / "frontend" / "index.html").write_text(
                '<script type="module" src="/src/main.tsx"></script>\n', encoding="utf-8"
            )
            subprocess.run(
                ["git", "-C", str(root), "add", "02_Architecture/view.html", "03_Implement/frontend/index.html"],
                check=True,
            )

            paths = MODULE.tracked_documentation_html_paths(root)

        self.assertEqual(paths, [Path("02_Architecture/view.html")])

    def test_tracked_markdown_paths_excludes_untracked_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            (root / "tracked.md").write_text("# Tracked\n", encoding="utf-8")
            (root / "untracked.md").write_text("# Untracked\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "tracked.md"], check=True)

            paths = MODULE.tracked_markdown_paths(root)

        self.assertEqual(paths, [Path("tracked.md")])

    def test_tracked_markdown_paths_excludes_deleted_worktree_files(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            present = root / "present.md"
            deleted = root / "deleted.md"
            present.write_text("# Present\n", encoding="utf-8")
            deleted.write_text("# Deleted\n", encoding="utf-8")
            subprocess.run(
                ["git", "-C", str(root), "add", "present.md", "deleted.md"],
                check=True,
            )
            deleted.unlink()

            paths = MODULE.tracked_markdown_paths(root)

        self.assertEqual(paths, [Path("present.md")])


class AdrIdUniquenessCheckTest(unittest.TestCase):
    def test_reports_duplicate_adr_numbers_with_different_slugs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adr_dir = root / "01_Plans" / "adr"
            adr_dir.mkdir(parents=True)
            first = Path("01_Plans/adr/ADR-0059-first.md")
            second = Path("01_Plans/adr/ADR-0059-second.md")
            (root / first).write_text("# ADR-0059: first\n", encoding="utf-8")
            (root / second).write_text("# ADR-0059: second\n", encoding="utf-8")

            findings = MODULE.check_adr_id_uniqueness(root, [first, second])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-ADR-001")
        self.assertEqual(findings[0].target, "ADR-0059")
        self.assertIn("ADR-0059-first.md", findings[0].message)
        self.assertIn("ADR-0059-second.md", findings[0].message)

    def test_accepts_unique_adr_numbers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adr_dir = root / "01_Plans" / "adr"
            adr_dir.mkdir(parents=True)
            first = Path("01_Plans/adr/ADR-0059-first.md")
            second = Path("01_Plans/adr/ADR-0060-second.md")
            (root / first).write_text("# ADR-0059: first\n", encoding="utf-8")
            (root / second).write_text("# ADR-0060: second\n", encoding="utf-8")

            findings = MODULE.check_adr_id_uniqueness(root, [first, second])

        self.assertEqual(findings, [])


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


class DocumentedResponseModelsTest(unittest.TestCase):
    def _write_required_docs(self, root: Path) -> None:
        for path, terms in MODULE.DOCUMENTED_RESPONSE_MODEL_REQUIRED_TERMS.items():
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("\n".join(terms), encoding="utf-8")

    def test_accepts_all_required_endpoint_and_model_markers(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_required_docs(root)

            findings = MODULE.check_documented_response_models(root)

        self.assertEqual(findings, [])

    def test_reports_missing_marker_in_each_canonical_doc(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_required_docs(root)
            api_path = root / "02_Architecture" / "api.md"
            api_path.write_text(
                api_path.read_text(encoding="utf-8").replace("/ai/provider-status", ""),
                encoding="utf-8",
            )
            schemas_path = root / "02_Architecture" / "schemas.md"
            schemas_path.write_text(
                schemas_path.read_text(encoding="utf-8").replace("totalGroupCount", ""),
                encoding="utf-8",
            )

            findings = MODULE.check_documented_response_models(root)

        self.assertEqual(
            {(finding.path, finding.target) for finding in findings},
            {
                ("02_Architecture/api.md", "/ai/provider-status"),
                ("02_Architecture/schemas.md", "totalGroupCount"),
            },
        )
        self.assertTrue(all(finding.rule_id == "DC-API-001" for finding in findings))


class AdrTraceabilityPathCheckTest(unittest.TestCase):
    def test_reports_missing_adr_traceability_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adr_dir = root / "01_Plans" / "adr"
            adr_dir.mkdir(parents=True)
            source = Path("01_Plans/adr/ADR-0001-source.md")
            (root / source).write_text(
                "# ADR-0001\n\n- Supersedes: `01_Plans/adr/ADR-0002-missing.md`\n",
                encoding="utf-8",
            )

            findings = MODULE.check_adr_traceability_paths(root, [source])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "DC-ADR-002")
        self.assertEqual(findings[0].line, 3)
        self.assertEqual(findings[0].target, "01_Plans/adr/ADR-0002-missing.md")

    def test_accepts_existing_adr_and_ignores_superseded_non_adr_documents(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            adr_dir = root / "01_Plans" / "adr"
            adr_dir.mkdir(parents=True)
            source = Path("01_Plans/adr/ADR-0001-source.md")
            target = Path("01_Plans/adr/ADR-0002-target.md")
            (root / source).write_text(
                "# ADR-0001\n\n"
                "- Derived-from: `01_Plans/adr/ADR-0002-target.md`\n"
                "- Supersedes: `01_Plans/legacy-plan.md`\n",
                encoding="utf-8",
            )
            (root / target).write_text("# ADR-0002\n", encoding="utf-8")

            findings = MODULE.check_adr_traceability_paths(root, [source, target])

        self.assertEqual(findings, [])


class CiJobTimeoutCheckTest(unittest.TestCase):
    def test_reports_each_job_without_a_valid_timeout(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.yml"
            workflow.write_text(
                "jobs:\n"
                "  missing:\n"
                "    runs-on: ubuntu-latest\n"
                "  zero:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 0\n"
                "  valid:\n"
                "    runs-on: ubuntu-latest\n"
                "    timeout-minutes: 30\n",
                encoding="utf-8",
            )

            findings = MODULE.check_ci_job_timeouts(root, (Path("workflow.yml"),))

        self.assertEqual([finding.target for finding in findings], ["missing", "zero"])
        self.assertTrue(all(finding.rule_id == "DC-CI-001" for finding in findings))

    def test_accepts_bounded_timeout_for_every_job(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            workflow = root / "workflow.yml"
            workflow.write_text(
                "jobs:\n"
                "  first-job:\n"
                "    timeout-minutes: 5\n"
                "  second_job:\n"
                "    timeout-minutes: 360\n",
                encoding="utf-8",
            )

            findings = MODULE.check_ci_job_timeouts(root, (Path("workflow.yml"),))

        self.assertEqual(findings, [])


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


class PublicBoundaryTest(unittest.TestCase):
    def _write_fixtures(self, root: Path, entry: str, catalog: str, ledger: str) -> None:
        docs = root / "04_Documentation"
        screenshots = docs / "assets" / "screenshots"
        screenshots.mkdir(parents=True)
        (docs / "public_index.md").write_text(entry, encoding="utf-8")
        (docs / "ui_catalog.md").write_text(catalog, encoding="utf-8")
        (screenshots / "README.md").write_text(ledger, encoding="utf-8")

    def test_accepts_public_entry_and_complete_ui_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                "[現行UIカタログ](ui_catalog.md)\n",
                "\n".join(MODULE.PUBLIC_UI_CATALOG_REQUIRED_TERMS),
                "\n".join(MODULE.SCREENSHOT_LEDGER_REQUIRED_TERMS),
            )

            findings = MODULE.check_public_boundary(root)

        self.assertEqual(findings, [])

    def test_reports_internal_markers_missing_route_and_missing_provenance(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_fixtures(
                root,
                "内部管理は 01_Plans を参照します。\n",
                "ADR-9999 の設計指示です。\n",
                "撮影日だけあります。\n",
            )

            findings = MODULE.check_public_boundary(root)

        self.assertTrue(all(f.rule_id == "DC-PUB-001" for f in findings))
        targets = {f.target for f in findings}
        self.assertIn("内部管理", targets)
        self.assertIn("01_Plans", targets)
        self.assertIn("ADR-", targets)
        self.assertIn("ui_catalog.md", targets)
        self.assertIn("確認対象revision", targets)
        self.assertIn("source revision", targets)


class SafetyRouteTest(unittest.TestCase):
    def _write_fixtures(self, root: Path, agent_text: str, public_text: str) -> None:
        (root / "AGENTS.md").write_text(agent_text, encoding="utf-8")
        (root / "THREAT_MODEL.md").write_text("# Threat model\n", encoding="utf-8")
        (root / "02_Architecture").mkdir()
        (root / "02_Architecture" / "architecture.md").write_text("# Architecture\n", encoding="utf-8")
        docs = root / "04_Documentation"
        docs.mkdir()
        (docs / "public_index.md").write_text(public_text, encoding="utf-8")
        for destination, required_terms in MODULE.PUBLIC_SAFETY_ROUTES.items():
            (docs / destination).write_text("\n".join(required_terms), encoding="utf-8")

    def test_accepts_complete_agent_invariants_and_public_routes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = "\n".join(f"[{name}]({name})" for name in MODULE.PUBLIC_SAFETY_ROUTES)
            agent_text = "\n".join(
                (*MODULE.AGENT_SAFETY_REQUIRED_TERMS, *MODULE.AGENT_SAFETY_REQUIRED_ROUTES)
            )
            self._write_fixtures(root, agent_text, routes)

            findings = MODULE.check_safety_routes(root)

        self.assertEqual(findings, [])

    def test_reports_missing_invariant_route_and_target_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            routes = "\n".join(
                f"[{name}]({name})"
                for name in MODULE.PUBLIC_SAFETY_ROUTES
                if name != "security.md"
            )
            self._write_fixtures(root, "THREAT_MODEL.md\n", routes)
            (root / "04_Documentation" / "ce2_low_risk_ai_assist.md").write_text(
                "proposal-only\n", encoding="utf-8"
            )

            findings = MODULE.check_safety_routes(root)

        self.assertTrue(all(f.rule_id == "DC-SAF-001" for f in findings))
        targets = {f.target for f in findings}
        self.assertIn("SafeModeは既定ON", targets)
        self.assertIn("02_Architecture/architecture.md", targets)
        self.assertIn("security.md", targets)
        self.assertIn("human_reviewed", targets)


class NpmScriptCommandCheckTest(unittest.TestCase):
    def _write_package_json(self, root: Path, scripts: dict[str, str]) -> None:
        package_dir = root / "03_Implement" / "frontend"
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "package.json").write_text(
            f'{{"name": "kj-atlas-frontend", "scripts": {_scripts_json(scripts)}}}',
            encoding="utf-8",
        )

    def test_accepts_existing_script_names_in_public_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_package_json(root, {"typecheck": "tsc --noEmit", "test": "vitest run"})
            readme = root / "README.md"
            readme.write_text("```bash\nnpm run typecheck\nnpm run test\n```\n", encoding="utf-8")

            findings = MODULE.check_npm_script_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_reports_script_name_missing_from_package_json(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_package_json(root, {"typecheck": "tsc --noEmit"})
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "installation.md"
            doc.write_text("```bash\nnpm run docs-check\n```\n", encoding="utf-8")

            findings = MODULE.check_npm_script_commands(root, [Path("04_Documentation/installation.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/installation.md")
        self.assertEqual(finding.line, 2)
        self.assertEqual(finding.target, "npm run docs-check")
        self.assertIn("does not exist", finding.message)

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_package_json(root, {"typecheck": "tsc --noEmit"})
            issues_dir = root / "01_Plans" / "issues"
            issues_dir.mkdir(parents=True)
            memo = issues_dir / "issue-example.md"
            memo.write_text("検証コマンド宣言: `npm run docs-check`\n", encoding="utf-8")

            findings = MODULE.check_npm_script_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])


def _scripts_json(scripts: dict[str, str]) -> str:
    import json

    return json.dumps(scripts)


class ComposeServiceCommandCheckTest(unittest.TestCase):
    def _write_compose_file(self, root: Path, services: list[str]) -> None:
        deploy_dir = root / "03_Implement" / "deploy"
        deploy_dir.mkdir(parents=True, exist_ok=True)
        body = "services:\n" + "".join(f"  {name}:\n    image: placeholder\n" for name in services)
        body += "\nvolumes:\n  kj_atlas_pgdata:\n"
        (deploy_dir / "docker-compose.yml").write_text(body, encoding="utf-8")

    def test_accepts_existing_service_names_in_public_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_compose_file(root, ["api", "db", "web"])
            readme = root / "README.md"
            readme.write_text(
                "```bash\ndocker compose logs api --tail=100\ndocker compose exec -T db pg_dump\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_compose_service_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_reports_service_name_missing_from_compose_file(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_compose_file(root, ["api", "db"])
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "operations.md"
            doc.write_text("```bash\ndocker compose logs worker --tail=100\n```\n", encoding="utf-8")

            findings = MODULE.check_compose_service_commands(root, [Path("04_Documentation/operations.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/operations.md")
        self.assertEqual(finding.line, 2)
        self.assertEqual(finding.target, "docker compose logs worker")
        self.assertIn("does not exist", finding.message)

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_compose_file(root, ["api", "db"])
            issues_dir = root / "01_Plans" / "issues"
            issues_dir.mkdir(parents=True)
            memo = issues_dir / "issue-example.md"
            memo.write_text("検証コマンド宣言: `docker compose logs worker`\n", encoding="utf-8")

            findings = MODULE.check_compose_service_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])

    def test_ignores_project_wide_subcommands_without_a_service_argument(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_compose_file(root, ["api", "db"])
            readme = root / "README.md"
            readme.write_text(
                "```bash\ndocker compose up --build -d\ndocker compose ps\ndocker compose down -v\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_compose_service_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])


class RuntimeParameterKeyCheckTest(unittest.TestCase):
    def _write_registry(self, root: Path, keys: list[str]) -> None:
        arch_dir = root / "02_Architecture"
        arch_dir.mkdir(parents=True, exist_ok=True)
        body = "# Runtime Parameter Registry\n\n## Backend settings\n\n"
        body += "| Key | Default | Purpose |\n| --- | --- | --- |\n"
        body += "".join(f"| `{key}` | none | placeholder |\n" for key in keys)
        (arch_dir / "runtime_parameter_registry.md").write_text(body, encoding="utf-8")

    def test_accepts_existing_keys_in_public_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_registry(root, ["KJ_ATLAS_LLM_PROVIDER", "KJ_ATLAS_API_KEY"])
            readme = root / "README.md"
            readme.write_text(
                "```bash\nexport KJ_ATLAS_LLM_PROVIDER=none\nexport KJ_ATLAS_API_KEY=change-me\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_runtime_parameter_key_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_accepts_registry_row_with_a_trailing_annotation_marker(self):
        # Real registry rows mark known gaps with a trailing "⚠️" between the
        # closing backtick and the next `|` (e.g. `` `KJ_ATLAS_API_KEY` ⚠️ ``);
        # the row-extraction regex must not require the backtick to be
        # immediately followed by whitespace-then-pipe.
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            arch_dir = root / "02_Architecture"
            arch_dir.mkdir(parents=True)
            (arch_dir / "runtime_parameter_registry.md").write_text(
                "| Key | Default | Purpose |\n| --- | --- | --- |\n"
                "| `KJ_ATLAS_API_KEY` ⚠️ | 未設定 | protects the API |\n",
                encoding="utf-8",
            )
            readme = root / "README.md"
            readme.write_text("```bash\nexport KJ_ATLAS_API_KEY=change-me\n```\n", encoding="utf-8")

            findings = MODULE.check_runtime_parameter_key_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_reports_key_missing_from_registry(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_registry(root, ["KJ_ATLAS_LLM_PROVIDER"])
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "configuration.md"
            doc.write_text("```bash\nexport KJ_ATLAS_NONEXISTENT_KEY=1\n```\n", encoding="utf-8")

            findings = MODULE.check_runtime_parameter_key_commands(root, [Path("04_Documentation/configuration.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/configuration.md")
        self.assertEqual(finding.line, 2)
        self.assertEqual(finding.target, "KJ_ATLAS_NONEXISTENT_KEY")
        self.assertIn("does not exist", finding.message)

    def test_ignores_prefix_family_mentions(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_registry(root, ["KJ_ATLAS_AUDIT_EXPORT_ENABLED"])
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "security.md"
            doc.write_text("監査系設定は `KJ_ATLAS_AUDIT_*` を参照してください。\n", encoding="utf-8")

            findings = MODULE.check_runtime_parameter_key_commands(root, [Path("04_Documentation/security.md")])

        self.assertEqual(findings, [])

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_registry(root, ["KJ_ATLAS_LLM_PROVIDER"])
            issues_dir = root / "01_Plans" / "issues"
            issues_dir.mkdir(parents=True)
            memo = issues_dir / "issue-example.md"
            memo.write_text("検証コマンド宣言: `KJ_ATLAS_NONEXISTENT_KEY=1`\n", encoding="utf-8")

            findings = MODULE.check_runtime_parameter_key_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])


class RepositoryPathCheckTest(unittest.TestCase):
    def test_accepts_existing_paths_in_public_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target_dir = root / "03_Implement" / "backend"
            target_dir.mkdir(parents=True)
            (target_dir / "settings.py").write_text("", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text("設定は `03_Implement/backend/settings.py` を参照。\n", encoding="utf-8")

            findings = MODULE.check_repository_path_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_reports_missing_path(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "installation.md"
            doc.write_text("設定は `03_Implement/backend/does_not_exist.py` を参照。\n", encoding="utf-8")

            findings = MODULE.check_repository_path_commands(root, [Path("04_Documentation/installation.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/installation.md")
        self.assertEqual(finding.line, 1)
        self.assertEqual(finding.target, "03_Implement/backend/does_not_exist.py")
        self.assertIn("does not exist", finding.message)

    def test_ignores_placeholder_tokens(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "configuration.md"
            doc.write_text("`03_Implement/<component>/settings.py` のように置き換えます。\n", encoding="utf-8")

            findings = MODULE.check_repository_path_commands(root, [Path("04_Documentation/configuration.md")])

        self.assertEqual(findings, [])

    def test_accepts_existing_path_with_trailing_line_reference(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target_dir = root / "03_Implement" / "backend"
            target_dir.mkdir(parents=True)
            (target_dir / "main.py").write_text("line1\nline2\n", encoding="utf-8")
            readme = root / "README.md"
            readme.write_text("詳細は `03_Implement/backend/main.py:42` を参照。\n", encoding="utf-8")

            findings = MODULE.check_repository_path_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            issues_dir = root / "01_Plans" / "issues"
            issues_dir.mkdir(parents=True)
            memo = issues_dir / "issue-example.md"
            memo.write_text("参照: `03_Implement/backend/does_not_exist.py`\n", encoding="utf-8")

            findings = MODULE.check_repository_path_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])

    def test_accepts_build_output_path_absent_before_a_build_runs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            frontend_dir = root / "03_Implement" / "frontend"
            frontend_dir.mkdir(parents=True)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "release.md"
            doc.write_text(
                "GitHub Actions artifact（`03_Implement/frontend/dist`の内容）を取得する。\n",
                encoding="utf-8",
            )

            findings = MODULE.check_repository_path_commands(root, [Path("04_Documentation/release.md")])

        self.assertEqual(findings, [])

    def test_reports_missing_path_under_a_nonexistent_parent_even_with_a_build_output_leaf(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "release.md"
            doc.write_text(
                "誤った参照 `03_Implement/wrong-place/dist` は検出される。\n",
                encoding="utf-8",
            )

            findings = MODULE.check_repository_path_commands(root, [Path("04_Documentation/release.md")])

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].target, "03_Implement/wrong-place/dist")


class CliOptionCheckTest(unittest.TestCase):
    def _write_script(self, root: Path, rel_path: str, body: str) -> None:
        script_path = root / rel_path
        script_path.parent.mkdir(parents=True, exist_ok=True)
        script_path.write_text(body, encoding="utf-8")

    def test_accepts_existing_options_in_public_docs(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_script(
                root,
                "03_Implement/deploy/tools/mock_local_llm.py",
                "import argparse\n"
                "parser = argparse.ArgumentParser()\n"
                "parser.add_argument('--host', default='127.0.0.1')\n"
                "parser.add_argument('--port', type=int, default=8001)\n",
            )
            readme = root / "README.md"
            readme.write_text(
                "```bash\npython3 03_Implement/deploy/tools/mock_local_llm.py --host 127.0.0.1 --port 8001\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_cli_option_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_reports_unknown_option(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_script(
                root,
                "01_Plans/issues/validate_active_issue_memos.py",
                "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--root')\n",
            )
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "installation.md"
            doc.write_text(
                "```bash\npython3 01_Plans/issues/validate_active_issue_memos.py --files x.md\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_cli_option_commands(root, [Path("04_Documentation/installation.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/installation.md")
        self.assertEqual(finding.target, "01_Plans/issues/validate_active_issue_memos.py --files")
        self.assertIn("does not exist", finding.message)

    def test_skips_script_without_argparse(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_script(root, "03_Implement/deploy/tools/no_parser.py", "print('hello')\n")
            readme = root / "README.md"
            readme.write_text(
                "```bash\npython3 03_Implement/deploy/tools/no_parser.py --whatever\n```\n",
                encoding="utf-8",
            )

            findings = MODULE.check_cli_option_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._write_script(
                root,
                "01_Plans/issues/validate_active_issue_memos.py",
                "import argparse\nparser = argparse.ArgumentParser()\nparser.add_argument('--root')\n",
            )
            issues_dir = root / "01_Plans" / "issues"
            memo = issues_dir / "issue-example.md"
            memo.write_text(
                "検証コマンド宣言: `python3 01_Plans/issues/validate_active_issue_memos.py --files x.md`\n",
                encoding="utf-8",
            )

            findings = MODULE.check_cli_option_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])


class LocalhostProbeCheckTest(unittest.TestCase):
    def test_accepts_allowlisted_exact_url(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            readme = root / "README.md"
            readme.write_text("```bash\ncurl -fsS http://localhost:8080/api/healthz\n```\n", encoding="utf-8")

            findings = MODULE.check_localhost_probe_commands(root, [Path("README.md")])

        self.assertEqual(findings, [])

    def test_accepts_allowlisted_prefix_url(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "acceptance_check.md"
            doc.write_text("`curl http://localhost:8080/api/docs/doc_phase1_canvas`\n", encoding="utf-8")

            findings = MODULE.check_localhost_probe_commands(root, [Path("04_Documentation/acceptance_check.md")])

        self.assertEqual(findings, [])

    def test_reports_known_bug_shape_missing_trailing_z(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            doc_dir = root / "04_Documentation"
            doc_dir.mkdir()
            doc = doc_dir / "installation.md"
            doc.write_text("```bash\ncurl -fsS http://localhost:8080/api/health\n```\n", encoding="utf-8")

            findings = MODULE.check_localhost_probe_commands(root, [Path("04_Documentation/installation.md")])

        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, "DC-CMD-001")
        self.assertEqual(finding.path, "04_Documentation/installation.md")
        self.assertEqual(finding.line, 2)
        self.assertEqual(finding.target, "http://localhost:8080/api/health")
        self.assertIn("not in the probe allowlist", finding.message)

    def test_ignores_process_memos_outside_the_public_doc_scope(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            issues_dir = root / "01_Plans" / "issues"
            issues_dir.mkdir(parents=True)
            memo = issues_dir / "issue-example.md"
            memo.write_text("検証コマンド宣言: `curl http://localhost:8080/api/health`\n", encoding="utf-8")

            findings = MODULE.check_localhost_probe_commands(root, [Path("01_Plans/issues/issue-example.md")])

        self.assertEqual(findings, [])


if __name__ == "__main__":
    unittest.main()
