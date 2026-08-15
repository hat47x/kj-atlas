#!/usr/bin/env bash
# Verify the kj-atlas ADMIN plane (control-plane provisioning) over the HTTP
# API from an external script (admin/CI path, SEC-ADMIN-PLANE-01/02).
#
# This is the "administrator writes their own script to use the CLI/API" path
# for /admin/provision/*: a plain curl client exercises the control-plane auth
# boundary (X-Admin-Api-Key vs the business X-API-Key separation) and the
# a2a3-gate validation helper.
#
# Usage:
#   ./verify_api_admin.sh [BASE_URL]
#     BASE_URL  default http://127.0.0.1:8000
#
# Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000).
#
# Mode is detected by probing the a2a3-gate helper with no credential:
#   - 200  -> the admin plane is open (local-dev / evaluation, admin key
#             unconfigured). Only the success paths are verified.
#   - 401  -> the admin plane requires auth. If KJ_ATLAS_ADMIN_API_KEY is set
#             (and matches the backend), the full auth boundary is verified:
#             no key / wrong key / business key only -> 401, admin key -> success.
#             If the key is unset, the boundary cannot be verified and the
#             script reports an SKIP (exit 0) rather than guessing.
#
# DOGFOOD-06 rule: success cases AND abnormal cases are both asserted, so a
# future change that re-couples the control plane to the business key or leaves
# an /admin/provision/* route unprotected fails here.

set -u
BASE_URL="${1:-http://127.0.0.1:8000}"
PASS=0
FAIL=0
ADMIN_KEY="${KJ_ATLAS_ADMIN_API_KEY:-}"

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

gate_payload='{"freezeContractId":"HIL-RS-02-A1-CONTRACT-FREEZE-v1","schemaVersion":"1.0.0","overridePolicy":"human_dual_control_only","contractLinkLocked":true,"sharedResourceFreeze":true,"a1Status":"Done","pendingDecisionQueueCount":0,"hasUndefinedContractChangeRequest":false,"hasSafeModeRegressionRequest":false,"hasShareExportLeakageRelaxationRequest":false}'
gate_drift_payload='{"freezeContractId":"HIL-RS-02-A1-CONTRACT-FREEZE-v1","schemaVersion":"9.9.9","overridePolicy":"human_dual_control_only","contractLinkLocked":true,"sharedResourceFreeze":true,"a1Status":"Done","pendingDecisionQueueCount":0,"hasUndefinedContractChangeRequest":false,"hasSafeModeRegressionRequest":false,"hasShareExportLeakageRelaxationRequest":false}'

gate_code() {
  curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/hil-rs/a2a3-gate:validate" \
    -H 'Content-Type: application/json' "$@" -d "$gate_payload"
}
gate_drift_code() {
  curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/hil-rs/a2a3-gate:validate" \
    -H 'Content-Type: application/json' "$@" -d "$gate_drift_payload"
}

echo "=== kj-atlas ADMIN plane verification (base: $BASE_URL) ==="

# --- Mode detection ---------------------------------------------------------
probe=$(gate_code)
if [ "$probe" = "200" ]; then
  mode="open"
elif [ "$probe" = "401" ] || [ "$probe" = "403" ]; then
  if [ -z "$ADMIN_KEY" ]; then
    echo "  SKIP: admin plane requires auth but KJ_ATLAS_ADMIN_API_KEY is unset —"
    echo "        set it (and start the backend with it) to verify the boundary. (exit 0)"
    exit 0
  fi
  mode="auth"
else
  echo "  FAIL: cannot reach a2a3-gate:validate (unexpected probe $probe)"
  exit 1
fi
echo "  (mode: $mode)"

