from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _function_source(name: str) -> str:
    text = SETTINGS_PATH.read_text(encoding="utf-8")
    tree = ast.parse(text)
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    if node.end_lineno is None:
        raise AssertionError(f"source range unavailable for {name}")
    return "\n".join(text.splitlines()[node.lineno - 1 : node.end_lineno])


def _public_row(path: Path, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in path.read_text(encoding="utf-8").splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one public row for {key} in {path}, got {len(rows)}")
    return rows[0]


class OAuthClientFormatContractTests(unittest.TestCase):
    def test_client_id_and_secret_match_public_canonical_format(self) -> None:
        validator = _function_source("validate_llm_provider_guards")
        header_helper = _function_source("_validate_optional_header_value")
        bearer_helper = _function_source("_validate_canonical_bearer")

        self.assertIn("len(value) > 2048", header_helper)
        self.assertIn("any(character.isspace() for character in value)", header_helper)
        self.assertIn("any(not character.isprintable() for character in value)", header_helper)
        self.assertIn("not api_key", bearer_helper)
        self.assertIn("any(character.isspace() for character in api_key)", bearer_helper)
        self.assertIn("any(not character.isprintable() for character in api_key)", bearer_helper)
        self.assertIn("value=self.saas_oauth_broker_http_client_id", validator)
        self.assertIn('value_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID"', validator)
        self.assertIn("api_key=self.saas_oauth_broker_http_client_secret", validator)
        self.assertIn('api_key_key="KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET"', validator)

        for row in (
            _public_row(REGISTRY_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID"),
            _public_row(CONFIG_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID"),
        ):
            for term in ("2,048", "canonical", "空白", "制御文字"):
                self.assertIn(term, row)

        for row in (
            _public_row(REGISTRY_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET"),
            _public_row(CONFIG_PATH, "KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET"),
        ):
            for term in ("非空", "canonical bearer", "空白", "制御文字"):
                self.assertIn(term, row)


if __name__ == "__main__":
    unittest.main()
