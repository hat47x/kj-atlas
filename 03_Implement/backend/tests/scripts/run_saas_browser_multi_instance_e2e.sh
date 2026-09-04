#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "${SCRIPT_DIR}/../.." && pwd)"
REPO_ROOT="$(cd "${BACKEND_DIR}/../.." && pwd)"
FRONTEND_DIR="${REPO_ROOT}/03_Implement/frontend"
LOG_DIR="${RUNNER_TEMP:-/tmp}/kj-atlas-saas-browser-e2e"
mkdir -p "${LOG_DIR}"

: "${KJ_ATLAS_DATABASE_URL:?KJ_ATLAS_DATABASE_URL is required}"

BROWSER_BASE_URL=http://localhost:4173
BROKER_BROWSER_BASE_URL=http://localhost:9100
BROKER_BACKCHANNEL_BASE_URL=http://127.0.0.1:9100
POLICY_BASE_URL=http://127.0.0.1:9200

export KJ_ATLAS_RUNTIME_PROFILE=saas-multitenant
export KJ_ATLAS_ADMIN_API_KEY=e2e-admin-key
export KJ_ATLAS_ALLOW_JIT_PROVISIONING=false
export KJ_ATLAS_ACCESS_CONTROL_ADAPTER=external_http
export KJ_ATLAS_ACCESS_CONTROL_FAIL_SAFE_MODE=deny
export KJ_ATLAS_ACCESS_CONTROL_EXTERNAL_HTTP_ENDPOINT="${POLICY_BASE_URL}/access-control"
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_RESOLVER=external_http
export KJ_ATLAS_DOCUMENT_POLICY_BINDING_HTTP_ENDPOINT="${POLICY_BASE_URL}/document-policy"
export KJ_ATLAS_TENANT_CAPABILITY_RESOLVER=external_http
export KJ_ATLAS_TENANT_CAPABILITY_HTTP_ENDPOINT="${POLICY_BASE_URL}/capabilities"
export KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_AUTHORIZE_ENDPOINT="${BROKER_BROWSER_BASE_URL}/oauth/authorize"
export KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_TOKEN_ENDPOINT="${BROKER_BACKCHANNEL_BASE_URL}/oauth/token"
export KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_REDIRECT_URI="${BROWSER_BASE_URL}/session/callback"
export KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_ID=mock-client
export KJ_ATLAS_SAAS_OAUTH_BROKER_HTTP_CLIENT_SECRET=e2e-secret
export KJ_ATLAS_SAAS_AUTH_SESSION_HASH_KEY=0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef
export KJ_ATLAS_JWT_ALGORITHMS=RS256
export KJ_ATLAS_TENANT_CLAIM_NAME=tenant_ref
export KJ_ATLAS_LLM_PROVIDER=none
export KJ_ATLAS_MOCK_IDP_BASE="${BROKER_BROWSER_BASE_URL}"
export KJ_ATLAS_FRONTEND_API_BASE=/api
export KJ_ATLAS_E2E_WORKER_1=http://127.0.0.1:8001
export KJ_ATLAS_E2E_WORKER_2=http://127.0.0.1:8002

pids=()
cleanup() {
  status=$?
  for pid in "${pids[@]:-}"; do
    kill "${pid}" 2>/dev/null || true
  done
  wait 2>/dev/null || true
  if [[ ${status} -ne 0 ]]; then
    echo "--- SaaS browser E2E service logs ---"
    for log in "${LOG_DIR}"/*.log; do
      [[ -e "${log}" ]] || continue
      echo "### ${log}"
      tail -n 120 "${log}" || true
    done
  fi
  exit "${status}"
}
trap cleanup EXIT

wait_http() {
  local url="$1"
  for _ in $(seq 1 120); do
    if curl --fail --silent --show-error "${url}" >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.25
  done
  echo "service did not become ready: ${url}" >&2
  return 1
}

cd "${BACKEND_DIR}"
python -m alembic upgrade head
python -m tests.e2e_support.saas_browser_harness seed

python -m uvicorn tests.e2e_support.saas_browser_harness:policy_app --host 127.0.0.1 --port 9200 >"${LOG_DIR}/policy.log" 2>&1 & pids+=("$!")
python -m uvicorn tests.e2e_support.real_http_mock_idp:app --host 127.0.0.1 --port 9100 >"${LOG_DIR}/broker.log" 2>&1 & pids+=("$!")
wait_http "${POLICY_BASE_URL}/healthz"
wait_http "${BROKER_BACKCHANNEL_BASE_URL}/healthz"

python -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8001 >"${LOG_DIR}/worker1.log" 2>&1 & pids+=("$!")
python -m uvicorn kj_atlas_api.main:app --host 127.0.0.1 --port 8002 >"${LOG_DIR}/worker2.log" 2>&1 & pids+=("$!")
wait_http http://127.0.0.1:8001/readyz
wait_http http://127.0.0.1:8002/readyz

python -m uvicorn tests.e2e_support.saas_browser_harness:gateway_app --host 127.0.0.1 --port 8000 >"${LOG_DIR}/gateway.log" 2>&1 & pids+=("$!")
wait_http http://127.0.0.1:8000/healthz

cd "${FRONTEND_DIR}"
npm run dev -- --host localhost --port 4173 --strictPort >"${LOG_DIR}/frontend.log" 2>&1 & pids+=("$!")
wait_http "${BROWSER_BASE_URL}/"

npx playwright test --config=playwright.saas-multi-instance.config.ts
