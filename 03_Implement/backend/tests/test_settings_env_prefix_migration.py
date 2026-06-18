from __future__ import annotations

import ast
import os
import re
from pathlib import Path

from kj_atlas_api.settings import LEGACY_ENV_KEYS, Settings


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_REGISTRY_DOC = REPO_ROOT / "02_Architecture" / "runtime_parameter_registry.md"
PUBLIC_CONFIGURATION_DOC = REPO_ROOT / "04_Documentation" / "configuration.md"
PUBLIC_ENV_CONTRACT_DOCS = [RUNTIME_REGISTRY_DOC, PUBLIC_CONFIGURATION_DOC]
ENV_SCAN_ROOTS = [
    REPO_ROOT / "03_Implement" / "backend",
    REPO_ROOT / "03_Implement" / "frontend" / "src",
    REPO_ROOT / "03_Implement" / "frontend" / "scripts",
    REPO_ROOT / "03_Implement" / "frontend" / "vite.config.ts",
]
IGNORED_SCAN_PARTS = {".venv", "__pycache__", ".pytest_cache", "node_modules", "dist"}
ALLOWED_NON_PROJECT_ENV_KEYS = {"DEV", "PYTHONPATH"}
ENV_KEY_PATTERN = re.compile(r"KJ_ATLAS_[A-Z0-9_]+")
ENV_WILDCARD_PATTERN = re.compile(r"`KJ_ATLAS_[A-Z0-9]+[A-Z0-9_]*\*`")
LEGACY_FRONTEND_ENV_KEYS = {"VITE_API_BASE", "FRONTEND_API_BASE"}


def _unset_related_envs() -> None:
    for key in list(os.environ):
        if key.startswith("KJ_ATLAS_") or key in LEGACY_ENV_KEYS:
            os.environ.pop(key, None)


def _iter_scan_files() -> list[Path]:
    files: list[Path] = []
    for root in ENV_SCAN_ROOTS:
        if root.is_file():
            files.append(root)
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".py", ".sh", ".ts", ".tsx", ".js", ".mjs"}:
                if not any(part in IGNORED_SCAN_PARTS for part in path.parts):
                    files.append(path)
    return files


def _python_env_reads(path: Path) -> list[tuple[int, str]]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    constants: dict[str, str] = {}
    env_names: list[tuple[int, str]] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                constants[target.id] = node.value.value

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            is_getenv = (
                isinstance(func, ast.Attribute)
                and func.attr == "getenv"
                and isinstance(func.value, ast.Name)
                and func.value.id == "os"
            )
            if is_getenv and node.args:
                arg = node.args[0]
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    env_names.append((node.lineno, arg.value))
                elif isinstance(arg, ast.Name) and arg.id in constants:
                    env_names.append((node.lineno, constants[arg.id]))

        if isinstance(node, ast.Subscript):
            value = node.value
            is_os_environ = (
                isinstance(value, ast.Attribute)
                and value.attr == "environ"
                and isinstance(value.value, ast.Name)
                and value.value.id == "os"
            )
            if is_os_environ and isinstance(node.slice, ast.Constant) and isinstance(node.slice.value, str):
                env_names.append((node.lineno, node.slice.value))

    return env_names


def _text_env_reads(path: Path) -> list[tuple[int, str]]:
    text = path.read_text(encoding="utf-8")
    env_names: list[tuple[int, str]] = []

    for pattern in [
        re.compile(r"(?:process|import\.meta)\.env\.([A-Za-z_][A-Za-z0-9_]*)"),
        re.compile(r"^\s*export\s+([A-Z][A-Z0-9_]*)=", re.MULTILINE),
    ]:
        for match in pattern.finditer(text):
            env_names.append((text[: match.start()].count("\n") + 1, match.group(1)))

    return env_names


def _is_allowed_project_env_name(name: str) -> bool:
    return name.startswith("KJ_ATLAS_") or name in ALLOWED_NON_PROJECT_ENV_KEYS


def _env_keys(text: str) -> set[str]:
    return set(ENV_KEY_PATTERN.findall(text))


def _public_registry_env_keys() -> set[str]:
    text = RUNTIME_REGISTRY_DOC.read_text(encoding="utf-8")
    public_text = text.split("以下は製品ランタイムの公開設定ではなく", maxsplit=1)[0]
    return _env_keys(public_text)


def test_settings_uses_prefixed_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")

    loaded = Settings()

    assert loaded.database_url == "sqlite:///./canonical.db"


