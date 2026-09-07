from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ACCESS_CONTROL = ROOT / "03_Implement/backend/src/kj_atlas_api/access_control.py"
REGISTRY = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIGURATION = ROOT / "04_Documentation/configuration.md"


def _function_source(path: Path, name: str) -> str:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    lines = text.splitlines()
    node = next(
        item
        for item in ast.walk(tree)
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    return "\n".join(lines[node.lineno - 1 : node.end_lineno])


def _row(text: str, key: str) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in text.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one row for {key}, got {len(rows)}")
    return rows[0]


def _registry_backend_row(text: str, key: str) -> str:
    backend = text.split("## Backend settings", 1)[1]
    return _row(backend, key)


class AccessControlFailSafeEffectScopeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry = REGISTRY.read_text(encoding="utf-8")
        self.configuration = CONFIGURATION.read_text(encoding="utf-8")

    def _public_rows(self) -> tuple[str, str]:
        key = "KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE"
        return (
            _registry_backend_row(self.registry, key),
            _row(self.configuration, key),
        )

    def test_local_missing_policy_ref_uses_fail_safe_mode_only_for_org_restricted(self) -> None:
        source = _function_source(ACCESS_CONTROL, "apply_local_failsafe")
        self.assertIn('visibility not in {"Org", "Restricted"}', source)
        self.assertIn("if request.resource.policy_ref:", source)
        self.assertIn('if mode == "deny":', source)
        self.assertIn('reason="policy_ref_missing"', source)
        self.assertIn('_read_only_fallback("policy_ref_missing", action=request.action)', source)

    def test_adapter_failure_paths_delegate_to_same_fail_safe_mode(self) -> None:
        source = _function_source(ACCESS_CONTROL, "resolve_access_decision")
        for exception_name in (
            "AccessControlUnreachableError",
            "AccessControlInvalidPolicyError",
            "AccessControlInvalidRequestError",
        ):
            self.assertIn(f"except {exception_name}", source)
        self.assertGreaterEqual(source.count("apply_adapter_failsafe("), 4)

    def test_read_only_fallback_allows_only_read(self) -> None:
        source = _function_source(ACCESS_CONTROL, "_read_only_fallback")
        self.assertIn('if action == "read":', source)
        self.assertIn("AccessDecision(allow=True, read_only=True", source)
        self.assertIn("AccessDecision(allow=False, read_only=True", source)

    def test_public_rows_name_missing_policy_and_action_effects(self) -> None:
        for row in self._public_rows():
            self.assertIn("Org/Restricted", row)
            self.assertIn("policyRef", row)
            self.assertIn("adapter", row)
            self.assertIn("read", row)
            self.assertIn("write", row)
            self.assertIn("export", row)
            self.assertIn("share", row)
            self.assertIn("deny", row)
            self.assertIn("read_only", row)


if __name__ == "__main__":
    unittest.main()
