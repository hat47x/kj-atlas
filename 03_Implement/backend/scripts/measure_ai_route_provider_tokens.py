#!/usr/bin/env python3
"""Measure provider-reported input tokens for representative AI route prompts.

`AI-IR-SCALE-01` must not infer exact token counts from JSON bytes.  This tool
renders the same deterministic 300-card / 30-island source used by the scale
coverage probes, then optionally sends two representative prompts to one
explicitly named provider/model and records the provider-reported usage.

The default is a dry run: it never constructs or calls a provider.  External
execution requires BOTH `--execute` and `KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN=1`.
Only synthetic fixture-like text from `representative_document()` is sent.

The two routes are deliberately different:

- `suggest-layout`: the heaviest migrated route; normalized coordinates,
  relations and island structure are part of the IR context.
- `generate-narrative`: a representative non-coordinate route; reading order
  stays document-derived while logical relations come from the IR.

A provider that does not report input-token usage is not estimated.  The output
records `provider-did-not-report-usage` and `measurement_complete=false` instead.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Any, Protocol

from kj_atlas_api.llm.provider import LLMRequest, LLMResponse, ProviderError, get_provider
from kj_atlas_api.models import SuggestLayoutRequest
from kj_atlas_api.models_ai import GenerateNarrativeRequest
from kj_atlas_api.routes.ai import (
    _build_generate_narrative_prompt,
    _build_prompt,
    _generate_narrative_ir,
    _suggest_layout_ir,
)
from scripts.measure_ai_route_prompt_coverage import representative_document

OPT_IN_ENV = "KJ_ATLAS_TOKEN_MEASUREMENT_OPT_IN"
_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})


class _Provider(Protocol):
    provider_name: str
    provider_kind: str

    def generate(self, req: LLMRequest) -> LLMResponse:
        ...


def build_representative_requests(model: str) -> dict[str, LLMRequest]:
    """Render the two prompts from the exact same deterministic source document."""
    doc = representative_document(include_evidence=False)

    layout_payload = SuggestLayoutRequest.model_validate({"doc": doc})
    layout_ir = _suggest_layout_ir(layout_payload)
    layout_prompt = _build_prompt(layout_payload, layout_ir)

    narrative_payload = GenerateNarrativeRequest.model_validate({"doc": doc})
    narrative_ir = _generate_narrative_ir(narrative_payload)
    narrative_prompt = _build_generate_narrative_prompt(narrative_payload, narrative_ir)

    return {
        "suggest-layout": LLMRequest(
            task="re_layout",
            prompt=layout_prompt,
            inputs=layout_ir,
            temperature=0.0,
            # Input-token measurement does not need a substantive completion.
            # Keep output cost/latency to the minimum accepted by the provider layer.
            max_tokens=1,
            model=model,
        ),
        "generate-narrative": LLMRequest(
            task="generate_narrative",
            prompt=narrative_prompt,
            inputs=narrative_ir,
            temperature=0.0,
            max_tokens=1,
            model=model,
        ),
    }


def _route_row(req: LLMRequest) -> dict[str, Any]:
    return {
        "task": req.task,
        "prompt": {
            "unicode_chars": len(req.prompt),
            "utf8_bytes": len(req.prompt.encode("utf-8")),
        },
        "ir": {
            "cards": len((req.inputs or {}).get("cards", [])),
            "relations": len((req.inputs or {}).get("relations", [])),
            "islands": len((req.inputs or {}).get("islands", [])),
            "coordinates": len((req.inputs or {}).get("coordinates", [])),
            "truncation": (req.inputs or {}).get("truncation"),
        },
        "provider_reported": {
            "input_tokens": None,
            "output_tokens": None,
        },
        "status": "dry-run",
    }


def measure(
    *,
    model: str,
    expected_provider: str,
    execute: bool = False,
    provider: _Provider | None = None,
) -> dict[str, Any]:
    """Build a measurement report, optionally calling an already-resolved provider.

    `expected_provider` and `model` are mandatory names so a measurement can
    never silently run against whichever provider/model happens to be configured.
    The CLI resolves the provider only after the two explicit opt-ins pass.
    """
    if not model.strip():
        raise ValueError("model must be a non-empty explicit model id")
    if not expected_provider.strip():
        raise ValueError("expected_provider must be a non-empty explicit provider name")

    requests = build_representative_requests(model)
    routes = {name: _route_row(req) for name, req in requests.items()}
    report: dict[str, Any] = {
        "measurement": "ai-route-provider-reported-input-tokens",
        "scenario": "300-cards-30-islands-ring",
        "expected_provider": expected_provider,
        "expected_model": model,
        "executed": execute,
        "measurement_complete": False,
        "routes": routes,
        "interpretation_boundary": (
            "Exact token counts are accepted only from provider-reported usage. "
            "Prompt bytes/chars are diagnostics, never token estimates."
        ),
    }

    if not execute:
        return report
    if provider is None:
        raise ValueError("provider is required when execute=True")
    if provider.provider_name != expected_provider:
        raise ValueError(
            "configured provider does not match the explicitly named measurement provider"
        )

    all_measured = True
    for route_name, req in requests.items():
        row = routes[route_name]
        try:
            response = provider.generate(req)
        except ProviderError as exc:
            row["status"] = "provider-error"
            row["provider_error"] = exc.to_contract()
            all_measured = False
            continue

        row["actual_provider"] = response.metadata.provider_name
        row["actual_provider_kind"] = response.metadata.provider_kind
        row["actual_model"] = response.metadata.model_id
        row["provider_reported"] = {
            "input_tokens": response.input_tokens,
            "output_tokens": response.output_tokens,
        }

        if response.metadata.provider_name != expected_provider:
            row["status"] = "provider-mismatch"
            all_measured = False
        elif response.metadata.model_id != model:
            row["status"] = "model-mismatch"
            all_measured = False
        elif response.input_tokens is None:
            row["status"] = "provider-did-not-report-usage"
            all_measured = False
        else:
            row["status"] = "measured"

    report["measurement_complete"] = all_measured
    return report


def _opted_in() -> bool:
    return os.environ.get(OPT_IN_ENV, "").strip().lower() in _TRUE_VALUES


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--provider",
        required=True,
        help="Exact provider_name expected from the configured provider (for example: deepseek).",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Exact model id to use for both representative routes.",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help=(
            "Actually send the synthetic representative prompts. Also requires "
            f"{OPT_IN_ENV}=1. Without this flag the command is a no-network dry run."
        ),
    )
    return parser


def main() -> int:
    args = _parser().parse_args()

    if not args.execute:
        print(
            json.dumps(
                measure(
                    model=args.model,
                    expected_provider=args.provider,
                    execute=False,
                ),
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    if not _opted_in():
        print(
            json.dumps(
                {
                    "measurement": "ai-route-provider-reported-input-tokens",
                    "measurement_complete": False,
                    "status": "external-execution-not-opted-in",
                    "required_env": OPT_IN_ENV,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    provider = get_provider()
    try:
        report = measure(
            model=args.model,
            expected_provider=args.provider,
            execute=True,
            provider=provider,
        )
    except ValueError as exc:
        print(
            json.dumps(
                {
                    "measurement": "ai-route-provider-reported-input-tokens",
                    "measurement_complete": False,
                    "status": "configuration-mismatch",
                    "message": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 2

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["measurement_complete"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
