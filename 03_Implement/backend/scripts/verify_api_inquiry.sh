#!/usr/bin/env bash
# Verify the kj-atlas inquiry-bundle CAS lifecycle over the HTTP API from an
# external script (admin/CI path, DATA-INQUIRY-CONCURRENCY-01 案A).
#
# This is the "administrator writes their own script to use the CLI/API"
# path for the W-type inquiry bundle store: a plain curl client exercises the
# full create -> read -> update -> conflict -> delete lifecycle including the
# precondition headers an optimistic-concurrency contract demands.
#
# Usage:
#   ./verify_api_inquiry.sh [BASE_URL] [JOURNEY_ID]
#     BASE_URL   default http://127.0.0.1:8000
#     JOURNEY_ID default verify_inquiry_probe_<timestamp>
#
# Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000).
# The probe journey is deleted at the end (DELETE with the final revision), so
# reruns are idempotent as long as a fresh JOURNEY_ID is supplied.
# If KJ_ATLAS_API_KEY is set, it is passed via X-API-Key.
#
# DOGFOOD-06 rule: success cases AND abnormal cases are both asserted, so a
# future change that weakens the CAS contract (missing precondition accepted,
# stale write overwrites, malformed If-Match tolerated) fails here.

set -u
BASE_URL="${1:-http://127.0.0.1:8000}"
JOURNEY_ID="${2:-verify_inquiry_probe_$(date +%s)}"
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

auth_header=()
if [ -n "${KJ_ATLAS_API_KEY:-}" ]; then
  auth_header=(-H "X-API-Key: ${KJ_ATLAS_API_KEY}")
fi

# Opaque InquiryBundleV1 payload (any JSON value is legal for the backend).
payload='{"title":"verify inquiry probe","rounds":[{"id":"r1","label":"first"}]}'
updated_payload='{"title":"verify inquiry probe (updated)","rounds":[{"id":"r1","label":"first"},{"id":"r2","label":"second"}]}'

echo "=== kj-atlas inquiry-bundle CAS verification (base: $BASE_URL, journey: $JOURNEY_ID) ==="

# --- create -------------------------------------------------------------
# 1. If-None-Match: *  → 201 + ETag "1"
resp=$(curl -s -D /tmp/kj_inq_headers.txt -o /tmp/kj_inq_body.json -w '%{http_code}' \
  "${auth_header[@]}" -X POST "$BASE_URL/inquiry-bundles/$JOURNEY_ID" \
  -H 'Content-Type: application/json' -H 'If-None-Match: *' -d "$payload")
check "create (If-None-Match: *) returns 201" "201" "$resp"
etag=$(grep -i '^etag:' /tmp/kj_inq_headers.txt | tr -d '\r' | awk '{print $2}')
check "create returns ETag \"1\"" "\"1\"" "$etag"

# 2. Duplicate create with If-None-Match: *  → 409 (already exists, no overwrite)
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X POST \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'Content-Type: application/json' \
  -H 'If-None-Match: *' -d "$payload")
check "duplicate create returns 409 (no overwrite)" "409" "$resp"

# --- read ---------------------------------------------------------------
# 3. GET → 200 + ETag "1" + payload roundtrip
resp=$(curl -s -D /tmp/kj_inq_headers.txt -o /tmp/kj_inq_body.json -w '%{http_code}' \
  "${auth_header[@]}" "$BASE_URL/inquiry-bundles/$JOURNEY_ID")
check "read-back returns 200" "200" "$resp"
etag=$(grep -i '^etag:' /tmp/kj_inq_headers.txt | tr -d '\r' | awk '{print $2}')
check "read-back ETag is still \"1\"" "\"1\"" "$etag"
roundtrip=$(grep -o '"title":"verify inquiry probe"' /tmp/kj_inq_body.json | head -1)
check "payload roundtrips" "\"title\":\"verify inquiry probe\"" "$roundtrip"

# --- update -------------------------------------------------------------
# 4. If-Match: "1"  → 204 + ETag "2" (atomic rev 1 → 2)
resp=$(curl -s -D /tmp/kj_inq_headers.txt -o /dev/null -w '%{http_code}' \
  "${auth_header[@]}" -X POST "$BASE_URL/inquiry-bundles/$JOURNEY_ID" \
  -H 'Content-Type: application/json' -H 'If-Match: "1"' -d "$updated_payload")
check "update (If-Match: \"1\") returns 204" "204" "$resp"
etag=$(grep -i '^etag:' /tmp/kj_inq_headers.txt | tr -d '\r' | awk '{print $2}')
check "update returns ETag \"2\"" "\"2\"" "$etag"

# 5. Stale update with the OLD revision  → 409 (revision mismatch, nothing changed)
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X POST \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'Content-Type: application/json' \
  -H 'If-Match: "1"' -d "$updated_payload")
check "stale update (If-Match: \"1\") returns 409" "409" "$resp"

# 6. Update without any precondition  → 428
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X POST \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'Content-Type: application/json' -d "$updated_payload")
check "update without precondition returns 428" "428" "$resp"

# 7. Malformed If-Match (wildcard)  → 422
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X POST \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'Content-Type: application/json' \
  -H 'If-Match: *' -d "$updated_payload")
check "malformed If-Match (wildcard) returns 422" "422" "$resp"

# 8. GET after update → 200 + ETag "2" + updated payload
resp=$(curl -s -D /tmp/kj_inq_headers.txt -o /tmp/kj_inq_body.json -w '%{http_code}' \
  "${auth_header[@]}" "$BASE_URL/inquiry-bundles/$JOURNEY_ID")
check "read-back after update returns 200" "200" "$resp"
etag=$(grep -i '^etag:' /tmp/kj_inq_headers.txt | tr -d '\r' | awk '{print $2}')
check "read-back ETag advanced to \"2\"" "\"2\"" "$etag"
roundtrip=$(grep -o '"title":"verify inquiry probe (updated)"' /tmp/kj_inq_body.json | head -1)
check "updated payload roundtrips" "\"title\":\"verify inquiry probe (updated)\"" "$roundtrip"

# --- delete -------------------------------------------------------------
# 9. Delete with the CURRENT revision  → 204
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X DELETE \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'If-Match: "2"')
check "delete (If-Match: \"2\") returns 204" "204" "$resp"

# 10. GET after delete  → 404
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID")
check "read-back after delete returns 404" "404" "$resp"

# 11. Delete again with the same revision  → 409 (row already gone)
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X DELETE \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'If-Match: "2"')
check "re-delete returns 409 (row missing)" "409" "$resp"

# 12. Size bound: a payload over the 20 MiB ceiling is refused with 413
#     (inquiry_bundle_too_large), matching api.md — discovered via dogfooding
#     that the documented 5 MiB was stale vs the enforced 20 MiB.
if command -v python3 >/dev/null 2>&1; then
  BIG_FILE="$(mktemp /tmp/kj_inquiry_big_XXXXXX.json)"
  python3 -c "import json,sys; json.dump({'big':'a'*21000000}, open(sys.argv[1],'w'))" "$BIG_FILE"
  big_code=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" \
    -X POST "$BASE_URL/inquiry-bundles/verify-inquiry-too-big" \
    -H 'Content-Type: application/json' -H 'If-None-Match: *' --data-binary @"$BIG_FILE")
  rm -f "$BIG_FILE"
  check "payload >20MiB refused (413 inquiry_bundle_too_large)" "413" "$big_code"
else
  echo "  SKIP: size-bound check — python3 not available"
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
