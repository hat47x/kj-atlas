"""AI-IR-PROJECTION-01: keep every LLMRequest call site explicitly classified.

The route inventory drifted from 9 prompt builders at issue creation time to 11
by 2026-08-31. A hand-maintained count can therefore become stale while a new
AI path silently bypasses the LLM input IR. This test treats the current Stage 5
debt as explicit debt rather than as an invisible exception.

When a Stage 5 route is migrated, move its task from
EXPLICIT_STAGE5_DEBT_TASKS to IR_MIGRATED_TASKS in the same change. When a new
LLMRequest call is added, classify it deliberately. The test does not prove that
a prompt uses every IR field correctly; endpoint-specific integration tests keep
that responsibility.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
ROUTE_FILES = (
    BACKEND_ROOT / "src" / "kj_atlas_api" / "routes" / "ai.py",
    BACKEND_ROOT / "src" / "kj_atlas_api" / "routes" / "ai_relations.py",
)

IR_MIGRATED_TASKS = frozenset(
    {
        "detect_contradiction",
        "generate_narrative",
        "propose_opposing_viewpoint",
        "re_layout",
        "suggest_card_groups",
        "suggest_island_summary",
    }
)

EXPLICIT_STAGE5_DEBT_TASKS = frozenset(
    {
        "check_narrative",
        "refine_card_text",
        "suggest_document_title",
        "suggest_merges",
        "summarize_island_relation",
    }
)

EXPECTED_LLM_REQUEST_CALL_COUNT = 11


@dataclass(frozen=True)
class LLMRequestCall:
    path: Path
    line: int
    task: str | None
    has_inputs: bool

    @property
    def location(self) -> str:
        return f"{self.path.relative_to(BACKEND_ROOT)}:{self.line}"


def _call_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def _literal_task(call: ast.Call) -> str | None:
    for keyword in call.keywords:
        if keyword.arg != "task":
            continue
        value = keyword.value
        if isinstance(value, ast.Constant) and isinstance(value.value, str):
            return value.value
        return None
    return None


def _scan_llm_requests() -> list[LLMRequestCall]:
    calls: list[LLMRequestCall] = []
    for path in ROUTE_FILES:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or _call_name(node.func) != "LLMRequest":
                continue
            calls.append(
                LLMRequestCall(
                    path=path,
                    line=node.lineno,
                    task=_literal_task(node),
                    has_inputs=any(keyword.arg == "inputs" for keyword in node.keywords),
                )
            )
    return sorted(calls, key=lambda item: (str(item.path), item.line))


def _calls_by_task() -> dict[str, list[LLMRequestCall]]:
    rows: dict[str, list[LLMRequestCall]] = {}
    for call in _scan_llm_requests():
        if call.task is not None:
            rows.setdefault(call.task, []).append(call)
    return rows


def test_every_llm_request_call_site_is_explicitly_classified() -> None:
    calls = _scan_llm_requests()
    dynamic_tasks = [call.location for call in calls if call.task is None]
    assert not dynamic_tasks, (
        "LLMRequest task must be a string literal so IR coverage can be audited: "
        + ", ".join(dynamic_tasks)
    )

    assert len(calls) == EXPECTED_LLM_REQUEST_CALL_COUNT, (
        "LLMRequest call-site count changed. Review the new/removed call and update the "
        "explicit IR/debt classification instead of relying on a stale manual inventory."
    )

    discovered = {call.task for call in calls if call.task is not None}
    expected = IR_MIGRATED_TASKS | EXPLICIT_STAGE5_DEBT_TASKS
    assert discovered == expected, (
        "LLMRequest task inventory changed without an explicit IR/debt classification. "
        f"added={sorted(discovered - expected)}, removed={sorted(expected - discovered)}"
    )


def test_ir_migrated_tasks_always_attach_inputs() -> None:
    rows = _calls_by_task()
    violations = [
        call.location
        for task in sorted(IR_MIGRATED_TASKS)
        for call in rows.get(task, [])
        if not call.has_inputs
    ]
    assert not violations, (
        "An IR-migrated AI path dropped LLMRequest.inputs: " + ", ".join(violations)
    )


def test_stage5_debt_is_explicit_until_each_route_is_migrated() -> None:
    rows = _calls_by_task()
    prematurely_migrated = [
        f"{task}@{call.location}"
        for task in sorted(EXPLICIT_STAGE5_DEBT_TASKS)
        for call in rows.get(task, [])
        if call.has_inputs
    ]
    assert not prematurely_migrated, (
        "A Stage 5 debt route now carries IR inputs. Move the task to IR_MIGRATED_TASKS "
        "and add/confirm its endpoint-specific integration coverage in the same change: "
        + ", ".join(prematurely_migrated)
    )
