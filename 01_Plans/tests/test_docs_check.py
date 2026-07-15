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


class DocsCheckEntrypointTest(unittest.TestCase):
    def _repository(self, root: Path, guide_text: str) -> None:
        (root / "01_Plans" / "issues").mkdir(parents=True)
        (root / "01_Plans" / "adr").mkdir()
        (root / "docs").mkdir()
        (root / "docs" / "guide.md").write_text(guide_text, encoding="utf-8")
        for relative_path in MODULE.CURRENT_ONLY_PATHS:
            target = root / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Current contract\n", encoding="utf-8")
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "add", "."], cwd=root, check=True)

    def test_run_docs_check_passes_clean_minimal_repository(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            self._repository(root, "# Guide\n")

            result = MODULE.run_docs_check(root, run_tests=False)

        self.assertEqual(result.active_count, 0)
        self.assertEqual(result.markdown_count, 8)
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
            current_doc = root / MODULE.CURRENT_ONLY_PATHS[0]
            current_doc.write_text("# Current contract\n\n## Rerun checkpoint\n", encoding="utf-8")

            result = MODULE.run_docs_check(root, run_tests=False)

        self.assertEqual(len(result.errors), 1)
        self.assertIn("DC-CUR-001 01_Plans/project-progress-dashboard.md:3", result.errors[0])


if __name__ == "__main__":
    unittest.main()
