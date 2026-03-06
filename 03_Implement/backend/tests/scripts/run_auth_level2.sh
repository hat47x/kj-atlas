#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="${ROOT_DIR}/.artifacts/auth-level2"
mkdir -p "${LOG_DIR}"

BACKEND_PORT="${AUTH_LEVEL2_BACKEND_PORT:-18000}"
SP_PORT="${AUTH_LEVEL2_SP_PORT:-18080}"
IDP_PORT="${AUTH_LEVEL2_IDP_PORT:-18081}"

export PYTHONPATH="${ROOT_DIR}/src:${ROOT_DIR}"
export KJ_ATLAS_DATABASE_URL="${KJ_ATLAS_DATABASE_URL:-sqlite:///${ROOT_DIR}/.artifacts/auth-level2/auth_level2.sqlite3}"
export KJ_ATLAS_ALLOW_JIT_PROVISIONING="${KJ_ATLAS_ALLOW_JIT_PROVISIONING:-true}"
export KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR="${KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR:-${ROOT_DIR}/tests/federation/profiles}"
export AUTH_PROVIDER_PROFILE_DIR="${KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR}"
export BACKEND_BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
export MOCK_IDP_BASE_URL="http://127.0.0.1:${IDP_PORT}"
export AUTH_LEVEL2_SP_BASE_URL="http://127.0.0.1:${SP_PORT}"

alembic upgrade head >"${LOG_DIR}/alembic.log" 2>&1

cleanup() {
  for pid in "${SP_PID:-}" "${IDP_PID:-}" "${BACKEND_PID:-}"; do
    if [[ -n "${pid}" ]] && kill -0 "${pid}" >/dev/null 2>&1; then
      kill "${pid}" >/dev/null 2>&1 || true
      wait "${pid}" 2>/dev/null || true
    fi
  done
}
trap cleanup EXIT

uvicorn kj_atlas_api.main:app --port "${BACKEND_PORT}" >"${LOG_DIR}/backend.log" 2>&1 &
BACKEND_PID=$!
uvicorn tests.federation.mock_idp:app --port "${IDP_PORT}" >"${LOG_DIR}/mock-idp.log" 2>&1 &
IDP_PID=$!
uvicorn tests.federation.mock_sp:app --port "${SP_PORT}" >"${LOG_DIR}/mock-sp.log" 2>&1 &
SP_PID=$!

python - <<'PY'
import os
import time
import httpx

urls = [
    f"http://127.0.0.1:{os.environ['AUTH_LEVEL2_BACKEND_PORT'] if 'AUTH_LEVEL2_BACKEND_PORT' in os.environ else '18000'}/healthz",
    f"http://127.0.0.1:{os.environ['AUTH_LEVEL2_IDP_PORT'] if 'AUTH_LEVEL2_IDP_PORT' in os.environ else '18081'}/healthz",
    f"http://127.0.0.1:{os.environ['AUTH_LEVEL2_SP_PORT'] if 'AUTH_LEVEL2_SP_PORT' in os.environ else '18080'}/healthz",
]

for url in urls:
    ready = False
    for _ in range(40):
        try:
            res = httpx.get(url, timeout=2.0)
            if res.status_code == 200:
                ready = True
                break
        except Exception:
            time.sleep(0.25)
    if not ready:
        raise SystemExit(f"service not ready: {url}")
PY

pytest -m auth_level2 tests/test_auth_provider_profile_fixture.py | tee "${LOG_DIR}/pytest-auth-level2.log"
