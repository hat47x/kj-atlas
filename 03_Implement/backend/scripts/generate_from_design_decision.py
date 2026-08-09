#!/usr/bin/env python3
"""Generate implementation code from a three-element-verified design decision.

ADR-0067: Code generation from design decisions (P2 automation).

Input: A JSON file describing the design decision with its three-element verification.
Output: Generated code files written to the appropriate locations.

Currently supports: ai_task type (the most common pattern).

Usage:
  python generate_from_design_decision.py design_decision.json [--dry-run]
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_SRC = REPO_ROOT / "03_Implement" / "backend" / "src" / "kj_atlas_api"
FRONTEND_SRC = REPO_ROOT / "03_Implement" / "frontend" / "src"

# Template files used as patterns
MODELS_AI_PY = BACKEND_SRC / "models_ai.py"
ROUTES_AI_PY = BACKEND_SRC / "routes" / "ai.py"
CLIENT_TS = FRONTEND_SRC / "api" / "client.ts"
AGENTS_MD = REPO_ROOT / "AGENTS.md"


def to_pascal_case(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split("_"))


def to_camel_case(snake: str) -> str:
    parts = snake.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


def generate_pydantic_models(decision: dict[str, Any]) -> str:
    """Generate Pydantic request/response models."""
    task_name = decision["taskName"]
    pascal = to_pascal_case(task_name)
    request_fields = decision.get("requestFields", [])
    response_fields = decision.get("responseFields", [])

    lines = []
    # Request model
    lines.append(f"\nclass {pascal}Request(BaseModel):")
    lines.append(f'    """{decision.get("humanReadableName", task_name)} request."""')
    lines.append('    model_config = ConfigDict(extra="forbid")')
    lines.append("")
    for field in request_fields:
        fname = field["name"]
        ftype = field.get("type", "str")
        constraints = []
        if field.get("maxLength"):
            constraints.append(f"max_length={field['maxLength']}")
        if field.get("minLength"):
            constraints.append(f"min_length={field['minLength']}")
        if "maxItems" in field:
            constraints.append(f"max_length={field['maxItems']}")
        if "minItems" in field:
            constraints.append(f"min_length={field['minItems']}")
        default = field.get("default")
        if default is not None:
            constraint_str = ", ".join(constraints)
            fdef = f"Field(default={default}"
            if constraint_str:
                fdef += f", {constraint_str}"
            fdef += ")"
        elif constraints:
            constraint_str = ", ".join(constraints)
            fdef = f"Field({constraint_str})"
        else:
            fdef = "..."
        lines.append(f"    {fname}: {ftype} = {fdef}")
    lines.append("")

    # Response model
    lines.append(f"\nclass {pascal}Response(BaseModel):")
    lines.append(f'    """{decision.get("humanReadableName", task_name)} response."""')
    lines.append('    model_config = ConfigDict(extra="forbid")')
    lines.append("")
    for field in response_fields:
        fname = field["name"]
        ftype = field.get("type", "str")
        lines.append(f"    {fname}: {ftype}")
    lines.append("")

    return "\n".join(lines)


def generate_route_handler(decision: dict[str, Any]) -> str:
    """Generate FastAPI route handler code."""
    task_name = decision["taskName"]
    pascal = to_pascal_case(task_name)
    camel = to_camel_case(task_name)
    endpoint = f"/{task_name.replace('_', '-')}"
    temperature = decision.get("temperature", 0.4)
    max_tokens = decision.get("maxTokens", 300)

    return f"""
@router.post(
    "{endpoint}",
    response_model={pascal}Response,
    dependencies=[Depends(require_tenant_scoped_api_precondition)],
)
def {camel}(payload: {pascal}Request) -> {pascal}Response:
    try:
        llm_response = generate_with_fallback(
            LLMRequest(
                task="{task_name}",
                prompt=_build_{task_name}_prompt(payload),
                temperature={temperature},
                max_tokens={max_tokens},
            )
        )
    except ProviderDisabledError as exc:
        _raise_llm_http_error(exc)
    except ProviderRequestError as exc:
        _raise_llm_http_error(exc)
    _audit_llm_trace("{task_name}", llm_response)
    return _parse_{task_name}_response(llm_response.raw_text)


def _build_{task_name}_prompt(payload: {pascal}Request) -> str:
    # TODO: Customize prompt for this task
    return json.dumps(payload.model_dump(), ensure_ascii=False)


def _parse_{task_name}_response(raw_text: str) -> {pascal}Response:
    data = json.loads(raw_text)
    return {pascal}Response(**data)
