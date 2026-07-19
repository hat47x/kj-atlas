from __future__ import annotations

import argparse
import json
from typing import Any

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
    headers: dict[str, str] = {}
    if args.actor_ref:
        headers["x-actor-ref"] = args.actor_ref
    if args.trace_id:
        headers["x-trace-id"] = args.trace_id

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
