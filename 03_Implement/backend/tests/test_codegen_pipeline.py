"""Code generation pipeline tests (DX-CODEGEN-01, L3 autonomy foundation).

Verifies generate_from_design_decision.py:
1. ai_task type generates Pydantic models, route handler, client function
2. ui_component type generates React component with PascalCase preservation
3. data_boundary type generates Pydantic model with PascalCase preservation
4. Three-element verification is enforced for ALL types (reject unverified)
5. Unsupported types are rejected with a clear message

These tests use --dry-run (no files written) and are the foundation for
measuring the codegen success rate required by L3 autonomy criterion ①.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent / "scripts" / "generate_from_design_decision.py"


def _run_script(decision: dict, *extra_args: str) -> subprocess.CompletedProcess:
    """Run the codegen script with the given decision as a temp JSON file."""
    import tempfile

    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(decision, f, ensure_ascii=False)
        path = f.name
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), path, *extra_args],
            capture_output=True, text=True,
        )
    finally:
        Path(path).unlink(missing_ok=True)
    return result


def _verified(design: dict) -> dict:
    return {
        "designDecision": design,
        "threeElementVerification": {
            "business": "テスト用の業務設計",
            "data": "テスト用のデータ設計",
            "function": "テスト用の機能設計",
        },
    }


def _verified_ai_task() -> dict:
    return _verified({
        "type": "ai_task",
        "taskName": "test_task",
        "humanReadableName": "テストタスク",
        "requestFields": [{"name": "input", "type": "str"}],
        "responseFields": [{"name": "output", "type": "str"}],
    })


def _verified_ui_component() -> dict:
    return _verified({
        "type": "ui_component",
        "componentName": "TestComponent",
        "props": [{"name": "value", "type": "string"}],
        "i18nKeys": ["test_component.title"],
        "testIds": ["test-component"],
    })


def _verified_data_boundary() -> dict:
    return _verified({
        "type": "data_boundary",
        "typeName": "TestBoundary",
        "description": "テスト境界",
        "saveScope": "server",
        "fields": [{"name": "field", "type": "str"}],
    })


def test_ai_task_generates_all_sections() -> None:
    result = _run_script(_verified_ai_task(), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Generated Pydantic models" in result.stdout
    assert "Generated route handler" in result.stdout
    assert "Generated client function" in result.stdout
    assert "TestTaskRequest" in result.stdout


def test_ai_task_unverified_is_rejected() -> None:
    decision = {"designDecision": _verified_ai_task()["designDecision"]}  # no verification
    result = _run_script(decision, "--dry-run")
    assert result.returncode == 1
    assert "three-element" in result.stdout.lower() or "三要素" in result.stdout


def test_ui_component_preserves_pascal_case() -> None:
    result = _run_script(_verified_ui_component(), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Generating UI component: TestComponent" in result.stdout
    assert "TestComponentProps" in result.stdout
    assert "test-component" in result.stdout  # data-testid


def test_ui_component_requires_verification() -> None:
    decision = {"designDecision": _verified_ui_component()["designDecision"]}
    result = _run_script(decision, "--dry-run")
    assert result.returncode == 1
    assert "three-element" in result.stdout.lower() or "三要素" in result.stdout


def test_data_boundary_generates_model() -> None:
    result = _run_script(_verified_data_boundary(), "--dry-run")
    assert result.returncode == 0, result.stderr
    assert "Generating data boundary type: TestBoundary" in result.stdout
    assert "class TestBoundary(BaseModel)" in result.stdout
    assert "field: str" in result.stdout


def test_data_boundary_requires_verification() -> None:
    decision = {"designDecision": _verified_data_boundary()["designDecision"]}
    result = _run_script(decision, "--dry-run")
    assert result.returncode == 1
    assert "three-element" in result.stdout.lower() or "三要素" in result.stdout


def test_unsupported_type_rejected() -> None:
    decision = _verified({
        "type": "unknown_type",
        "name": "Whatever",
    })
    result = _run_script(decision, "--dry-run")
    assert result.returncode == 1
    assert "unsupported" in result.stdout.lower()


def test_check_only_mode() -> None:
    result = _run_script(_verified_ai_task(), "--check-only")
    assert result.returncode == 0
    assert "Three-element verification passed" in result.stdout
