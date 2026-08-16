from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any
from urllib.parse import quote

import httpx

from kj_atlas_api.audit import CE4_AUDIT_SCHEMA_VERSION, normalize_ce4_audit_metadata


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="kj_atlas_api.cli")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--actor-ref", default=None)
    parser.add_argument("--trace-id", default=None)

    subparsers = parser.add_subparsers(dest="command", required=True)
    ce4_parser = subparsers.add_parser("ce4")
    ce4_subparsers = ce4_parser.add_subparsers(dest="ce4_command", required=True)
    ce4_resolve = ce4_subparsers.add_parser("resolve-bundle")
    ce4_resolve.add_argument("--query", required=True)
    ce4_resolve.add_argument("--dry-run", action="store_true", default=True)
    ce4_resolve.add_argument("--no-dry-run", action="store_false", dest="dry_run")
    ce4_resolve.add_argument("--source-bundle-hash", required=True)
    ce4_resolve.add_argument("--safe-mode", action="store_true", default=True)
    ce4_resolve.add_argument("--no-safe-mode", action="store_false", dest="safe_mode")

    admin_parser = subparsers.add_parser(
        "admin",
        help="Operate the control plane using KJ_ATLAS_ADMIN_API_KEY.",
    )
    admin_subparsers = admin_parser.add_subparsers(dest="admin_resource", required=True)

    providers_parser = admin_subparsers.add_parser("providers")
    providers_subparsers = providers_parser.add_subparsers(
        dest="admin_action", required=True
    )
    provider_register = providers_subparsers.add_parser("register")
    provider_register.add_argument("--id", required=True)
    provider_register.add_argument("--kind", required=True)
    provider_register.add_argument("--display-name", required=True)
    provider_register.add_argument("--base-url")
    provider_register.add_argument("--api-key-ref")
    provider_register.add_argument("--yes", action="store_true")

    models_parser = admin_subparsers.add_parser("models")
    models_subparsers = models_parser.add_subparsers(dest="admin_action", required=True)
    models_subparsers.add_parser("list")
    model_register = models_subparsers.add_parser("register")
    model_register.add_argument("--id", required=True)
    model_register.add_argument("--provider-id", required=True)
    model_register.add_argument("--display-name", required=True)
    model_register.add_argument("--capabilities")
    model_register.add_argument("--yes", action="store_true")
    model_lifecycle = models_subparsers.add_parser("set-lifecycle")
    model_lifecycle.add_argument("--id", required=True)
    model_lifecycle.add_argument("--state", choices=("active", "disabled"), required=True)
    model_lifecycle.add_argument("--yes", action="store_true")

    tenants_parser = admin_subparsers.add_parser("tenants")
    tenants_subparsers = tenants_parser.add_subparsers(dest="admin_action", required=True)
    allowlist_get = tenants_subparsers.add_parser("model-allowlist-get")
    allowlist_get.add_argument("--tenant-id", required=True)
    allowlist_set = tenants_subparsers.add_parser("model-allowlist-set")
    allowlist_set.add_argument("--tenant-id", required=True)
    allowlist_set.add_argument(
        "--model-id",
        action="append",
        default=[],
        help="Allowed model ID. Repeat for multiple models; omit all to clear.",
    )
    allowlist_set.add_argument("--yes", action="store_true")

    audit_parser = admin_subparsers.add_parser("audit")
    audit_subparsers = audit_parser.add_subparsers(dest="admin_action", required=True)
    audit_list = audit_subparsers.add_parser("list")
    audit_list.add_argument("--limit", type=int, default=100)
    audit_list.add_argument("--cursor")

    for command, operation in (
        ("context-query", "query"),
        ("context-bundle", "bundle"),
        ("proposal-diff", "proposal"),
        ("apply", "apply"),
    ):
        sub = subparsers.add_parser(command)
        sub.add_argument("--input", required=True, help="JSON file containing at least docId")
        sub.add_argument("--safe-mode", action="store_true", default=True)
        sub.add_argument("--no-safe-mode", action="store_false", dest="safe_mode")
        sub.add_argument("--dry-run", action="store_true", default=True)
        sub.set_defaults(operation=operation)
    return parser.parse_args(argv)


def _business_plane_headers(*, actor_ref: str | None = None, trace_id: str | None = None) -> dict[str, str]:
    """Build non-secret and business-plane auth headers for CLI requests.

    The API key is environment-only by design: accepting it as a command-line
    option would expose it in shell history and process listings. Empty or
    whitespace-only values behave as unset, preserving open local-dev mode.
    """
    headers: dict[str, str] = {}
    api_key = (os.environ.get("KJ_ATLAS_API_KEY") or "").strip()
    if api_key:
        headers["x-api-key"] = api_key
    if actor_ref:
        headers["x-actor-ref"] = actor_ref
    if trace_id:
        headers["x-trace-id"] = trace_id
    return headers