if [ "$mode" = "auth" ]; then
  # ---- Auth-boundary mode (admin key configured) ----
  # 1. Admin key succeeds on the gate.
  check "a2a3-gate with admin key -> 200" "200" "$(gate_code -H "X-Admin-Api-Key: $ADMIN_KEY")"

  # 2. Gate invariant drift -> 409 (authorized but the frozen contract drifts).
  code=$(gate_drift_code -H "X-Admin-Api-Key: $ADMIN_KEY")
  case "$code" in
    409|422)
      echo "  PASS: a2a3-gate drift -> $code (rejected)"
      PASS=$((PASS+1))
      ;;
    *)
      echo "  FAIL: a2a3-gate drift (expected 409/422, got $code)"
      FAIL=$((FAIL+1))
      ;;
  esac

  # 3. No credential -> 401.
  check "a2a3-gate without credential -> 401" "401" "$(gate_code)"

  # 4. Wrong admin key -> 401.
  check "a2a3-gate with wrong admin key -> 401" "401" "$(gate_code -H "X-Admin-Api-Key: wrong-key")"

  # 5. Business-plane key alone must NOT reach /admin/provision/* (separation).
  check "a2a3-gate with business key only -> 401" "401" "$(gate_code -H "X-API-Key: business-key")"

  # 6. provision/users with admin key -> 201/200 (create / idempotent re-provision).
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/users" \
    -H 'Content-Type: application/json' -H "X-Admin-Api-Key: $ADMIN_KEY" \
    -d '{"provider":"verify_admin","externalUid":"probe-admin-1","displayName":"Admin Probe"}')
  case "$code" in
    201|200)
      echo "  PASS: provision/users with admin key -> $code"
      PASS=$((PASS+1))
      ;;
    *)
      echo "  FAIL: provision/users with admin key (expected 201/200, got $code)"
      FAIL=$((FAIL+1))
      ;;
  esac

  # 7. provision/users with business key only -> 401 (separation).
  check "provision/users with business key only -> 401" "401" \
    "$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/users" \
      -H 'Content-Type: application/json' -H 'X-API-Key: business-key' \
      -d '{"provider":"verify_admin","externalUid":"probe-admin-x","displayName":"X"}')"

  # 8. provision/users without credential -> 401.
  check "provision/users without credential -> 401" "401" \
    "$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/users" \
      -H 'Content-Type: application/json' \
      -d '{"provider":"verify_admin","externalUid":"probe-admin-y"}')"

  # 9. SEC-ADMIN-PLANE-03: the control-plane audit trail recorded the
  #    provision/users operation (success + abnormal case).
  audit_code=$(curl -s -o /tmp/kj_admin_audit.json -w '%{http_code}' \
    "$BASE_URL/admin/provision/audit?limit=10" -H "X-Admin-Api-Key: $ADMIN_KEY")
  if [ "$audit_code" = "200" ]; then
    if grep -q '"route":"/admin/provision/users"' /tmp/kj_admin_audit.json; then
      echo "  PASS: audit trail records provision/users (200)"
      PASS=$((PASS+1))
    else
      echo "  FAIL: audit trail lacks the provision/users event"
      FAIL=$((FAIL+1))
    fi
  else
    echo "  FAIL: GET /admin/provision/audit (expected 200, got $audit_code)"
    FAIL=$((FAIL+1))
  fi
  check "audit trail with business key only -> 401" "401" \
    "$(curl -s -o /dev/null -w '%{http_code}' "$BASE_URL/admin/provision/audit" \
      -H 'X-API-Key: business-key')"
else
  # ---- Open mode (no admin key configured: local-dev / evaluation) ----
  check "a2a3-gate (open) -> 200" "200" "$(gate_code)"
  code=$(gate_drift_code)
  case "$code" in
    409|422)
      echo "  PASS: a2a3-gate drift (open) -> $code (rejected)"
      PASS=$((PASS+1))
      ;;
    *)
      echo "  FAIL: a2a3-gate drift (open) (expected 409/422, got $code)"
      FAIL=$((FAIL+1))
      ;;
  esac
  code=$(curl -s -o /dev/null -w '%{http_code}' -X POST "$BASE_URL/admin/provision/users" \
    -H 'Content-Type: application/json' \
    -d '{"provider":"verify_admin","externalUid":"probe-open-1","displayName":"Open Probe"}')
  case "$code" in
    201|200)
      echo "  PASS: provision/users (open) -> $code"
      PASS=$((PASS+1))
      ;;
    *)
      echo "  FAIL: provision/users (open) (expected 201/200, got $code)"
      FAIL=$((FAIL+1))
      ;;
  esac

  echo "  INFO: auth boundary (401/403) not asserted — admin plane is open."
  echo "        Set KJ_ATLAS_ADMIN_API_KEY and start the backend with it to lock in the separation."
fi

echo ""
echo "=== Result: $PASS passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ]
