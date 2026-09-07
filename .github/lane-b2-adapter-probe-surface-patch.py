from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
TEST = ROOT / "01_Plans/tests/test_runtime_adapter_probe_surface_contract.py"


def replace_once(path: Path, old: str, new: str) -> None:
    raw = path.read_bytes()
    old_b = old.encode("utf-8")
    new_b = new.encode("utf-8")
    count = raw.count(old_b)
    if count != 1:
        raise SystemExit(f"expected one match in {path}, got {count}")
    path.write_bytes(raw.replace(old_b, new_b, 1))


replacements = {
    "| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter。`noop`, `mock`, `external_http` | direct | 通常値 | 選択した adapter 名が起動ログに反映されることを確認する |":
    "| `KJ_ATLAS_ACCESS_CONTROL_ADAPTER` | `noop` | access control adapter。`noop`, `mock`, `external_http` | direct | 通常値 | adapter名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalPolicyAccessControlAdapter` の実型を要求し、`external_http` の個別配送はPDP test doubleへの到達で確認する |",
    "| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | server-owned binding IDを一時的なpolicyRefへ解決するresolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、`ServerOwnedDocumentResourceResolver` の policy binding resolver として配線 | direct | 通常値 | 選択した resolver 名が起動ログに反映されることを確認する |":
    "| `KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER` | `none` | server-owned binding IDを一時的なpolicyRefへ解決するresolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、`ServerOwnedDocumentResourceResolver` の policy binding resolver として配線 | direct | 通常値 | resolver名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalHttpDocumentPolicyBindingResolver` の実型を要求し、`external_http` の個別配送はbinding service test doubleへのlookup到達で確認する |",
    "| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenant-scoped effective capability resolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、runtimeの tenant capability resolver として配線 | direct | 通常値 | 選択した resolver 名が起動ログに反映されることを確認する |":
    "| `KJ_ATLAS_TENANT_CAPABILITY_RESOLVER` | `none` | tenant-scoped effective capability resolver。`none`, `external_http`。`saas-multitenant` では `external_http` が必須で、起動前にexternal componentを検査し、runtimeの tenant capability resolver として配線 | direct | 通常値 | resolver名のstartup self-reportはない。`saas-multitenant` では起動前preflightが `ExternalHttpTenantCapabilityResolver` の実型を要求し、`external_http` の個別配送はcapability service test doubleへのlookup到達で確認する |",
}
for old, new in replacements.items():
    replace_once(REGISTRY, old, new)

TEST.write_text(
    '''from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
TRUSTED_SAAS_RUNTIME = ROOT / "03_Implement/backend/src/kj_atlas_api/trusted_saas_runtime.py"

KEYS_AND_TYPES = {
    "KJ_ATLAS_ACCESS_CONTROL_ADAPTER": "ExternalPolicyAccessControlAdapter",
    "KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER": "ExternalHttpDocumentPolicyBindingResolver",
    "KJ_ATLAS_TENANT_CAPABILITY_RESOLVER": "ExternalHttpTenantCapabilityResolver",
}


def _backend_row(text: str, key: str) -> str:
    backend = text.split("## Backend settings", 1)[1]
    prefix = f"| `{key}` |"
    rows = [line for line in backend.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one backend row for {key}, got {len(rows)}")
    return rows[0]


class RuntimeAdapterProbeSurfaceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.trusted_saas_runtime = TRUSTED_SAAS_RUNTIME.read_text(encoding="utf-8")

    def test_registry_does_not_claim_nonexistent_startup_name_logging(self) -> None:
        for key in KEYS_AND_TYPES:
            row = _backend_row(self.registry, key)
            with self.subTest(key=key):
                self.assertNotIn("起動ログに反映", row)
                self.assertIn("startup self-reportはない", row)
                self.assertIn("起動前preflight", row)
                self.assertIn("test double", row)

    def test_saas_preflight_checks_the_actual_component_types_named_by_probes(self) -> None:
        for key, concrete_type in KEYS_AND_TYPES.items():
            row = _backend_row(self.registry, key)
            with self.subTest(key=key):
                self.assertIn(concrete_type, row)
                self.assertIn(f"isinstance(\n                    self.", self.trusted_saas_runtime)
                self.assertIn(concrete_type, self.trusted_saas_runtime)

    def test_all_three_concrete_types_are_required_by_the_same_saas_preflight_bundle(self) -> None:
        self.assertIn("def validate_for_saas(self) -> None:", self.trusted_saas_runtime)
        for concrete_type in KEYS_AND_TYPES.values():
            self.assertIn(concrete_type, self.trusted_saas_runtime)
        self.assertIn("runtime_components.validate_for_saas()", self.trusted_saas_runtime)


if __name__ == "__main__":
    unittest.main()
''',
    encoding="utf-8",
)
