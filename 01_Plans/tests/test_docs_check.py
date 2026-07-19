import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_check.py"
sys.path.insert(0, str(MODULE_PATH.parent))
SPEC = importlib.util.spec_from_file_location("docs_check", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
CHECKS = sys.modules["docs_contract_checks"]


class DocsCheckEntrypointTest(unittest.TestCase):
    def _repository(self, root: Path, guide_text: str) -> None:
        (root / "01_Plans" / "issues").mkdir(parents=True)
        (root / "01_Plans" / "adr").mkdir()
        (root / "docs").mkdir()
        (root / "docs" / "guide.md").write_text(guide_text, encoding="utf-8")
        for relative_path in CHECKS.CURRENT_ONLY_PATHS:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Current contract\n", encoding="utf-8")
        (root / "02_Architecture" / "schemas.md").write_text(
            "```ts\nexport type DocumentV1 = {\n  version: 1;\n};\n```\n",
            encoding="utf-8",
        )
        (root / "02_Architecture" / "api.md").write_text("DocumentV1 API.\n", encoding="utf-8")
        (root / "02_Architecture" / "data_model_operations_overview.md").write_text(
            "DocumentV1 support.\n", encoding="utf-8"
        )
        for relative_path, required_terms in CHECKS.DOCUMENTED_RESPONSE_MODEL_REQUIRED_TERMS.items():
            target = root / relative_path
            target.write_text(
                target.read_text(encoding="utf-8") + "\n".join(required_terms) + "\n",
                encoding="utf-8",
            )
        screenshots = root / "04_Documentation" / "assets" / "screenshots"
        screenshots.mkdir(parents=True)
        (root / "04_Documentation" / "public_index.md").write_text(
            "[現行UIカタログ](ui_catalog.md)\n"
            + "\n".join(f"[{name}]({name})" for name in CHECKS.PUBLIC_SAFETY_ROUTES)
            + "\n",
            encoding="utf-8",
        )
        (root / "04_Documentation" / "ui_catalog.md").write_text(
            "\n".join(CHECKS.PUBLIC_UI_CATALOG_REQUIRED_TERMS), encoding="utf-8"
        )
        (screenshots / "README.md").write_text(
            "\n".join(CHECKS.SCREENSHOT_LEDGER_REQUIRED_TERMS), encoding="utf-8"
        )
        for destination, required_terms in CHECKS.PUBLIC_SAFETY_ROUTES.items():
            (root / "04_Documentation" / destination).write_text(
                "\n".join(required_terms), encoding="utf-8"
            )
        (root / "AGENTS.md").write_text(
            "\n".join(
                (*CHECKS.AGENT_SAFETY_REQUIRED_TERMS, *CHECKS.AGENT_SAFETY_REQUIRED_ROUTES)
            ),
            encoding="utf-8",
        )
        (root / "THREAT_MODEL.md").write_text("# Threat model\n", encoding="utf-8")
        history_dir = root / "02_Architecture" / "history"
        history_dir.mkdir(parents=True, exist_ok=True)
        history = history_dir / "formation.md"
        source = root / CHECKS.CURRENT_ONLY_PATHS[3]
        source.write_text(
            "# Current contract\n\n[Formation history](history/formation.md)\n",
            encoding="utf-8",
        )
        history.write_text(
            "# Formation history\n\n"
            "Status: Informative history\n\n"
            "Source document: [Current](../architecture.md)\n\n"
            "Source anchors: former §1\n\n"
            "Covered period: 2026-01-01\n\n"
            "Snapshot / source revision: `abc123`\n\n"
            "Retention reason: Preserve formation context.\n\n"
            "Current normative anchors:\n\n"
            "- [Current](../architecture.md#current-contract)\n\n"
            "## Former record\n",
            encoding="utf-8",
        )
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)

    def test_run_docs_check_passes_clean_minimal_repository(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repository(root, "# Guide\n")

            result = MODULE.run_docs_check(root, run_tests=False)

        self.assertEqual(result.active_count, 0)
        self.assertGreaterEqual(result.markdown_count, 7)
        self.assertEqual(result.errors, ())

    def test_run_docs_check_reports_broken_relative_link(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repository(root, "[missing](missing.md)\n")

            result = MODULE.run_docs_check(root, run_tests=False)

        self.assertEqual(len(result.errors), 1)
        self.assertIn("DC-LNK-001 docs/guide.md:1", result.errors[0])

    def test_run_docs_check_reports_current_history_heading(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repository(root, "# Guide\n")
            current_doc = root / CHECKS.CURRENT_ONLY_PATHS[0]
            current_doc.write_text("# Current contract\n\n## Rerun checkpoint\n", encoding="utf-8")

            result = MODULE.run_docs_check(root, run_tests=False)

        self.assertEqual(len(result.errors), 1)
        self.assertIn("DC-CUR-001 01_Plans/project-progress-dashboard.md:3", result.errors[0])


if __name__ == "__main__":
    unittest.main()
