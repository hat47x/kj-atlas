import importlib.util
import sys
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "ci_change_scope.py"
SPEC = importlib.util.spec_from_file_location("ci_change_scope", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class ChangeScopeTest(unittest.TestCase):
    def test_docs_only_change_skips_application_jobs(self):
        scope = MODULE.classify_changes(
            ["04_Documentation/public_index.md", "01_Plans/issues/issue-DX-DOC-02.md"]
        )

        self.assertFalse(scope.frontend)
        self.assertFalse(scope.backend)
        self.assertFalse(scope.mcp)

    def test_frontend_and_backend_changes_are_independent(self):
        frontend = MODULE.classify_changes(["03_Implement/frontend/src/App.tsx"])
        backend = MODULE.classify_changes(["03_Implement/backend/src/kj_atlas_api/main.py"])

        self.assertEqual(frontend, MODULE.ChangeScope(frontend=True, backend=False, mcp=False))
        self.assertEqual(backend, MODULE.ChangeScope(frontend=False, backend=True, mcp=False))

    def test_mcp_change_is_independent(self):
        mcp = MODULE.classify_changes(["03_Implement/mcp/src/http_server.ts"])

        self.assertFalse(mcp.frontend)
        self.assertFalse(mcp.backend)
        self.assertTrue(mcp.mcp)

    def test_ci_or_classifier_change_runs_both_application_scopes(self):
        for path in MODULE.RUN_ALL_PATHS:
            with self.subTest(path=path):
                self.assertEqual(
                    MODULE.classify_changes([path]),
                    MODULE.ChangeScope(frontend=True, backend=True, mcp=True),
                )

    def test_windows_separators_are_normalized(self):
        scope = MODULE.classify_changes([r"03_Implement\frontend\src\App.tsx"])

        self.assertTrue(scope.frontend)
        self.assertFalse(scope.backend)
        self.assertFalse(scope.mcp)


if __name__ == "__main__":
    unittest.main()
