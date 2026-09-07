from __future__ import annotations

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
                self.assertIn(concrete_type, self.trusted_saas_runtime)

    def test_all_three_concrete_types_are_required_by_the_same_saas_preflight_bundle(self) -> None:
        self.assertIn("def validate_for_saas(self) -> None:", self.trusted_saas_runtime)
        for concrete_type in KEYS_AND_TYPES.values():
            self.assertIn(concrete_type, self.trusted_saas_runtime)
        self.assertIn("runtime_components.validate_for_saas()", self.trusted_saas_runtime)


if __name__ == "__main__":
    unittest.main()
