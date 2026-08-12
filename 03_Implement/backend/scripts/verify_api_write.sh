#!/usr/bin/env bash
# Verify the kj-atlas HTTP API WRITE path from an external script
# (admin/CI path). Companion to verify_api.sh (read-only): this exercises
# document creation via PUT /docs/{id} and the GET read-back roundtrip, so
# an administrator who writes their own script can rely on the full
# create → read cycle.
#
# Usage:
#   ./verify_api_write.sh [BASE_URL] [DOC_ID]
#     BASE_URL  default http://127.0.0.1:8000
#     DOC_ID    default admin_write_probe
#
# Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000).
# The probe document is created and left in place (idempotent PUT).
# If KJ_ATLAS_API_KEY is set, it is passed via X-API-Key.

set -u
BASE_URL="${1:-http://127.0.0.1:8000}"
DOC_ID="${2:-admin_write_probe}"
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

# Minimal DocumentV1 payload that passes the A1 contract (PUT returns 2xx).
# Card text is bounded by DOMAIN-CARD-TEXT-01 (2000 chars max).
payload="$(cat <<JSON
{
  "version": 1,
  "id": "${DOC_ID}",
  "title": "admin write probe",
  "createdAt": "2026-08-12T00:00:00Z",
  "updatedAt": "2026-08-12T00:00:00Z",
  "transform": {"panX": 0, "panY": 0, "zoom": 1},
  "cards": [
    {"id": "card-1", "text": "alpha", "x": 0, "y": 0},
    {"id": "card-2", "text": "beta", "x": 10, "y": 10}
  ],
  "edges": [],
  "islands": [{"id": "island-1", "cardIds": ["card-1", "card-2"]}]
}
JSON
)"

echo "=== kj-atlas API WRITE verification (base: $BASE_URL, doc: $DOC_ID) ==="

# 1. Create/overwrite the document via PUT /docs/{id}.
put_code=$(curl -s -o /tmp/kj_write_put.json -w '%{http_code}' ${auth_header} \
  -X PUT "$BASE_URL/docs/$DOC_ID" -H 'Content-Type: application/json' -d "$payload")
case "$put_code" in
  200|201)
    echo "  PASS: PUT /docs/{id} created/updated document (HTTP $put_code)"
    PASS=$((PASS+1))
    ;;
  *)
    echo "  FAIL: PUT /docs/{id} returned $put_code"
    FAIL=$((FAIL+1))
    ;;
esac

# 2. Read it back and verify the roundtrip (title + card count).
get_code=$(curl -s -o /tmp/kj_write_get.json -w '%{http_code}' ${auth_header} "$BASE_URL/docs/$DOC_ID")
check "GET /docs/{id} reads back document" "200" "$get_code"
if [ "$get_code" = "200" ]; then
  title=$(grep -o '"title":"[^"]*"' /tmp/kj_write_get.json | head -1)
  check "title roundtrips" "\"title\":\"admin write probe\"" "$title"
  card_count=$(grep -o '"id":"card-[0-9]*"' /tmp/kj_write_get.json | sort -u | wc -l | tr -d ' ')
  check "card count roundtrips (2 cards)" "2" "$card_count"
fi

# 3. Update the document (PUT again with modified content) and verify the
#    change is reflected on the next read — the full create→read→update→read
#    lifecycle an admin script depends on.
updated_payload="$(cat <<JSON
{
  "version": 1,
  "id": "${DOC_ID}",
  "title": "admin write probe (updated)",
  "createdAt": "2026-08-12T00:00:00Z",
  "updatedAt": "2026-08-12T00:00:01Z",
  "transform": {"panX": 5, "panY": 5, "zoom": 1},
  "cards": [
    {"id": "card-1", "text": "alpha", "x": 0, "y": 0},
    {"id": "card-2", "text": "beta", "x": 10, "y": 10},
    {"id": "card-3", "text": "gamma", "x": 20, "y": 20}
  ],
  "edges": [],
  "islands": [{"id": "island-1", "cardIds": ["card-1", "card-2", "card-3"]}]
}
JSON
)"
update_code=$(curl -s -o /dev/null -w '%{http_code}' ${auth_header} \
  -X PUT "$BASE_URL/docs/$DOC_ID" -H 'Content-Type: application/json' -d "$updated_payload")
check "PUT /docs/{id} updates document" "200" "$update_code"

get_code2=$(curl -s -o /tmp/kj_write_get2.json -w '%{http_code}' ${auth_header} "$BASE_URL/docs/$DOC_ID")
if [ "$get_code2" = "200" ]; then
  title2=$(grep -o '"title":"[^"]*"' /tmp/kj_write_get2.json | head -1)
  check "update reflected in title" "\"title\":\"admin write probe (updated)\"" "$title2"
  card_count2=$(grep -o '"id":"card-[0-9]*"' /tmp/kj_write_get2.json | sort -u | wc -l | tr -d ' ')
  check "update reflected in card count (3 cards)" "3" "$card_count2"
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
