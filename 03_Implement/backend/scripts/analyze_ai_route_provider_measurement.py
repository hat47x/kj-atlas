#!/usr/bin/env python3
"""Validate and summarize AI route provider-token measurement JSON.

This analyzer is intentionally downstream of ``measure_ai_route_provider_tokens.py``.
It never estimates tokens from prompt bytes/chars and never chooses A2/B/C. Its job is
to answer a narrower question: is a saved measurement report internally complete enough
for the next architecture comparison, and which provider-reported observations are
actually available?

Usage::

    python scripts/analyze_ai_route_provider_measurement.py measurement.json
    cat measurement.json | python scripts/analyze_ai_route_provider_measurement.py -

A dry-run report is valid JSON but is not decision-ready. Missing provider usage,
provider/model mismatches, partial layout-C batches, and malformed route rows are
reported as explicit validation errors rather than being filled from diagnostic bytes.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

try:
    from scripts.measure_ai_route_provider_tokens import (
        _prompt_sha256,
        build_representative_requests,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from measure_ai_route_provider_tokens import (
        _prompt_sha256,
        build_representative_requests,
    )

MEASUREMENT_NAME = "ai-route-provider-reported-input-tokens"
SCENARIO_NAME = "300-cards-30-islands-ring"
PROMPT_FINGERPRINT = {"algorithm": "sha256", "encoding": "utf-8"}
PROVIDER_CALL_PROVENANCE = {"version": 1}
CORE_ROUTE_TASKS = {
    "suggest-card-groups": "suggest_card_groups",
    "suggest-card-groups-route-b": "suggest_card_groups",
    "suggest-layout": "re_layout",
    "suggest-layout-route-b": "re_layout",
    "generate-narrative": "generate_narrative",
    "check-narrative": "check_narrative",
}
CORE_ROUTES = tuple(CORE_ROUTE_TASKS)
GROUPS_A2_ROUTE = "suggest-card-groups-a2-lower-bound"
LAYOUT_C_PREFIX = "suggest-layout-c-"
LAYOUT_C_ROUTES = tuple(
    [f"suggest-layout-c-local-{index:02d}" for index in range(1, 31)]
    + ["suggest-layout-c-global"]
)
LAYOUT_C_REQUESTS = len(LAYOUT_C_ROUTES)


def _int_token(row: dict[str, Any]) -> int | None:
    value = (row.get("provider_reported") or {}).get("input_tokens")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _validate_measured_route(
    *,
    name: str,
    row: Any,
    expected_task: str,
    expected_provider: str,
    expected_model: str,
    expected_prompt_sha256: str | None,
    errors: list[str],
) -> int | None:
    if not isinstance(row, dict):
        errors.append(f"route-not-object:{name}")
        return None
    if row.get("task") != expected_task:
        errors.append(f"task-mismatch:{name}")
        return None
    prompt = row.get("prompt")
    if not isinstance(prompt, dict):
        errors.append(f"prompt-diagnostics-missing:{name}")
        return None
    if expected_prompt_sha256 is None:
        errors.append(f"canonical-prompt-missing:{name}")
        return None
    if prompt.get("sha256") != expected_prompt_sha256:
        errors.append(f"prompt-fingerprint-mismatch:{name}")
        return None
    if row.get("status") != "measured":
        errors.append(f"route-not-measured:{name}:{row.get('status')}")
        return None
    if row.get("actual_provider") != expected_provider:
        errors.append(f"provider-mismatch:{name}")
        return None
    if row.get("actual_model") != expected_model:
        errors.append(f"model-mismatch:{name}")
        return None

    provider_call = row.get("provider_call")
    if not isinstance(provider_call, dict):
        errors.append(f"provider-call-metadata-missing:{name}")
        return None
    if provider_call.get("provider") != expected_provider:
        errors.append(f"provider-call-provider-mismatch:{name}")
        return None
    if provider_call.get("provider_kind") != row.get("actual_provider_kind"):
        errors.append(f"provider-call-kind-mismatch:{name}")
        return None
    if provider_call.get("model_id") != expected_model:
        errors.append(f"provider-call-model-mismatch:{name}")
        return None
    for field in ("transport", "requested_at", "trace_id"):
        value = provider_call.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"provider-call-{field}-missing:{name}")
            return None
    if provider_call.get("fallback_to_none") is not False:
        errors.append(f"provider-call-fallback-detected:{name}")
        return None
    if provider_call.get("execution_path") != "primary":
        errors.append(f"provider-call-non-primary-path:{name}")
        return None

    token = _int_token(row)
    if token is None:
        errors.append(f"input-usage-missing:{name}")
        return None
    return token


def analyze(report: Any) -> dict[str, Any]:
    """Return a fail-closed comparison-readiness summary for one saved report."""
    errors: list[str] = []
    if not isinstance(report, dict):
        return {
            "analysis": "ai-route-provider-measurement-readiness",
            "decision_ready": False,
            "errors": ["report-not-object"],
        }

    if report.get("measurement") != MEASUREMENT_NAME:
        errors.append("unexpected-measurement-kind")
    if report.get("scenario") != SCENARIO_NAME:
        errors.append("unexpected-scenario")
    if report.get("prompt_fingerprint") != PROMPT_FINGERPRINT:
        errors.append("unsupported-or-missing-prompt-fingerprint")
    if report.get("provider_call_provenance") != PROVIDER_CALL_PROVENANCE:
        errors.append("unsupported-or-missing-provider-call-provenance")

    expected_provider = report.get("expected_provider")
    expected_model = report.get("expected_model")
    if not isinstance(expected_provider, str) or not expected_provider.strip():
        errors.append("missing-expected-provider")
        expected_provider = ""
    if not isinstance(expected_model, str) or not expected_model.strip():
        errors.append("missing-expected-model")
        expected_model = ""

    executed = report.get("executed") is True
    if not executed:
        errors.append("report-not-executed")

    routes = report.get("routes")
    if not isinstance(routes, dict):
        errors.append("routes-not-object")
        routes = {}

    include_groups_a2 = GROUPS_A2_ROUTE in routes
    include_layout_c = any(name.startswith(LAYOUT_C_PREFIX) for name in routes)
    canonical_requests = (
        build_representative_requests(
            expected_model,
            include_groups_a2=include_groups_a2,
            include_layout_c=include_layout_c,
        )
        if expected_model
        else {}
    )
    canonical_prompt_hashes = {
        name: _prompt_sha256(req.prompt) for name, req in canonical_requests.items()
    }
    for unexpected in sorted(set(routes) - set(canonical_requests)):
        errors.append(f"unexpected-route:{unexpected}")

    tokens: dict[str, int] = {}
    for name, expected_task in CORE_ROUTE_TASKS.items():
        if name not in routes:
            errors.append(f"missing-core-route:{name}")
            continue
        token = _validate_measured_route(
            name=name,
            row=routes[name],
            expected_task=expected_task,
            expected_provider=expected_provider,
            expected_model=expected_model,
            expected_prompt_sha256=canonical_prompt_hashes.get(name),
            errors=errors,
        )
        if token is not None:
            tokens[name] = token

    groups_a2_present = GROUPS_A2_ROUTE in routes
    if groups_a2_present:
        token = _validate_measured_route(
            name=GROUPS_A2_ROUTE,
            row=routes[GROUPS_A2_ROUTE],
            expected_task="suggest_card_groups",
            expected_provider=expected_provider,
            expected_model=expected_model,
            expected_prompt_sha256=canonical_prompt_hashes.get(GROUPS_A2_ROUTE),
            errors=errors,
        )
        if token is not None:
            tokens[GROUPS_A2_ROUTE] = token

    layout_c_names = sorted(name for name in routes if name.startswith(LAYOUT_C_PREFIX))
    layout_c_present = bool(layout_c_names)
    expected_layout_c = set(LAYOUT_C_ROUTES)
    actual_layout_c = set(layout_c_names)
    layout_c_tokens: list[int] = []
    if layout_c_present:
        for missing in sorted(expected_layout_c - actual_layout_c):
            errors.append(f"layout-c-missing-route:{missing}")
        for unexpected in sorted(actual_layout_c - expected_layout_c):
            errors.append(f"layout-c-unexpected-route:{unexpected}")
        for name in layout_c_names:
            token = _validate_measured_route(
                name=name,
                row=routes[name],
                expected_task="re_layout",
                expected_provider=expected_provider,
                expected_model=expected_model,
                expected_prompt_sha256=canonical_prompt_hashes.get(name),
                errors=errors,
            )
            if token is not None and name in expected_layout_c:
                layout_c_tokens.append(token)

    core_ready = all(name in tokens for name in CORE_ROUTES)
    groups_a2_ready = groups_a2_present and GROUPS_A2_ROUTE in tokens
    layout_c_ready = (
        layout_c_present
        and actual_layout_c == expected_layout_c
        and len(layout_c_tokens) == LAYOUT_C_REQUESTS
    )

    groups: dict[str, Any] = {
        "current_input_tokens": tokens.get("suggest-card-groups"),
        "route_b_input_tokens": tokens.get("suggest-card-groups-route-b"),
        "a2_input_tokens": tokens.get(GROUPS_A2_ROUTE),
        "a2_measured": groups_a2_ready,
        "route_b_minus_current_input_tokens": None,
        "a2_minus_route_b_input_tokens": None,
    }
    if {
        "suggest-card-groups",
        "suggest-card-groups-route-b",
    }.issubset(tokens):
        groups["route_b_minus_current_input_tokens"] = (
            tokens["suggest-card-groups-route-b"] - tokens["suggest-card-groups"]
        )
    if groups_a2_ready and "suggest-card-groups-route-b" in tokens:
        groups["a2_minus_route_b_input_tokens"] = (
            tokens[GROUPS_A2_ROUTE] - tokens["suggest-card-groups-route-b"]
        )

    layout: dict[str, Any] = {
        "current_input_tokens": tokens.get("suggest-layout"),
        "route_b_input_tokens": tokens.get("suggest-layout-route-b"),
        "route_b_minus_current_input_tokens": None,
        "a2_reuses_route_b_observation": True,
        "a2_reuse_reason": (
            "R29 fixed the representative layout A2 and route-B rendered prompts as "
            "identical under the same task/model/max_tokens contract; no duplicate "
            "provider request is required."
        ),
        "layout_c_measured": layout_c_ready,
        "layout_c_requests": len(layout_c_names),
        "layout_c_max_single_input_tokens": (
            max(layout_c_tokens) if layout_c_ready else None
        ),
        "layout_c_aggregate_input_tokens": (
            sum(layout_c_tokens) if layout_c_ready else None
        ),
    }
    if {"suggest-layout", "suggest-layout-route-b"}.issubset(tokens):
        layout["route_b_minus_current_input_tokens"] = (
            tokens["suggest-layout-route-b"] - tokens["suggest-layout"]
        )

    whole_document = {
        "generate_narrative_input_tokens": tokens.get("generate-narrative"),
        "check_narrative_input_tokens": tokens.get("check-narrative"),
        "check_minus_generate_input_tokens": None,
    }
    if {"generate-narrative", "check-narrative"}.issubset(tokens):
        whole_document["check_minus_generate_input_tokens"] = (
            tokens["check-narrative"] - tokens["generate-narrative"]
        )

    # ``measurement_complete`` is useful evidence but is not trusted by itself:
    # every route row is revalidated above. Conversely, a complete six-route core
    # report remains usable even when optional A2/C observations were not requested.
    measurement_complete_claim = report.get("measurement_complete") is True
    if executed and core_ready and not measurement_complete_claim:
        errors.append("measurement-complete-claim-false")

    return {
        "analysis": "ai-route-provider-measurement-readiness",
        "scenario": report.get("scenario"),
        "provider": expected_provider or None,
        "model": expected_model or None,
        "executed": executed,
        "core_ready": core_ready,
        "groups_a2_ready": groups_a2_ready,
        "layout_c_ready": layout_c_ready,
        "decision_ready": executed and core_ready and not errors,
        "errors": errors,
        "observations": {
            "groups": groups,
            "layout": layout,
            "whole_document": whole_document,
        },
        "interpretation_boundary": (
            "All token observations and deltas come only from provider_reported.input_tokens. "
            "Prompt SHA-256 is used only for exact UTF-8 prompt identity/provenance; bytes, chars, "
            "and hashes are never converted into tokens. This report does not know the "
            "model context limit or choose A2/B/C; optional A2/C readiness only records whether "
            "those explicit measurements are present and internally complete."
        ),
    }


def _load(path: str) -> Any:
    if path == "-":
        return json.load(sys.stdin)
    with Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", help="measurement JSON path, or '-' to read stdin")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        result = analyze(_load(args.report))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "analysis": "ai-route-provider-measurement-readiness",
            "decision_ready": False,
            "errors": [f"measurement-report-read-error:{type(exc).__name__}"],
        }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("decision_ready") else 2


if __name__ == "__main__":
    raise SystemExit(main())
