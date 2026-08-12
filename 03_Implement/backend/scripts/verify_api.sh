#!/usr/bin/env bash
# Verify kj-atlas HTTP API endpoints from an external script (admin/CI path).
#
# This is the "administrator writes their own script to use the CLI/API"
# verification path — a plain curl-based client independent of the frontend.
#
# Usage:
#   ./verify_api.sh [BASE_URL]     # default http://127.0.0.1:8000
#
# Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000).
# For local single-tenant dev, no API key is required. If KJ_ATLAS_API_KEY
# is set, pass it via KJ_ATLAS_API_KEY env.

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

auth_header=""
if [ -n "${KJ_ATLAS_API_KEY:-}" ]; then
  auth_header="-H 'X-API-Key: ${KJ_ATLAS_API_KEY}'"
fi

echo "=== kj-atlas API verification (base: $BASE_URL) ==="

# 1. /healthz — unauthenticated liveness
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/healthz")
check "/healthz" "200" "$code"

# 2. /ai/provider-status — read-only provider echo
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/ai/provider-status")
check "/ai/provider-status" "200" "$code"

# 3. /docs/{id} — read a document (sample fixture id)
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/docs/doc_phase1_canvas")
# 404 is acceptable (document may not be seeded); non-5xx means route works
if [ "$code" != "500" ] && [ "$code" != "503" ]; then
  echo "  PASS: /docs/{id} route reachable (HTTP $code)"
  PASS=$((PASS+1))
else
  echo "  FAIL: /docs/{id} returned $code"
  FAIL=$((FAIL+1))
fi

# 4. /session/context — session context (may require auth)
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/session/context")
check "/session/context reachable (non-500)" "reachable" "$([ "$code" = "500" ] && echo fail || echo reachable)"

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
