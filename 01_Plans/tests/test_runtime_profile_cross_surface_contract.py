from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"
FRONTEND_RUNTIME_PATH = ROOT / "03_Implement/frontend/src/session/runtime_activation.ts"
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
CONFIG_PATH = ROOT / "04_Documentation/configuration.md"


def _backend_profiles() -> set[str]:
    tree = ast.parse(SETTINGS_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "supported_runtime_profiles"
            for target in node.targets
        ):
            continue
        value = ast.literal_eval(node.value)
        if isinstance(value, set) and all(isinstance(item, str) for item in value):
            return value
    raise AssertionError("backend supported_runtime_profiles literal set is missing")


def _frontend_profiles() -> set[str]:
    text = FRONTEND_RUNTIME_PATH.read_text(encoding="utf-8")
    try:
        body = text.split("export function resolveRuntimeEntryMode", 1)[1].split(
            "function isAbortFailure", 1
        )[0]
    except IndexError as exc:
        raise AssertionError("frontend resolveRuntimeEntryMode function is missing") from exc
    return set(re.findall(r'runtimeProfile === "([^"]+)"', body))


def _section(text: str, start: str, end: str) -> str:
    try:
        return text.split(start, 1)[1].split(end, 1)[0]
    except IndexError as exc:
        raise AssertionError(f"section boundary is missing: {start} -> {end}") from exc


def _purpose(section: str, key: str, purpose_index: int) -> str:
    prefix = f"| `{key}` |"
    rows = [line for line in section.splitlines() if line.startswith(prefix)]
    if len(rows) != 1:
        raise AssertionError(f"expected one {key} row, got {len(rows)}")
    cells = [cell.strip() for cell in rows[0].strip().strip("|").split("|")]
    if len(cells) <= purpose_index:
        raise AssertionError(f"malformed {key} row")
    return cells[purpose_index]


def _code_tokens(text: str) -> set[str]:
    return set(re.findall(r"`([^`]+)`", text))


def _explicit_profile_clause(purpose: str, expected: set[str]) -> set[str]:
    candidates = [
        _code_tokens(sentence)
        for sentence in purpose.split("。")
        if expected.issubset(_code_tokens(sentence))
    ]
    if len(candidates) != 1:
        raise AssertionError(
            f"expected one explicit runtime-profile clause for {sorted(expected)} in: {purpose}"
        )
    return candidates[0]


class RuntimeProfileCrossSurfaceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.backend = _backend_profiles()
        cls.frontend = _frontend_profiles()
        registry = REGISTRY_PATH.read_text(encoding="utf-8")
        configuration = CONFIG_PATH.read_text(encoding="utf-8")
        cls.registry_backend = _section(
            registry,
            "## Backend settings",
            "## Compose and frontend build keys",
        )
        cls.registry_compose = _section(
            registry,
            "## Compose and frontend build keys",
            "## Private adapter boundary",
        )
        cls.configuration_backend = _section(
            configuration,
            "## Backend 環境変数",
            "## Compose / frontend build 環境変数",
        )

    def test_backend_and_frontend_accept_the_same_named_profiles(self) -> None:
        self.assertEqual(self.frontend, self.backend)

    def test_backend_public_tables_name_the_same_profile_set(self) -> None:
        config_values = _explicit_profile_clause(
            _purpose(self.configuration_backend, "KJ_ATLAS_RUNTIME_PROFILE", 2),
            self.backend,
        )
        registry_values = _explicit_profile_clause(
            _purpose(self.registry_backend, "KJ_ATLAS_RUNTIME_PROFILE", 2),
            self.backend,
        )
        self.assertEqual(config_values, self.backend)
        self.assertEqual(registry_values, self.backend)

    def test_frontend_registry_row_describes_saas_as_active_tenant_session_profile(self) -> None:
        purpose = _purpose(self.registry_compose, "KJ_ATLAS_RUNTIME_PROFILE", 2)
        self.assertEqual(_explicit_profile_clause(purpose, self.backend), self.backend)
        self.assertNotIn("予約中", purpose)
        self.assertIn("tenant session必須", purpose)


if __name__ == "__main__":
    unittest.main()