"""


def generate_client_function(decision: dict[str, Any]) -> str:
    """Generate TypeScript API client function."""
    task_name = decision["taskName"]
    pascal = to_pascal_case(task_name)
    camel = to_camel_case(task_name)
    endpoint = f"/{task_name.replace('_', '-')}"
    request_fields = decision.get("requestFields", [])
    response_fields = decision.get("responseFields", [])

    # Type definitions
    ts_types = []
    # Response type
    ts_types.append(f"export type {pascal}Response = {{")
    for field in response_fields:
        ts_types.append(f"  {field['name']}: {field.get('type', 'string')};")
    ts_types.append("};")
    ts_types.append("")

    # Function params
    params = []
    for field in request_fields:
        fname = field["name"]
        ftype = field.get("type", "str")
        ts_type = "string[]" if "list" in ftype else "string | undefined" if "null" in ftype else "string"
        params.append(f"  {fname}: {ts_type},")

    param_str = "\n".join(params)
    body_fields = ", ".join(f.name for f in [
        type("F", (), {"name": f["name"]})() for f in request_fields
    ])

    return f"""
{"".join(ts_types)}

export async function {camel}(
{param_str}
  requestOptions: TenantScopedRequestOptions = {{}},
): Promise<{pascal}Response> {{
  const response = await fetch(`${{API_BASE}}/ai{endpoint}`, {{
    method: "POST",
    headers: {{
      "Content-Type": "application/json",
      ...tenantSessionPreconditionHeaders(requestOptions),
    }},
    body: JSON.stringify({{}}),
  }});

  if (!response.ok) {{
    const errorDetail = await parseErrorDetail(response);
    throw new ApiError(response.status, errorDetail.message, {{
      code: errorDetail.code,
      disabledReason: errorDetail.disabledReason,
    }});
  }}

  return (await response.json()) as {pascal}Response;
}}
"""


def generate_import_lines(decision: dict[str, Any]) -> dict[str, str]:
    """Generate import lines to add to existing files."""
    task_name = decision["taskName"]
    pascal = to_pascal_case(task_name)

    return {
        "models_ai.py": f"from kj_atlas_api.models_ai import {pascal}Request, {pascal}Response",
        "routes/ai.py": f"    {pascal}Request,\n    {pascal}Response,",
    }


def check_three_element_verification(decision: dict[str, Any]) -> list[str]:
    """Verify the design decision has passed three-element constraint checking."""
    issues = []
    verification = decision.get("threeElementVerification", {})
    if not verification.get("business"):
        issues.append("Missing business design verification")
    if not verification.get("data"):
        issues.append("Missing data design verification")
    if not verification.get("function"):
        issues.append("Missing function design verification")
    return issues


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate code from a three-element-verified design decision"
    )
    parser.add_argument(
        "decision_file", type=Path,
        help="JSON file with the design decision"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would be generated without writing files"
    )
    parser.add_argument(
        "--check-only", action="store_true",
        help="Only verify three-element verification, don't generate"
    )
    args = parser.parse_args()

    if not args.decision_file.exists():
        print(f"Error: {args.decision_file} not found")
        return 1

    try:
        decision = json.loads(args.decision_file.read_text())
    except json.JSONDecodeError as e:
        print(f"Error: invalid JSON in {args.decision_file}: {e}")
        return 1

    design = decision.get("designDecision", decision)
    if design.get("type") != "ai_task":
        print(f"Error: only 'ai_task' type is currently supported, got '{design.get('type')}'")
        return 1

    # Verify three-element constraint check passed
    issues = check_three_element_verification(decision)
    if issues:
        print("ERROR: Design decision has NOT passed three-element verification:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nRun the three-element-constraint-checklist before generating code.")
        return 1

    if args.check_only:
        print("OK: Three-element verification passed")
        return 0

    task_name = design["taskName"]
    print(f"Generating code for AI task: {task_name}")
    print(f"  Model level: {design.get('modelLevel', 'not specified')}")
    print(f"  Recommended model: {design.get('recommendedModel', 'not specified')}")

    # Generate code
    print("\n=== Generated Pydantic models ===")
    models_code = generate_pydantic_models(design)
    print(models_code)

    print("=== Generated route handler ===")
    route_code = generate_route_handler(design)
    print(route_code)

    print("=== Generated client function ===")
    client_code = generate_client_function(design)
    print(client_code)

    if args.dry_run:
        print("\n[Dry run — no files written]")
        return 0

    print("\nNote: This is a template generator. Review and customize the output")
    print("before inserting into the actual codebase.")
    print(f"Target files:")
    print(f"  1. {MODELS_AI_PY} — append Pydantic models")
    print(f"  2. {ROUTES_AI_PY} — add route handler + prompt/parse functions + imports")
    print(f"  3. {CLIENT_TS} — add client function + types")
    print(f"  4. {AGENTS_MD} — add to operation model level table")

    return 0


if __name__ == "__main__":
    sys.exit(main())
