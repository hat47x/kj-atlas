#!/usr/bin/env bash
# Verify a REALISTIC W-type inquiry journey round-trips through the inquiry-bundle
# API (business-domain coverage: DOMAIN-W-ITERATION-01 G5).
#
# The CAS lifecycle is covered by verify_api_inquiry.sh; this script uses a
# representative InquiryBundleV1 (journey + multiple rounds + handoffs +
# fieldwork requests, mirroring createRepresentativeInquiryBundle) and asserts
# the full structure survives the opaque payload round-trip.
#
# Usage:
#   ./verify_api_inquiry_journey.sh [BASE_URL] [JOURNEY_ID]
#
# Requires a running backend. The probe journey is deleted at the end.

set -u
BASE_URL="${1:-http://127.0.0.1:8000}"
JOURNEY_ID="${2:-verify_inquiry_journey_$(date +%s)}"
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

# Representative W-type bundle: a journey with two rounds (R2 situation-grasp,
# R3 essence-pursuit), each with a handoff carrying unresolved questions and a
# fieldwork request. Mirrors inquiry_journey.fixture.ts's structure.
payload='{
  "schemaVersion": "1.0.0",
  "journey": {
    "schemaVersion": "1.0.0",
    "journeyId": "'"${JOURNEY_ID}"'",
    "title": "窓口対応の待ち時間を捉え直す",
    "originSnapshotIds": ["snapshot-origin"],
    "roundRecords": [
      {
        "roundId": "round-r2-1",
        "createdAt": "2026-08-14T00:00:00.000Z",
        "updatedAt": "2026-08-14T00:00:00.000Z",
        "stage": "r2_situation_grasp",
        "iteration": 1,
        "parentRoundIds": [],
        "status": "handed_off",
        "theme": "来庁者が待っている間に実際に何が起きているか",
        "inputSnapshotIds": ["snapshot-origin"],
        "outputSnapshotId": "snapshot-r2-1",
        "handoff": {
          "carryoverRefs": [{"snapshotId": "snapshot-r2-1", "kind": "card", "entityId": "observation-1"}],
          "heldRefs": [],
          "unresolvedQuestions": ["案内表示を読んだか"],
          "fieldworkRequests": [{"fieldworkRequestId": "fw-1", "question": "案内表示の注視状況を観察する"}]
        }
      },
      {
        "roundId": "round-r3-1",
        "createdAt": "2026-08-14T00:00:00.000Z",
        "updatedAt": "2026-08-14T00:00:00.000Z",
        "stage": "r3_essence_pursuit",
        "iteration": 2,
        "parentRoundIds": ["round-r2-1"],
        "status": "in_progress",
        "theme": "負担の正体を捉える",
        "inputSnapshotIds": ["snapshot-r2-1"],
        "outputSnapshotId": "snapshot-r3-1",
        "handoff": {
          "carryoverRefs": [{"snapshotId": "snapshot-r3-1", "kind": "card", "entityId": "hypothesis-1"}],
          "heldRefs": [],
          "unresolvedQuestions": [],
          "fieldworkRequests": []
        }
      }
    ]
  },
  "snapshots": [
    {"schemaVersion": "1.0.0", "snapshotId": "snapshot-origin", "createdAt": "2026-08-14T00:00:00.000Z", "canonicalDigest": "sha256:origin", "document": {"version": 1, "id": "doc-origin", "createdAt": "2026-08-14T00:00:00.000Z", "updatedAt": "2026-08-14T00:00:00.000Z", "transform": {"panX": 0, "panY": 0, "zoom": 1}, "cards": [{"id": "observation-1", "text": "observation", "x": 40, "y": 60}], "edges": [], "islands": []}}
  ]
}'

echo "=== kj-atlas W-type inquiry journey verification (base: $BASE_URL, journey: $JOURNEY_ID) ==="

# 1. Create with If-None-Match: * → 201 + ETag "1"
resp=$(curl -s -D /tmp/kj_journey_headers.txt -o /tmp/kj_journey_body.json -w '%{http_code}' \
  "${auth_header[@]}" -X POST "$BASE_URL/inquiry-bundles/$JOURNEY_ID" \
  -H 'Content-Type: application/json' -H 'If-None-Match: *' -d "$payload")
check "create (If-None-Match: *) returns 201" "201" "$resp"
etag=$(grep -i '^etag:' /tmp/kj_journey_headers.txt | tr -d '\r' | awk '{print $2}')
check "create returns ETag \"1\"" "\"1\"" "$etag"

