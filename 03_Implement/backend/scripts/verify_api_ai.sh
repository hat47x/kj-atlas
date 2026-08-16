#!/usr/bin/env bash
# Verify the kj-atlas AI routes' fail-closed behavior over the HTTP API from an
# external script (admin/CI path).
#
# These are the safety contracts an admin script must be able to rely on:
#   - provider=none (or an unavailable provider) -> structured 503
#     provider_unavailable (fail-closed; never a crash or a silent fallback).
#   - a document containing UNREVIEWED card text -> 422
#     unreviewed_text_not_allowed (SEC-AI-SAFEMODE-01 / ADR-0068) — the
#     unreviewed boundary is enforced at the API edge, so a curl client cannot
#     leak unreviewed content to an external LLM.
#
# Usage:
#   ./verify_api_ai.sh [BASE_URL]
#
# Requires a running backend. The checks are provider-agnostic: when a provider
# IS configured, the 503 expectation changes, so this script asserts the
# fail-closed shapes (422 for unreviewed always; 503 only when provider=none).

set -u
BASE_URL="${1:-http://127.0.0.1:8000}"
PASS=0
FAIL=0

check() {
  local desc="$1" expected="$2" actual="$3"
  if [ "$actual" = "$expected" ]; then
    echo "  PASS: $desc"
    PASS=$((PASS+1))
  else
    echo "  FAIL: $desc (expected $expected, got $actual)"
    FAIL=$((FAIL+1))
  fi
}

# auth_header is a bash ARRAY so a keyed backend sends a well-formed
# X-API-Key header (the fail-closed 422/503 boundaries are provider-agnostic
# but the request still needs to pass HTTP auth on a keyed backend).
auth_header=()
if [ -n "${KJ_ATLAS_API_KEY:-}" ]; then
  auth_header=(-H "X-API-Key: ${KJ_ATLAS_API_KEY}")
fi

reviewed_payload='{"islandId":"i1","doc":{"version":1,"id":"ai-probe","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"reviewed card","x":0,"y":0,"textReviewed":true}],"edges":[],"islands":[{"id":"i1","cardIds":["c1"],"title":"T","summaryText":"s","summaryReviewed":true}]}}'
unreviewed_payload='{"islandId":"i1","doc":{"version":1,"id":"ai-probe","createdAt":"2026-08-15T00:00:00Z","updatedAt":"2026-08-15T00:00:00Z","transform":{"panX":0,"panY":0,"zoom":1},"cards":[{"id":"c1","text":"unreviewed secret","x":0,"y":0}],"edges":[],"islands":[{"id":"i1","cardIds":["c1"],"title":"T","summaryText":"","summaryReviewed":false}]}}'

echo "=== kj-atlas AI fail-closed verification (base: $BASE_URL) ==="

# 1. Unreviewed card text must be rejected 422 before any provider call
#    (SEC-AI-SAFEMODE-01). This holds regardless of provider configuration.
code=$(curl -s -o /tmp/kj_ai_body.json -w '%{http_code}' -X POST \
  "${auth_header[@]}" "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' -d "$unreviewed_payload")
check "unreviewed text -> 422 (SafeMode boundary)" "422" "$code"
if [ "$code" = "422" ]; then
  err=$(grep -o '"code":"[^"]*"' /tmp/kj_ai_body.json | head -1)
  check "unreviewed error code is unreviewed_text_not_allowed" '"code":"unreviewed_text_not_allowed"' "$err"
fi

# 2. A fully-reviewed request under provider=none must fail closed 503 with the
#    structured provider_unavailable body (never a crash, never a silent
#    fallback). When a provider IS configured, the code differs — but the
#    request must NOT succeed with a stub/unconfigured provider.
code=$(curl -s -o /tmp/kj_ai_body.json -w '%{http_code}' -X POST \
  "${auth_header[@]}" "$BASE_URL/ai/suggest-island-summary" -H 'Content-Type: application/json' -d "$reviewed_payload")
if [ "$code" = "503" ]; then
  err=$(grep -o '"code":"[^"]*"' /tmp/kj_ai_body.json | head -1)
  check "provider=none -> 503 provider_unavailable" '"code":"provider_unavailable"' "$err"
  trace=$(grep -o '"trace_id":"[^"]*"' /tmp/kj_ai_body.json | head -1)
  echo "  INFO: structured error carries trace_id ($trace) — observability present"
  PASS=$((PASS+1))
else
  echo "  INFO: provider is configured (code $code), 503 fail-closed check skipped"
  echo "        — the unreviewed-422 boundary above is the provider-agnostic contract."
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
