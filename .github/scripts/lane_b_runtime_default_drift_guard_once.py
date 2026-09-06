from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKS = ROOT / "01_Plans/docs_contract_checks.py"
TEST = ROOT / "01_Plans/tests/test_runtime_parameter_default_contract.py"

HELPERS = r'''

def _normalize_documented_runtime_default(raw: str) -> object:
    value = raw.strip().strip("`").strip()
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


def _extract_profile_implementation_defaults(registry_text: str) -> dict[str, tuple[object, int]]:
    marker = "### Profile default vs recommendation"
    if marker not in registry_text:
        return {}
    prefix, remainder = registry_text.split(marker, 1)
    section = remainder.split("\n## ", 1)[0]
    first_line = prefix.count("\n") + 1
    defaults: dict[str, tuple[object, int]] = {}
    for offset, line in enumerate(section.splitlines(), start=1):
        if not line.lstrip().startswith("| `KJ_ATLAS_"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        key = cells[0].strip("`")
        defaults[key] = (_normalize_documented_runtime_default(cells[1]), first_line + offset)
    return defaults


def _extract_settings_literal_defaults(settings_text: str) -> dict[str, object]:
    tree = ast.parse(settings_text)
    settings_class = next(
        (node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "Settings"),
        None,
    )
    if settings_class is None:
        return {}
    defaults: dict[str, object] = {}
    for statement in settings_class.body:
        if not isinstance(statement, ast.AnnAssign) or not isinstance(statement.target, ast.Name):
            continue
        value = statement.value
        default_node: ast.AST | None = None
        if isinstance(value, ast.Call):
            func_name = value.func.id if isinstance(value.func, ast.Name) else None
            if func_name != "Field":
                continue
            default_keyword = next((keyword for keyword in value.keywords if keyword.arg == "default"), None)
            if default_keyword is None:
                continue
            default_node = default_keyword.value
        elif value is not None:
            default_node = value
        if default_node is None:
            continue
        try:
            defaults[statement.target.id] = ast.literal_eval(default_node)
        except (ValueError, TypeError):
            # computed/default_factory values are intentionally outside this static gate
            continue
    return defaults


def check_runtime_parameter_default_values(
    root: Path,
    registry_path: Path = RUNTIME_PARAMETER_REGISTRY_PATH,
    settings_path: Path = Path("03_Implement/backend/src/kj_atlas_api/settings.py"),
) -> list[DocsCheckFinding]:
    """Reject static Settings defaults that drift from the registry's implementation-default table."""
    repository_root = root.resolve()
    registry_file = repository_root / registry_path
    settings_file = repository_root / settings_path
    if not registry_file.exists() or not settings_file.exists():
        return []

    documented = _extract_profile_implementation_defaults(registry_file.read_text(encoding="utf-8"))
    implemented = _extract_settings_literal_defaults(settings_file.read_text(encoding="utf-8"))
    findings: list[DocsCheckFinding] = []
    for key, (documented_default, line) in sorted(documented.items()):
        field_name = key.removeprefix("KJ_ATLAS_").lower()
        if field_name not in implemented:
            continue
        implementation_default = implemented[field_name]
        if implementation_default == documented_default:
            continue
        findings.append(
            DocsCheckFinding(
                rule_id=RUNTIME_PARAMETER_DEFAULT_RULE_ID,
                path=registry_path.as_posix(),
                line=line,
                target=key,
                message=(
                    f"documented implementation default {documented_default!r} does not match "
                    f"Settings.{field_name} default {implementation_default!r}"
                ),
            )
        )
    return findings
'''

