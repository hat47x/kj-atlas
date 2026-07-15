import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_check.py"
SPEC = importlib.util.spec_from_file_location("docs_check", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class DocsCheckEntrypointTest(unittest.TestCase):
    def test_runs_tests_validator_and_contract_checker(self):
        commands = MODULE.check_commands(MODULE.ROOT)
        rendered = [" ".join(command) for command in commands]

        self.assertEqual(len(commands), 4)
        self.assertTrue(any("01_Plans\\tests" in command or "01_Plans/tests" in command for command in rendered))
        self.assertTrue(any("issues" in command and "tests" in command for command in rendered))
        self.assertTrue(any("validate_active_issue_memos.py" in command for command in rendered))
        self.assertTrue(any("docs_contract_checks.py" in command for command in rendered))


if __name__ == "__main__":
    unittest.main()
