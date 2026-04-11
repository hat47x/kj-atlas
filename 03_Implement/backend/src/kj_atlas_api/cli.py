from __future__ import annotations

import argparse
import json

import httpx


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="kj_atlas_api.cli")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--actor-ref", default=None)
    parser.add_argument("--trace-id", default=None)

    subparsers = parser.add_subparsers(dest="command", required=True)
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
        sub.add_argument("--no-dry-run", action="store_false", dest="dry_run")
        sub.set_defaults(operation=operation)
    return parser.parse_args(argv)


def _build_payload(args: argparse.Namespace, input_payload: dict[str, object]) -> tuple[str, dict[str, object]]:
    doc_id = str(input_payload["docId"])
    payload = {
        "operation": args.operation,
        "safeMode": args.safe_mode,
        "bundleHash": input_payload.get("bundleHash"),
        "queryHash": input_payload.get("queryHash"),
        "dryRun": args.dry_run,
        "rejectReasonCode": input_payload.get("rejectReasonCode"),
        "command": args.command,
        "channel": "cli",
    }
    return doc_id, payload


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    with open(args.input, encoding="utf-8") as fh:
        input_payload = json.load(fh)
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
