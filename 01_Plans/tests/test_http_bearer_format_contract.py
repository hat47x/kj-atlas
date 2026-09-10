from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/sui_sensemaking_api/settings.py"
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


class HttpBearerFormatContractTests(unittest.TestCase):
    def test_outbound_http_credentials_share_canonical_bearer_contract(self) -> None:
        validator = _function_source("validate_llm_provider_guards")
        optional_http = _function_source("_validate_optional_http_integration")
        trusted_resolver = _function_source("_validate_trusted_http_resolver")
        bearer = _function_source("_validate_canonical_bearer")

        self.assertIn("_validate_canonical_bearer", optional_http)
        self.assertIn("_validate_canonical_bearer", trusted_resolver)
        self.assertIn("not api_key", bearer)
        self.assertIn("any(character.isspace() for character in api_key)", bearer)
        self.assertIn("any(not character.isprintable() for character in api_key)", bearer)

        field_keys = (
            ("self.audit_http_api_key", "SUI_AUDIT_HTTP_API_KEY"),
            (
                "self.access_control_external_http_static_bearer_token",
                "SUI_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN",
            ),
            (
                "self.document_policy_binding_http_api_key",
                "SUI_DOCUMENT_POLICY_BINDING_HTTP_API_KEY",
            ),
            (
                "self.tenant_capability_http_api_key",
                "SUI_TENANT_CAPABILITY_HTTP_API_KEY",
            ),
        )
        for field, key in field_keys:
            self.assertIn(field, validator)
            self.assertIn(f'"{key}"', validator)
            for row in (_public_row(REGISTRY_PATH, key), _public_row(CONFIG_PATH, key)):
                for term in ("非空", "canonical bearer", "空白", "制御文字"):
                    self.assertIn(term, row)


if __name__ == "__main__":
    unittest.main()
