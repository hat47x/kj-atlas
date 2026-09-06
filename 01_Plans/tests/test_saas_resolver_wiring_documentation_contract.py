from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"
MAIN_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/main.py"
RUNTIME_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"


def _backend_registry_row(key: str) -> str:
    text = REGISTRY_PATH.read_text(encoding="utf-8")
    section = text.split("## Backend settings", 1)[1].split(
        "## Compose and frontend build keys", 1
    )[0]
    prefix = f"| `{key}` |"
    row = next((line for line in section.splitlines() if line.startswith(prefix)), None)
    if row is None:
        raise AssertionError(f"runtime registry row is missing: {key}")
    return row


def _configuration_row(key: str) -> str:
    text = CONFIG_PATH.read_text(encoding="utf-8")
    section = text.split("## Backend 環境変数", 1)[1].split(
        "## Compose / frontend build 環境変数", 1
    )[0]
    prefix = f"| `{key}` |"
    row = next((line for line in section.splitlines() if line.startswith(prefix)), None)
    if row is None:
        raise AssertionError(f"configuration row is missing: {key}")
    return row


def _section(path: Path, start: str, end: str) -> str:
    text = path.read_text(encoding="utf-8")
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except IndexError as exc:
        raise AssertionError(f"documentation section is missing: {start} -> {end} in {path}") from exc


def _function_source(path: Path, function_name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    node = next(
        (
            item
            for item in tree.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name == function_name
        ),
        None,
    )
    if node is None or node.end_lineno is None:
        raise AssertionError(f"function is missing: {function_name} in {path}")
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


class SaasResolverWiringDocumentationContractTests(unittest.TestCase):
    def test_main_builds_both_resolvers_into_trusted_saas_components(self) -> None:
        source = _function_source(MAIN_PATH, "_trusted_saas_runtime_components")
        self.assertIn("tenant_capability_resolver=build_tenant_capability_resolver()", source)
        self.assertIn(
            "document_policy_binding_resolver=build_document_policy_binding_resolver()",
            source,
        )

    def test_saas_preflight_requires_external_resolver_components(self) -> None:
        source = RUNTIME_PATH.read_text(encoding="utf-8")
        self.assertIn("ExternalHttpTenantCapabilityResolver", source)
        self.assertIn("ExternalHttpDocumentPolicyBindingResolver", source)
        self.assertIn('"external tenant capability component"', source)
        self.assertIn('"external document binding component"', source)

    def test_document_policy_binding_is_wired_into_server_owned_resource_resolution(self) -> None:
        source = _function_source(RUNTIME_PATH, "initialize_trusted_saas_runtime")
        self.assertIn("ServerOwnedDocumentResourceResolver", source)
        self.assertIn(
            "policy_binding_resolver=runtime_components.document_policy_binding_resolver",
            source,
        )

    def test_tenant_capability_resolver_is_exposed_by_main_lifespan(self) -> None:
        source = _function_source(MAIN_PATH, "lifespan")
        self.assertIn(
            "app.state.tenant_capability_resolver = runtime_components.tenant_capability_resolver",
            source,
        )

    def test_public_docs_do_not_claim_resolvers_are_unwired(self) -> None:
        for row in (
            _backend_registry_row("KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER"),
            _backend_registry_row("KJ_ATLAS_TENANT_CAPABILITY_RESOLVER"),
            _configuration_row("KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER"),
            _configuration_row("KJ_ATLAS_TENANT_CAPABILITY_RESOLVER"),
        ):
            self.assertNotIn("SaaS runtime未配線", row)
            self.assertNotIn("auth edge未配線", row)
            self.assertIn("saas-multitenant", row)
            self.assertIn("external_http", row)

    def test_current_state_prose_does_not_reintroduce_reserved_or_unwired_saas_status(self) -> None:
        main_source = MAIN_PATH.read_text(encoding="utf-8")
        self.assertIn("JwtSaasIdentityContextResolver", main_source)
        self.assertIn("install_trusted_saas_runtime(", main_source)

        current_state_sections = (
            _section(
                REGISTRY_PATH,
                "## Profile selection criteria（運用判断基準）",
                "### Drift check gates（設定ドリフト防止ゲート）",
            ),
            _section(
                CONFIG_PATH,
                "### 文書policy binding resolver",
                "## 設定後の確認",
            ),
        )
        stale_phrases = (
            "現行releaseで選択不可",
            "予約名に留める",
            "予約profile拒否",
            "起動拒否を解除する",
            "将来SaaS用",
            "まだ配線されていません",
            "trusted SaaS identity resolverが未接続",
        )
        for section in current_state_sections:
            for phrase in stale_phrases:
                self.assertNotIn(phrase, section)
            self.assertIn("saas-multitenant", section)


if __name__ == "__main__":
    unittest.main()
