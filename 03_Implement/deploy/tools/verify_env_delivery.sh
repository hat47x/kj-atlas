#!/usr/bin/env bash
# ENV-COMPOSE-01 Phase 2: functional probe for the two base-Compose
# pass-through keys (KJ_ATLAS_API_KEY, KJ_ATLAS_ALLOW_JIT_PROVISIONING).
#
# Local, Docker-capable-host verification only -- this script is not run in
# CI (it starts real containers and takes several minutes). It never prints
# a configured secret value; only pass/fail and HTTP status codes.
#
# Usage: bash 03_Implement/deploy/tools/verify_env_delivery.sh
# Run from anywhere; paths below are relative to this script's location.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
COMPOSE_FILE="${DEPLOY_DIR}/docker-compose.yml"
BASE_URL="http://localhost:8080"
PROBE_DOC_ID_PREFIX="probe-env-delivery"
FAILED=0

log() {
  echo "[verify_env_delivery] $1"
}

fail() {
  echo "[verify_env_delivery] FAIL: $1"
  FAILED=1
}

compose() {
  docker compose -f "${COMPOSE_FILE}" "$@"
}

wait_for_healthy() {
  local attempt=0
  local max_attempts=60
  while [ "${attempt}" -lt "${max_attempts}" ]; do
    if curl -fsS "${BASE_URL}/api/healthz" >/dev/null 2>&1; then
      return 0
    fi
    attempt=$((attempt + 1))
    sleep 2
  done
  return 1
}

put_probe_doc() {
  local doc_id="$1"
  shift
  local extra_headers=("$@")
  local payload
  payload=$(cat <<JSON
{
  "version": 1,
  "id": "${doc_id}",
  "title": "env delivery probe",
  "createdAt": "2026-01-01T00:00:00.000Z",
  "updatedAt": "2026-01-01T00:00:00.000Z",
  "transform": {"panX": 0, "panY": 0, "zoom": 1},
  "cards": [],
  "edges": [],
  "islands": [],
  "readingOrder": [],
  "narratives": [],
  "evidenceLinks": [],
  "mergeSuggestionDecisions": []
}
JSON
  )
  curl -s -o /dev/null -w '%{http_code}' -X PUT "${BASE_URL}/api/docs/${doc_id}" \
    -H 'Content-Type: application/json' \
    "${extra_headers[@]}" \
    --data "${payload}"
}

cleanup() {
  log "tearing down (docker compose down)"
  compose down >/dev/null 2>&1 || true
}
trap cleanup EXIT

# --- P-1: API key protection -------------------------------------------
log "P-1: starting stack with KJ_ATLAS_API_KEY set (value not shown)"
KJ_ATLAS_API_KEY="probe-local-key-$$" compose up -d --build >/dev/null 2>&1

if ! wait_for_healthy; then
  fail "P-1: stack did not become healthy"
else
  status_no_key=$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/api/docs/${PROBE_DOC_ID_PREFIX}-p1")
  if [ "${status_no_key}" = "401" ]; then
    log "P-1a: no key -> 401 (pass)"
  else
    fail "P-1a: expected 401 without X-API-Key, got ${status_no_key}"
  fi

  status_with_key=$(curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: probe-local-key-$$" "${BASE_URL}/api/docs/${PROBE_DOC_ID_PREFIX}-p1")
  if [ "${status_with_key}" != "401" ]; then
    log "P-1b: correct key -> ${status_with_key}, not 401 (pass, middleware passed the request through)"
  else
    fail "P-1b: expected non-401 with the correct X-API-Key, got 401"
  fi

  status_healthz=$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/api/healthz")
  if [ "${status_healthz}" = "200" ]; then
    log "P-1c: /healthz stays unprotected -> 200 (pass)"
  else
    fail "P-1c: expected /healthz to stay 200 without a key, got ${status_healthz}"
  fi
fi

compose down >/dev/null 2>&1

# --- P-2: JIT provisioning denial ---------------------------------------
log "P-2: starting stack with KJ_ATLAS_ALLOW_JIT_PROVISIONING=false"
KJ_ATLAS_ALLOW_JIT_PROVISIONING=false compose up -d --build >/dev/null 2>&1

if ! wait_for_healthy; then
  fail "P-2: stack did not become healthy"
else
  status_jit=$(put_probe_doc "${PROBE_DOC_ID_PREFIX}-p2" -H "x-forwarded-user: verify-env-delivery-probe" -H "x-auth-provider: oidc")
  if [ "${status_jit}" = "403" ]; then
    log "P-2: unregistered identity denied -> 403 (pass)"
  else
    fail "P-2: expected 403 for an unregistered identity with JIT disabled, got ${status_jit}"
  fi
fi

compose down >/dev/null 2>&1

# --- P-3: default preserved when unset ----------------------------------
log "P-3: starting stack with both keys unset (implementation default)"
unset KJ_ATLAS_API_KEY KJ_ATLAS_ALLOW_JIT_PROVISIONING
compose up -d --build >/dev/null 2>&1

if ! wait_for_healthy; then
  fail "P-3: stack did not become healthy"
else
  status_default=$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/api/docs/${PROBE_DOC_ID_PREFIX}-p3")
  if [ "${status_default}" != "401" ]; then
    log "P-3: no KJ_ATLAS_API_KEY set anywhere -> ${status_default}, not 401 (pass, protection stays off by default)"
  else
    fail "P-3: expected the unset-by-default state to NOT require a key, got 401"
  fi
fi

compose down >/dev/null 2>&1

if [ "${FAILED}" -ne 0 ]; then
  log "one or more probes failed"
  exit 1
fi

log "all probes passed"
exit 0
