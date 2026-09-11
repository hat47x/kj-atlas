from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/sui_sensemaking_api/settings.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _public_row(path: Path, key: str) -> str:
    text = path.read_text(encoding="utf-8")
    if path == REGISTRY_PATH:
        text = text.split("## Backend settings", 1)[1].split(
            "## Compose and frontend build keys", 1
        )[0]
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(
            f"expected one public row for {key} in {path}, got {len(rows)}"
        )
    return rows[0]


def _settings_validator_source() -> str:
    text = SETTINGS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(text)
    settings_class = next(
        node
        for node in tree.body
        if isinstance(node, ast.ClassDef) and node.name == "Settings"
    )
    validator = next(
        node
        for node in settings_class.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name == "validate_llm_provider_guards"
    )
    if validator.end_lineno is None:
        raise AssertionError("Settings validator source range is unavailable")
    return "\n".join(
        text.splitlines()[validator.lineno - 1 : validator.end_lineno]
    )


class ControlPlaneCredentialSeparationContractTests(unittest.TestCase):
    def test_business_and_admin_api_keys_must_be_distinct_everywhere_public(self) -> None:
        validator = _settings_validator_source()
        self.assertIn("self.api_key == self.admin_api_key", validator)
        self.assertIn(
            "SUI_API_KEY and SUI_ADMIN_API_KEY must be distinct",
            validator,
        )

        for row in (
            _public_row(REGISTRY_PATH, "SUI_ADMIN_API_KEY"),
            _public_row(CONFIG_PATH, "SUI_ADMIN_API_KEY"),
        ):
            self.assertIn("SUI_API_KEY", row)
            self.assertIn("同じ秘密値", row)
            self.assertIn("起動時に拒否", row)


if __name__ == "__main__":
    unittest.main()