def _control_plane_headers(
    *, actor_ref: str | None = None, trace_id: str | None = None
) -> dict[str, str]:
    """Build admin headers without accepting secrets in process arguments."""
    headers: dict[str, str] = {}
    admin_api_key = (os.environ.get("KJ_ATLAS_ADMIN_API_KEY") or "").strip()
    if admin_api_key:
        headers["x-admin-api-key"] = admin_api_key
    if actor_ref:
        headers["x-actor-ref"] = actor_ref
    if trace_id:
        headers["x-request-id"] = trace_id
    return headers


def _print_json(payload: object, *, stream: Any | None = None) -> None:
    print(
        json.dumps(payload, ensure_ascii=False, sort_keys=True),
        file=sys.stdout if stream is None else stream,
    )


def _request_json(
    args: argparse.Namespace,
    method: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
    params: dict[str, object] | None = None,
) -> object:
    try:
        response = httpx.request(
            method,
            f"{args.api_base_url.rstrip('/')}{path}",
            json=payload,
            params=params,
            headers=_control_plane_headers(actor_ref=args.actor_ref, trace_id=args.trace_id),
            timeout=10.0,
        )
    except httpx.RequestError as exc:
        _print_json(
            {"ok": False, "code": "control_plane_unreachable", "message": str(exc)},
            stream=sys.stderr,
        )
        raise SystemExit(3) from None

    if response.is_error:
        try:
            response_payload = response.json()
        except ValueError:
            response_payload = {"detail": "Control plane returned a non-JSON error."}
        detail = response_payload.get("detail", response_payload) if isinstance(response_payload, dict) else response_payload
        _print_json(
            {"ok": False, "status": response.status_code, "error": detail},
            stream=sys.stderr,
        )
        raise SystemExit(2)
    try:
        return response.json()
    except ValueError:
        return {"status": "ok"}


def _confirm_admin_write(args: argparse.Namespace, preview: dict[str, object]) -> None:
    _print_json({"changePreview": preview}, stream=sys.stderr)
    if args.yes:
        return
    if not sys.stdin.isatty():
        raise SystemExit("admin write requires --yes when stdin is not interactive")
    answer = input("Apply this control-plane change? [y/N] ").strip().lower()
    if answer not in {"y", "yes"}:
        raise SystemExit("admin change cancelled")


def _admin_main(args: argparse.Namespace) -> int:
    resource = args.admin_resource
    action = args.admin_action

    if resource == "models" and action == "list":
        _print_json(_request_json(args, "GET", "/admin/provision/models"))
        return 0
    if resource == "providers" and action == "register":
        payload = {
            "id": args.id,
            "providerKind": args.kind,
            "displayName": args.display_name,
            "baseUrl": args.base_url,
            "apiKeyRef": args.api_key_ref,
        }
        _confirm_admin_write(args, {"operation": "registerProvider", "after": payload})
        _print_json(_request_json(args, "POST", "/admin/provision/models/providers", payload=payload))
        return 0
    if resource == "models" and action == "register":
        payload = {
            "id": args.id,
            "providerId": args.provider_id,
            "displayName": args.display_name,
            "capabilities": args.capabilities,
        }
        _confirm_admin_write(args, {"operation": "registerModel", "after": payload})
        _print_json(_request_json(args, "POST", "/admin/provision/models", payload=payload))
        return 0
    if resource == "models" and action == "set-lifecycle":
        registry = _request_json(args, "GET", "/admin/provision/models")
        models = registry.get("models", []) if isinstance(registry, dict) else []
        current = next(
            (item for item in models if isinstance(item, dict) and item.get("id") == args.id),
            None,
        )
        _confirm_admin_write(
            args,
            {
                "operation": "setModelLifecycle",
                "modelId": args.id,
                "before": current,
                "after": {"lifecycleState": args.state},
            },
        )
        model_id = quote(args.id, safe="")
        _print_json(
            _request_json(
                args,
                "PATCH",
                f"/admin/provision/models/{model_id}",
                payload={"lifecycleState": args.state},
            )
        )
        return 0
    if resource == "tenants" and action == "model-allowlist-get":
        tenant_id = quote(args.tenant_id, safe="")
        _print_json(
            _request_json(
                args, "GET", f"/admin/provision/models/tenants/{tenant_id}/allowlist"
            )
        )
        return 0
    if resource == "tenants" and action == "model-allowlist-set":
        tenant_id = quote(args.tenant_id, safe="")
        path = f"/admin/provision/models/tenants/{tenant_id}/allowlist"
        current = _request_json(args, "GET", path)
        before = current.get("modelIds", []) if isinstance(current, dict) else []
        after = sorted(args.model_id)
        _confirm_admin_write(
            args,
            {
                "operation": "setTenantModelAllowlist",
                "tenantId": args.tenant_id,
                "before": before,
                "after": after,
                "added": sorted(set(after) - set(before)),
                "removed": sorted(set(before) - set(after)),
            },
        )
        _print_json(_request_json(args, "PUT", path, payload={"modelIds": args.model_id}))
        return 0
    if resource == "audit" and action == "list":
        params: dict[str, object] = {"limit": args.limit}
        if args.cursor:
            params["cursor"] = args.cursor
        _print_json(_request_json(args, "GET", "/admin/provision/audit", params=params))
        return 0
    raise SystemExit("unsupported admin command")




