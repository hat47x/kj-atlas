from __future__ import annotations

import ast
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "02_Architecture/runtime_parameter_registry.md"
SETTINGS_PATH = ROOT / "03_Implement/backend/src/kj_atlas_api/settings.py"


def _normalize_documented_default(raw: str) -> object:
    value = raw.strip().strip("`").strip()
    if value in {"未設定（空文字）", "（空）"}:
        return ""
    if "（" in value:
        value = value.split("（", 1)[0].strip()
    if value == "未設定":
        return None
    lowered = value.lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    numeric = value.replace(",", "").replace("_", "")
    if re.fullmatch(r"-?\d+", numeric):
        return int(numeric)
    if re.fullmatch(r"-?\d+\.\d+", numeric):
        return float(numeric)
    return value


def _backend_registry_defaults(registry_text: str) -> tuple[dict[str, object], list[str]]:
    marker = "## Backend settings"
    end_marker = "## Compose and frontend build keys"
    if marker not in registry_text or end_marker not in registry_text:
        raise AssertionError("runtime parameter registry backend settings table is missing")
    section = registry_text.split(marker, 1)[1].split(end_marker, 1)[0]
    defaults: dict[str, object] = {}
    duplicates: list[str] = []
    for line in section.splitlines():
        if not line.lstrip().startswith("| `KJ_ATLAS_"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].strip("`")
        if key in defaults:
            duplicates.append(key)
            continue
        defaults[key] = _normalize_documented_default(cells[1])
    return defaults, duplicates


def _settings_static_defaults(settings_text: str) -> dict[str, object]:
    tree = ast.parse(settings_text)
    settings_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"),
        None,
    )
    if settings_class is None:
        raise AssertionError("Settings class is missing")

    defaults: dict[str, object] = {}
    for statement in settings_class.body:
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        func_name = call.func.id if isinstance(call.func, ast.Name) else None
        if func_name != "Field":
            continue
        alias_keyword = next(
            (keyword for keyword in call.keywords if keyword.arg == "validation_alias"),
            None,
        )
        default_keyword = next((keyword for keyword in call.keywords if keyword.arg == "default"), None)
        if alias_keyword is None or default_keyword is None:
            continue
        try:
            alias = ast.literal_eval(alias_keyword.value)
            default = ast.literal_eval(default_keyword.value)
        except (ValueError, TypeError):
            # Arithmetic expressions and default_factory-like computed values stay outside this static gate.
            continue
        if isinstance(alias, str) and alias.startswith("KJ_ATLAS_"):
            defaults[alias] = default
    return defaults


class RuntimeParameterBackendRegistryContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry_defaults, cls.duplicates = _backend_registry_defaults(
            REGISTRY_PATH.read_text(encoding="utf-8")
        )
        cls.settings_defaults = _settings_static_defaults(SETTINGS_PATH.read_text(encoding="utf-8"))

    def test_backend_settings_keys_are_unique_inside_the_ssot_table(self) -> None:
        self.assertEqual(
            self.duplicates,
            [],
            f"duplicate backend runtime keys in registry: {sorted(set(self.duplicates))}",
        )

    def test_static_settings_defaults_match_backend_settings_default_column(self) -> None:
        mismatches = {
            key: (self.registry_defaults[key], implementation_default)
            for key, implementation_default in self.settings_defaults.items()
            if key in self.registry_defaults and self.registry_defaults[key] != implementation_default
        }
        self.assertEqual(mismatches, {}, f"backend registry default drift: {mismatches}")

    def test_regression_keys_are_covered_by_the_backend_table(self) -> None:
        # These keys exposed the gap after the narrower Profile-default guard landed.
        for key in {
            "KJ_ATLAS_APP_REVISION",
            "KJ_ATLAS_MAX_DOCUMENT_CARDS",
            "KJ_ATLAS_LLM_TASK_MODEL_MAP",
            "KJ_ATLAS_TRUSTED_PROXIES",
        }:
            self.assertIn(key, self.registry_defaults)
            self.assertIn(key, self.settings_defaults)


if __name__ == "__main__":
    unittest.main()