def test_project_env_access_points_use_kj_atlas_prefix() -> None:
    violations: list[str] = []

    for path in _iter_scan_files():
        relative_path = path.relative_to(REPO_ROOT)
        env_reads = _python_env_reads(path) if path.suffix == ".py" else _text_env_reads(path)
        for line_number, name in env_reads:
            if not _is_allowed_project_env_name(name):
                violations.append(f"{relative_path}:{line_number}:{name}")

    assert violations == []


def test_public_configuration_doc_lists_exact_public_runtime_keys() -> None:
    configuration_text = PUBLIC_CONFIGURATION_DOC.read_text(encoding="utf-8")

    assert ENV_WILDCARD_PATTERN.findall(configuration_text) == []
    assert _env_keys(configuration_text) == _public_registry_env_keys()


def test_public_env_contract_docs_do_not_advertise_legacy_frontend_keys() -> None:
    violations: list[str] = []

    for path in PUBLIC_ENV_CONTRACT_DOCS:
        text = path.read_text(encoding="utf-8")
        for key in sorted(LEGACY_FRONTEND_ENV_KEYS):
            legacy_key_pattern = re.compile(rf"(?<!KJ_ATLAS_)\b{re.escape(key)}\b")
            if legacy_key_pattern.search(text):
                violations.append(f"{path.relative_to(REPO_ROOT)}:{key}")

    assert violations == []


def test_settings_rejects_legacy_key_only(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    try:
        Settings()
        assert False, "Expected legacy-only env to be rejected"
    except ValueError as exc:
        assert "Legacy env keys are no longer supported" in str(exc)
        assert "DATABASE_URL" in str(exc)


def test_settings_rejects_mixed_prefixed_and_legacy_keys(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_DATABASE_URL", "sqlite:///./canonical.db")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./legacy.db")

    try:
        Settings()
        assert False, "Expected mixed env keys to be rejected"
    except ValueError as exc:
        assert "Legacy env keys are no longer supported" in str(exc)
        assert "DATABASE_URL" in str(exc)


def test_settings_normalizes_access_control_auth_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_AUTH_MODE", "  OIDC ")

    loaded = Settings()

    assert loaded.access_control_external_http_auth_mode == "oidc"


def test_settings_normalizes_access_control_adapter_and_fail_safe(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_ADAPTER", "  MOCK ")
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE", "  DENY ")

    loaded = Settings()

    assert loaded.access_control_adapter == "mock"
    assert loaded.access_control_fail_safe_mode == "deny"


def test_settings_rejects_invalid_access_control_adapter(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_ADAPTER", "custom")

    try:
        Settings()
        assert False, "Expected invalid access-control adapter to be rejected"
    except ValueError as exc:
        assert "KJ_ATLAS_ACCESS_CONTROL_ADAPTER" in str(exc)


def test_settings_rejects_invalid_access_control_fail_safe(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE", "allow")

    try:
        Settings()
        assert False, "Expected invalid access-control fail-safe mode to be rejected"
    except ValueError as exc:
        assert "KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE" in str(exc)


def test_settings_normalizes_reviewer_ref_resolver_adapter(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_REVIEWER_REF_RESOLVER_ADAPTER", "  SSO_SUBJECT ")

    loaded = Settings()

    assert loaded.reviewer_ref_resolver_adapter == "sso_subject"


def test_settings_rejects_non_ce4_equivalence_mode(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_CE4_EQUIVALENCE_MODE", "bundle_hash_only")

    try:
        Settings()
        assert False, "Expected invalid CE4 equivalence mode to be rejected"
    except ValueError as exc:
        assert "KJ_ATLAS_CE4_EQUIVALENCE_MODE" in str(exc)


def test_settings_rejects_disabling_ce4_audit_require_all_events(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS", "false")

    try:
        Settings()
        assert False, "Expected CE4 audit fail-closed guard to be rejected"
    except ValueError as exc:
        assert "KJ_ATLAS_CE4_AUDIT_REQUIRE_ALL_EVENTS" in str(exc)


def test_settings_exposes_ce4_stub_unresolved_contracts(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("KJ_ATLAS_CE4_STUB_UNRESOLVED_CONTRACTS", "false")

    loaded = Settings()

    assert loaded.ce4_stub_unresolved_contracts is False


def test_settings_rejects_legacy_ce4_stub_key(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    _unset_related_envs()
    monkeypatch.setenv("CE4_STUB_UNRESOLVED_CONTRACTS", "false")

    try:
        Settings()
        assert False, "Expected legacy CE4 stub key to be rejected"
    except ValueError as exc:
        assert "CE4_STUB_UNRESOLVED_CONTRACTS" in str(exc)
