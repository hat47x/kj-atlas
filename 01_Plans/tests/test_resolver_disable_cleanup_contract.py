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
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        and item.name == name
    )
    if node.end_lineno is None:
        raise AssertionError(f"source range unavailable for {name}")
    return "\n".join(text.splitlines()[node.lineno - 1 : node.end_lineno])


class ResolverDisableCleanupContractTests(unittest.TestCase):
    def test_none_rejects_leftover_http_settings_and_is_publicly_documented(self) -> None:
        helper = _function_source("_validate_trusted_http_resolver")
        self.assertIn('normalized_resolver == "none"', helper)
        self.assertIn('endpoint is not None or api_key is not None', helper)
        self.assertIn('require {resolver_key}=external_http', helper)

        validator = _function_source("validate_llm_provider_guards")
        for resolver_key in (
            "SUI_DOCUMENT_POLICY_BINDING_RESOLVER",
            "SUI_TENANT_CAPABILITY_RESOLVER",
        ):
            self.assertIn(f'resolver_key="{resolver_key}"', validator)

        registry_validation = REGISTRY_PATH.read_text(encoding="utf-8").split(
            "## Validation rules", 1
        )[1].split("## Operating rule", 1)[0]
        self.assertIn('`none`でHTTP設定だけを残すことも拒否', registry_validation)
        self.assertIn(
            '`SUI_TENANT_CAPABILITY_RESOLVER`も同じtrusted HTTP接続制約',
            registry_validation,
        )

        config = CONFIG_PATH.read_text(encoding="utf-8")
        binding = config.split("### 文書policy binding resolver", 1)[1].split(
            "### Tenant capability resolver", 1
        )[0]
        tenant = config.split("### Tenant capability resolver", 1)[1].split(
            "## 設定後の確認", 1
        )[0]
        for section in (binding, tenant):
            self.assertIn('resolverを`none`へ戻す場合', section)
            self.assertIn('endpoint/API key', section)
            self.assertIn('起動時に拒否', section)


if __name__ == "__main__":
    unittest.main()