TEST_CONTENT = r'''from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "docs_contract_checks.py"
SPEC = importlib.util.spec_from_file_location("docs_contract_checks", MODULE_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RuntimeParameterDefaultContractTests(unittest.TestCase):
    def _write_fixture(self, root: Path, registry_default: str = "50,000") -> None:
        registry = root / "02_Architecture/runtime_parameter_registry.md"
        registry.parent.mkdir(parents=True)
        registry.write_text(
            "# Runtime Parameter Registry\n\n"
            "### Profile default vs recommendation（既定値と推奨値）\n\n"
            "| Key | Implementation default | Enterprise recommendation | Rationale |\n"
            "| --- | --- | --- | --- |\n"
            f"| `KJ_ATLAS_MAX_DOCUMENT_CARDS` | `{registry_default}` | any | test |\n"
            "| `KJ_ATLAS_ADMIN_API_KEY` | 未設定 | required | test |\n"
            "| `KJ_ATLAS_LLM_PROVIDER` | `none` | none | test |\n",
            encoding="utf-8",
        )
        settings = root / "03_Implement/backend/src/kj_atlas_api/settings.py"
        settings.parent.mkdir(parents=True)
        settings.write_text(
            "class Settings:\n"
            "    max_document_cards: int = Field(default=50_000, ge=1)\n"
            "    admin_api_key: str | None = Field(default=None)\n"
            "    llm_provider: str = Field(default='none')\n"
            "    computed: int = Field(default_factory=lambda: 1)\n",
            encoding="utf-8",
        )

    def test_current_literal_defaults_match_after_numeric_normalization(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            self.assertEqual(MODULE.check_runtime_parameter_default_values(root), [])

    def test_registry_default_drift_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root, registry_default="10,000")
            findings = MODULE.check_runtime_parameter_default_values(root)
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.rule_id, MODULE.RUNTIME_PARAMETER_DEFAULT_RULE_ID)
        self.assertEqual(finding.target, "KJ_ATLAS_MAX_DOCUMENT_CARDS")
        self.assertIn("10000", finding.message)
        self.assertIn("50000", finding.message)

    def test_unset_and_none_string_remain_distinct_and_match_their_literals(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_fixture(root)
            documented = MODULE._extract_profile_implementation_defaults(
                (root / "02_Architecture/runtime_parameter_registry.md").read_text(encoding="utf-8")
            )
        self.assertIsNone(documented["KJ_ATLAS_ADMIN_API_KEY"][0])
        self.assertEqual(documented["KJ_ATLAS_LLM_PROVIDER"][0], "none")

    def test_computed_defaults_are_outside_static_contract(self) -> None:
        settings = "class Settings:\n    value: int = Field(default_factory=lambda: 1)\n"
        self.assertEqual(MODULE._extract_settings_literal_defaults(settings), {})


if __name__ == "__main__":
    unittest.main()
'''


def insert_before_function(source: str, function_name: str, payload: str) -> str:
    marker = f"def {function_name}("
    index = source.find(marker)
    if index < 0:
        raise SystemExit(f"missing function anchor: {function_name}")
    return source[:index] + payload + "\n" + source[index:]


def inject_before_final_return(source: str, function_name: str, statement: str) -> str:
    tree = ast.parse(source)
    function = next(
        node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function_name
    )
    returns = [
        node
        for node in ast.walk(function)
        if isinstance(node, ast.Return) and isinstance(node.value, ast.Name) and node.value.id == "findings"
    ]
    if not returns:
        raise SystemExit(f"missing findings return in {function_name}")
    target = max(returns, key=lambda node: node.lineno)
    lines = source.splitlines(keepends=True)
    indent = lines[target.lineno - 1][: len(lines[target.lineno - 1]) - len(lines[target.lineno - 1].lstrip())]
    lines.insert(target.lineno - 1, indent + statement + "\n")
    return "".join(lines)


source = CHECKS.read_text(encoding="utf-8")
if "import ast\n" not in source:
    source = source.replace("import argparse\n", "import argparse\nimport ast\n", 1)
if 'RUNTIME_PARAMETER_DEFAULT_RULE_ID = "DC-CFG-001"' not in source:
    source = source.replace(
        'NPM_SCRIPT_COMMAND_RULE_ID = "DC-CMD-001"\n',
        'NPM_SCRIPT_COMMAND_RULE_ID = "DC-CMD-001"\nRUNTIME_PARAMETER_DEFAULT_RULE_ID = "DC-CFG-001"\n',
        1,
    )
if "def check_runtime_parameter_default_values(" not in source:
    source = insert_before_function(source, "check_runtime_parameter_key_commands", HELPERS)
if "check_runtime_parameter_default_values(root, registry_path=registry_path)" not in source:
    source = inject_before_final_return(
        source,
        "check_runtime_parameter_key_commands",
        "findings.extend(check_runtime_parameter_default_values(root, registry_path=registry_path))",
    )
CHECKS.write_text(source, encoding="utf-8")
TEST.write_text(TEST_CONTENT, encoding="utf-8")