# 2. Read back — verify the FULL journey structure survives the opaque round-trip.
resp=$(curl -s -o /tmp/kj_journey_get.json -w '%{http_code}' "${auth_header[@]}" \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID")
check "read-back returns 200" "200" "$resp"
if [ "$resp" = "200" ]; then
  title=$(grep -o '"title":"[^"]*"' /tmp/kj_journey_get.json | head -1)
  check "journey title round-trips" '"title":"窓口対応の待ち時間を捉え直す"' "$title"
  round_count=$(grep -o '"roundId":"[^"]*"' /tmp/kj_journey_get.json | wc -l | tr -d ' ')
  check "round count round-trips (2 rounds)" "2" "$round_count"
  stage_r2=$(grep -o '"stage":"[^"]*"' /tmp/kj_journey_get.json | head -1)
  check "R2 stage survives" '"stage":"r2_situation_grasp"' "$stage_r2"
  fw_question=$(grep -o '"question":"[^"]*"' /tmp/kj_journey_get.json | head -1)
  check "fieldwork question survives" '"question":"案内表示の注視状況を観察する"' "$fw_question"
  unresolved=$(grep -o '"unresolvedQuestions":\[[^]]*\]' /tmp/kj_journey_get.json | head -1)
  check "unresolved question survives" '"unresolvedQuestions":["案内表示を読んだか"]' "$unresolved"
fi

# 3. Update with If-Match "1" → 204 (advance a round, prove edit round-trips).
updated_payload='{
  "schemaVersion": "1.0.0",
  "journey": {
    "schemaVersion": "1.0.0",
    "journeyId": "'"${JOURNEY_ID}"'",
    "title": "窓口対応の待ち時間を捉え直す（更新）",
    "originSnapshotIds": ["snapshot-origin"],
    "roundRecords": [
      {"roundId": "round-r2-1", "createdAt": "2026-08-14T00:00:00.000Z", "updatedAt": "2026-08-14T00:00:00.000Z", "stage": "r2_situation_grasp", "iteration": 1, "parentRoundIds": [], "status": "handed_off", "theme": "来庁者が待っている間に実際に何が起きているか", "inputSnapshotIds": ["snapshot-origin"], "outputSnapshotId": "snapshot-r2-1", "handoff": {"carryoverRefs": [{"snapshotId": "snapshot-r2-1", "kind": "card", "entityId": "observation-1"}], "heldRefs": [], "unresolvedQuestions": ["案内表示を読んだか"], "fieldworkRequests": [{"fieldworkRequestId": "fw-1", "question": "案内表示の注視状況を観察する"}]}},
      {"roundId": "round-r3-1", "createdAt": "2026-08-14T00:00:00.000Z", "updatedAt": "2026-08-14T00:00:00.000Z", "stage": "r3_essence_pursuit", "iteration": 2, "parentRoundIds": ["round-r2-1"], "status": "handed_off", "theme": "負担の正体を捉える", "inputSnapshotIds": ["snapshot-r2-1"], "outputSnapshotId": "snapshot-r3-1", "handoff": {"carryoverRefs": [{"snapshotId": "snapshot-r3-1", "kind": "card", "entityId": "hypothesis-1"}], "heldRefs": [], "unresolvedQuestions": [], "fieldworkRequests": []}},
      {"roundId": "round-r4-1", "createdAt": "2026-08-14T00:00:00.000Z", "updatedAt": "2026-08-14T00:00:00.000Z", "stage": "r4_construction", "iteration": 3, "parentRoundIds": ["round-r3-1"], "status": "in_progress", "theme": "構想を形にする", "inputSnapshotIds": ["snapshot-r3-1"], "outputSnapshotId": "snapshot-r4-1", "handoff": {"carryoverRefs": [], "heldRefs": [], "unresolvedQuestions": [], "fieldworkRequests": []}}
    ]
  },
  "snapshots": []
}'
resp=$(curl -s -D /tmp/kj_journey_headers2.txt -o /dev/null -w '%{http_code}' \
  "${auth_header[@]}" -X POST "$BASE_URL/inquiry-bundles/$JOURNEY_ID" \
  -H 'Content-Type: application/json' -H 'If-Match: "1"' -d "$updated_payload")
check "update (If-Match: \"1\") returns 204" "204" "$resp"
etag2=$(grep -i '^etag:' /tmp/kj_journey_headers2.txt | tr -d '\r' | awk '{print $2}')
check "update returns ETag \"2\"" "\"2\"" "$etag2"

# 4. Read back — R4 round added.
resp=$(curl -s -o /tmp/kj_journey_get2.json -w '%{http_code}' "${auth_header[@]}" \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID")
check "read-back after update returns 200" "200" "$resp"
if [ "$resp" = "200" ]; then
  round_count2=$(grep -o '"roundId":"[^"]*"' /tmp/kj_journey_get2.json | wc -l | tr -d ' ')
  check "round count advanced (3 rounds)" "3" "$round_count2"
  stage_r4=$(grep -o '"stage":"[^"]*"' /tmp/kj_journey_get2.json | tail -1)
  check "R4 stage survives" '"stage":"r4_construction"' "$stage_r4"
fi

# 5. Delete with the current revision → 204.
resp=$(curl -s -o /dev/null -w '%{http_code}' "${auth_header[@]}" -X DELETE \
  "$BASE_URL/inquiry-bundles/$JOURNEY_ID" -H 'If-Match: "2"')
check "delete (If-Match: \"2\") returns 204" "204" "$resp"

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
