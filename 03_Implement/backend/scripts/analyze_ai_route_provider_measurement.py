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

MEASUREMENT_NAME = "ai-route-provider-reported-input-tokens"
SCENARIO_NAME = "300-cards-30-islands-ring"
CORE_ROUTES = (
    "suggest-card-groups",
    "suggest-card-groups-route-b",
    "suggest-layout",
    "suggest-layout-route-b",
    "generate-narrative",
    "check-narrative",
)
GROUPS_A2_ROUTE = "suggest-card-groups-a2-lower-bound"
LAYOUT_C_PREFIX = "suggest-layout-c-"
LAYOUT_C_REQUESTS = 31


def _int_token(row: dict[str, Any]) -> int | None:
    value = (row.get("provider_reported") or {}).get("input_tokens")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        return None
    return value


def _validate_measured_route(
    *,
    name: str,
    row: Any,
    expected_provider: str,
    expected_model: str,
    errors: list[str],
) -> int | None:
    if not isinstance(row, dict):
        errors.append(f"route-not-object:{name}")
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

    tokens: dict[str, int] = {}
    for name in CORE_ROUTES:
        if name not in routes:
            errors.append(f"missing-core-route:{name}")
            continue
        token = _validate_measured_route(
            name=name,
            row=routes[name],
            expected_provider=expected_provider,
            expected_model=expected_model,
            errors=errors,
        )
        if token is not None:
            tokens[name] = token

    groups_a2_present = GROUPS_A2_ROUTE in routes
    if groups_a2_present:
        token = _validate_measured_route(
            name=GROUPS_A2_ROUTE,
            row=routes[GROUPS_A2_ROUTE],
            expected_provider=expected_provider,
            expected_model=expected_model,
            errors=errors,
        )
        if token is not None:
            tokens[GROUPS_A2_ROUTE] = token

    layout_c_names = sorted(name for name in routes if name.startswith(LAYOUT_C_PREFIX))
    layout_c_present = bool(layout_c_names)
    layout_c_tokens: list[int] = []
    if layout_c_present:
        if len(layout_c_names) != LAYOUT_C_REQUESTS:
            errors.append(
                f"layout-c-request-count:{len(layout_c_names)}:{LAYOUT_C_REQUESTS}"
            )
        for name in layout_c_names:
            token = _validate_measured_route(
                name=name,
                row=routes[name],
                expected_provider=expected_provider,
                expected_model=expected_model,
                errors=errors,
            )
            if token is not None:
                layout_c_tokens.append(token)

    core_ready = all(name in tokens for name in CORE_ROUTES)
    groups_a2_ready = groups_a2_present and GROUPS_A2_ROUTE in tokens
    layout_c_ready = (
        layout_c_present
        and len(layout_c_names) == LAYOUT_C_REQUESTS
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
            "Prompt bytes/chars are never converted into tokens. This report does not know the "
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
