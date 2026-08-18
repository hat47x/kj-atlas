#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
LOG_DIR="${ROOT_DIR}/.artifacts/auth-level2"
export KJ_ATLAS_LEVEL2_DIAG_DIR="${KJ_ATLAS_LEVEL2_DIAG_DIR:-${LOG_DIR}/legacy-federation}"
rm -rf "${LOG_DIR}"
mkdir -p "${LOG_DIR}" "${KJ_ATLAS_LEVEL2_DIAG_DIR}"

# CI sets KJ_ATLAS_DATABASE_URL=sqlite:///./kj_atlas.db at the step level, so
# the default below never applies there -- the file this alembic upgrade
# actually targets is ./kj_atlas.db relative to this script's cwd
# (03_Implement/backend), not .artifacts/auth-level2/. That file is shared,
# by literal env value, with the two pytest steps that run immediately
# before this one in the same job. When it survives from an earlier step
# already migrated, alembic (seeing no/stale alembic_version bookkeeping in
# whatever created it) walks the chain from scratch and collides with
# tables/indexes that already exist. Delete whatever sqlite file this run's
# KJ_ATLAS_DATABASE_URL points at before touching it, so this step always
# starts from a state alembic has never seen, regardless of what an earlier
# step in the same job left behind.
_existing_database_url="${KJ_ATLAS_DATABASE_URL:-}"
if [[ "${_existing_database_url}" == sqlite:///* ]]; then
  _sqlite_path="${_existing_database_url#sqlite:///}"
  case "${_sqlite_path}" in
    /*) : ;;
    *) _sqlite_path="${ROOT_DIR}/${_sqlite_path}" ;;
  esac
  rm -f "${_sqlite_path}"
fi

export KJ_ATLAS_AUTH_LEVEL2_BACKEND_PORT="${KJ_ATLAS_AUTH_LEVEL2_BACKEND_PORT:-18000}"
export KJ_ATLAS_AUTH_LEVEL2_SP_PORT="${KJ_ATLAS_AUTH_LEVEL2_SP_PORT:-18080}"
export KJ_ATLAS_AUTH_LEVEL2_IDP_PORT="${KJ_ATLAS_AUTH_LEVEL2_IDP_PORT:-18081}"
BACKEND_PORT="${KJ_ATLAS_AUTH_LEVEL2_BACKEND_PORT}"
SP_PORT="${KJ_ATLAS_AUTH_LEVEL2_SP_PORT}"
IDP_PORT="${KJ_ATLAS_AUTH_LEVEL2_IDP_PORT}"

export PYTHONPATH="${ROOT_DIR}/src:${ROOT_DIR}"
export KJ_ATLAS_DATABASE_URL="${KJ_ATLAS_DATABASE_URL:-sqlite:///${ROOT_DIR}/.artifacts/auth-level2/auth_level2.sqlite3}"
export KJ_ATLAS_ALLOW_JIT_PROVISIONING="${KJ_ATLAS_ALLOW_JIT_PROVISIONING:-true}"
export KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR="${KJ_ATLAS_AUTH_PROVIDER_PROFILE_DIR:-${ROOT_DIR}/tests/federation/profiles}"
export KJ_ATLAS_AUTH_LEVEL2_BACKEND_BASE_URL="http://127.0.0.1:${BACKEND_PORT}"
export KJ_ATLAS_AUTH_LEVEL2_MOCK_IDP_BASE_URL="http://127.0.0.1:${IDP_PORT}"
export KJ_ATLAS_AUTH_LEVEL2_SP_BASE_URL="http://127.0.0.1:${SP_PORT}"

# CI may inject legacy key for unrelated jobs; ENV-ARCH-01 forbids legacy keys.
unset DATABASE_URL || true

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
    f"http://127.0.0.1:{os.environ['KJ_ATLAS_AUTH_LEVEL2_BACKEND_PORT']}/healthz",
    f"http://127.0.0.1:{os.environ['KJ_ATLAS_AUTH_LEVEL2_IDP_PORT']}/healthz",
    f"http://127.0.0.1:{os.environ['KJ_ATLAS_AUTH_LEVEL2_SP_PORT']}/healthz",
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

pytest -m auth_level2 \
  tests/test_auth_federation_level2.py \
  tests/test_auth_provider_profile_fixture.py \
  | tee "${LOG_DIR}/pytest-auth-level2.log"
