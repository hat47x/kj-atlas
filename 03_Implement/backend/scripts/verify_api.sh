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

# 1b. /readyz — unauthenticated readiness (DB reachable + schema at migration head).
# A 503 with reason database_unavailable / schema_mismatch is the correct
# non-200; anything else (e.g. a 500) is a server crash.
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/readyz")
case "$code" in
  200)
    echo "  PASS: /readyz ready"
    PASS=$((PASS+1))
    ;;
  503)
    echo "  INFO: /readyz returned 503 (DB unavailable or schema mismatch) —"
    echo "        expected when the DB is stopped or migrations are not applied."
    ;;
  *)
    echo "  FAIL: /readyz returned $code (expected 200 or 503)"
    FAIL=$((FAIL+1))
    ;;
esac

# 1c. /version — build revision (OPS-OBSERV-01). Unauthenticated.
code=$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/version")
check "/version" "200" "$code"

# 2. /ai/provider-status — read-only provider echo
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/ai/provider-status")
check "/ai/provider-status" "200" "$code"

# 3. /docs — list the tenant's document metadata (第2反復 canvas-list foundation).
#    Row metadata only (never card content). 200 with a JSON array.
code=$(curl -s -o /tmp/kj_docs_list.json -w '%{http_code}' ${auth_header} "$BASE_URL/docs")
check "/docs (list)" "200" "$code"
if [ "$code" = "200" ]; then
  if head -c1 /tmp/kj_docs_list.json | grep -q '^\['; then
    echo "  PASS: /docs returns a JSON array"
    PASS=$((PASS+1))
  else
    echo "  FAIL: /docs did not return a JSON array"
    FAIL=$((FAIL+1))
  fi
fi

# 3b. /docs/{id} — read a document (sample fixture id)
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/docs/doc_phase1_canvas")
# 404 is acceptable (document may not be seeded); non-5xx means route works
if [ "$code" != "500" ] && [ "$code" != "503" ]; then
  echo "  PASS: /docs/{id} route reachable (HTTP $code)"
  PASS=$((PASS+1))
else
  echo "  FAIL: /docs/{id} returned $code"
  FAIL=$((FAIL+1))
fi

# 4. /session/context — session context (may require auth).
# DOGFOOD-04: do NOT treat every non-500 as "reachable". A 503 means the
# endpoint is present but Service Unavailable (e.g. local-dev has no SaaS
# identity resolver and returns 503 by design). Report status classes
# distinctly so a real outage is not masked as reachable.
code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} "$BASE_URL/session/context")
case "$code" in
  500)
    echo "  FAIL: /session/context returned 500 (server crash)"
    FAIL=$((FAIL+1))
    ;;
  503)
    echo "  INFO: /session/context returned 503 (Service Unavailable) —"
    echo "        expected in local-dev (no SaaS identity resolver); NOT counted as reachable."
    ;;
  2*|3*|404)
    check "/session/context reachable" "reachable" "reachable"
    ;;
  *)
    echo "  FAIL: /session/context returned $code (unexpected)"
    FAIL=$((FAIL+1))
    ;;
esac

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
