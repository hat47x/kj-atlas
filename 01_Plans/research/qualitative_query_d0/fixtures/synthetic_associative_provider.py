#!/usr/bin/env python3
"""Synthetic process provider used only to test the SUI transport boundary."""

from __future__ import annotations

import json
import sys
import time


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "valid"
    if mode == "sleep":
        time.sleep(10)
        return 0
    if mode == "fail":
        print("synthetic provider failure", file=sys.stderr)
        return 7
    if mode == "invalid-json":
        sys.stdout.write("not-json")
        return 0

    request = json.load(sys.stdin)
    anchors = set(request["anchorRefs"])
    candidates = sorted(
        item["ref"] for item in request["items"] if item["ref"] not in anchors
    )[: request["policy"]["candidateLimit"]]

    response = {
        "schema": "sui.associative-recall-response/v1alpha1",
        "requestId": request["requestId"],
        "provider": {
            "providerId": "synthetic-process-provider",
            "implementationVersion": "test-v1",
        },
        "outcome": "candidates" if candidates else "abstain",
        "candidateRefs": candidates,
        "evidence": [
            {"ref": ref, "matchedChannelRefs": []} for ref in candidates
        ],
        "noveltyCue": "none" if candidates else "abstain",
    }
    if mode == "contract-invalid":
        response["score"] = 0.99
    if mode == "duplicate-key":
        encoded = json.dumps(response, ensure_ascii=False, separators=(",", ":"))
        sys.stdout.write(encoded[:-1] + ',"outcome":"candidates"}')
        return 0

    json.dump(response, sys.stdout, ensure_ascii=False, separators=(",", ":"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
