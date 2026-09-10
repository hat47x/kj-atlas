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
    return ast.get_source_segment(text, node) or ""


class HttpIntegrationDisableCleanupContractTests(unittest.TestCase):
    def test_disabled_http_integration_rejects_leftover_endpoint_or_api_key(self) -> None:
        helper = _function_source("_validate_optional_http_integration")
        self.assertIn("if not enabled:", helper)
        self.assertIn("endpoint is not None or api_key is not None", helper)
        self.assertIn("require the HTTP integration", helper)

        validator = _function_source("validate_llm_provider_guards")
        self.assertIn("enabled=normalized_access_control_adapter == \"external_http\"", validator)
        self.assertIn('endpoint_key="SUI_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT"', validator)
        self.assertIn('api_key_key="SUI_ACCESS_CONTROL_EXTERNAL_HTTP_STATIC_BEARER_TOKEN"', validator)

        registry_validation = REGISTRY_PATH.read_text(encoding="utf-8").split(
            "## Validation rules", 1
        )[1].split("## Operating rule", 1)[0]
        self.assertIn("HTTP連携を無効にしたままendpoint/API keyを残すこと", registry_validation)

        config = CONFIG_PATH.read_text(encoding="utf-8")
        section = config.split("## アクセス制御を使う", 1)[1].split(
            "### 文書policy binding resolver", 1
        )[0]
        self.assertIn("adapterを明示的に`noop`へ戻し", section)
        self.assertIn("endpointと固定bearerも同時に未設定へ戻して", section)
        self.assertIn("`noop`のままendpointまたは固定bearerだけを残す構成は起動時に拒否", section)


    def test_idp_issuer_requires_external_http_adapter_and_endpoint(self) -> None:
        validator = _function_source("validate_llm_provider_guards")
        self.assertIn("self.access_control_external_http_idp_issuer is not None", validator)
        self.assertIn('normalized_access_control_adapter != "external_http"', validator)
        self.assertIn("self.access_control_external_http_endpoint is None", validator)
        self.assertIn("SUI_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER requires", validator)
        self.assertIn("SUI_ACCESS_CONTROL_ADAPTER=external_http and its endpoint", validator)

        for path in (REGISTRY_PATH, CONFIG_PATH):
            prefix = "| `SUI_ACCESS_CONTROL_EXTERNAL_HTTP_IDP_ISSUER` |"
            rows = [
                line
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.startswith(prefix)
            ]
            self.assertEqual(len(rows), 1)
            self.assertIn("SUI_ACCESS_CONTROL_ADAPTER=external_http", rows[0])
            self.assertIn("endpoint", rows[0])

        section = CONFIG_PATH.read_text(encoding="utf-8").split(
            "## アクセス制御を使う", 1
        )[1].split("### 文書policy binding resolver", 1)[0]
        self.assertIn("IdP issuerを設定する場合も`external_http` adapterとendpointが必要", section)
        self.assertIn("どちらかを欠く構成は起動時に拒否", section)


if __name__ == "__main__":
    unittest.main()