def _validate_ce4_resolve_response(payload: dict[str, Any], *, dry_run: bool) -> None:
    required_fields = (
        "equivalenceKey",
        "bundleHash",
        "queryCanonicalHash",
        "proposalLifecycle",
        "sideEffect",
        "auditChain",
    )
    missing = [field for field in required_fields if field not in payload]
    if missing:
        raise SystemExit(f"CE4 fail-closed: missing response field(s): {', '.join(missing)}")

    if dry_run and payload.get("sideEffect") != "none":
        raise SystemExit("CE4 fail-closed: dryRun=true requires sideEffect=none")

    audit_chain = payload.get("auditChain")
    if not isinstance(audit_chain, dict):
        raise SystemExit("CE4 fail-closed: auditChain must be an object")

    for event_key in ("query", "bundle", "proposal", "apply"):
        if event_key not in audit_chain:
            raise SystemExit(f"CE4 fail-closed: auditChain missing '{event_key}'")

def _build_payload(args: argparse.Namespace, input_payload: dict[str, object]) -> tuple[str, dict[str, object]]:
    doc_id = str(input_payload["docId"])
    equivalence_key = input_payload.get("equivalenceKey")
    bundle_hash = input_payload.get("bundleHash")
    if not isinstance(equivalence_key, str) or not equivalence_key:
        raise SystemExit("input JSON must include equivalenceKey")
    if not isinstance(bundle_hash, str) or not bundle_hash:
        raise SystemExit("input JSON must include bundleHash")

    dry_run = args.dry_run
    if args.operation == "apply":
        dry_run = True
    side_effect = input_payload.get("sideEffect", "none")
    if dry_run:
        side_effect = "none"

    operation_to_command = {
        "query": "context-query",
        "bundle": "context-bundle",
        "proposal": "proposal-diff",
        "apply": "apply --dry-run",
    }

    query_hash = input_payload.get("queryCanonicalHash", input_payload.get("queryHash", equivalence_key))

    payload = normalize_ce4_audit_metadata(
        {
            "operation": args.operation,
            "safeMode": args.safe_mode,
            "equivalenceKey": equivalence_key,
            "bundleHash": bundle_hash,
            "sourceBundleHash": input_payload.get("sourceBundleHash"),
            "queryHash": query_hash,
            "dryRun": dry_run,
            "sideEffect": side_effect,
            "rejectReasonCode": input_payload.get("rejectReasonCode"),
            "command": operation_to_command[args.operation],
            "channel": "cli",
            "schemaVersion": CE4_AUDIT_SCHEMA_VERSION,
            "ignoredInput": input_payload.get("ignoredInput"),
        }
    )
    return doc_id, payload


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if args.command == "admin":
        return _admin_main(args)
    if args.command == "ce4":
        payload = {
            "query": args.query,
            "dryRun": args.dry_run,
            "sourceBundleHash": args.source_bundle_hash,
            "safeMode": args.safe_mode,
        }
        response = httpx.post(
            f"{args.api_base_url}/context/bundles:resolve",
            json=payload,
            headers=_business_plane_headers(),
            timeout=5.0,
        )
        response.raise_for_status()
        response_payload = response.json()
        if not isinstance(response_payload, dict):
            raise SystemExit("CE4 fail-closed: response must be a JSON object")
        _validate_ce4_resolve_response(response_payload, dry_run=args.dry_run)
        print(json.dumps(response_payload, ensure_ascii=False))
        return 0

    try:
        with open(args.input, encoding="utf-8") as fh:
            input_payload = json.load(fh)
    except OSError as exc:
        raise SystemExit(f"could not read --input file: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"--input file is not valid JSON: {exc}") from exc
    if "docId" not in input_payload:
        raise SystemExit("input JSON must include docId")

    doc_id, payload = _build_payload(args, input_payload)
    headers = _business_plane_headers(actor_ref=args.actor_ref, trace_id=args.trace_id)

    response = httpx.post(
        f"{args.api_base_url}/docs/{doc_id}/context-audit",
        json=payload,
        headers=headers,
        timeout=5.0,
    )
    response.raise_for_status()
    print(response.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
