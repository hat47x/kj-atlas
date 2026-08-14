#!/usr/bin/env bash
# kj-atlas comprehensive verification script.
# Runs: lint → unit tests → integration tests → doc checks
# Exit code: 0 = all passed, 1 = at least one check failed.
set -uo pipefail
cd "$(dirname "$0")"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'
PASS="${GREEN}PASS${NC}"
FAIL="${RED}FAIL${NC}"
VENV_PYTHON=".venv/bin/python"

failures=0

check() {
  local label="$1"
  shift
  echo -n "[....] $label "
  if "$@" > /tmp/verify_check.log 2>&1; then
    echo -e "\r[$PASS] $label"
  else
    echo -e "\r[$FAIL] $label"
    echo "  --- output (last 5 lines) ---"
    tail -5 /tmp/verify_check.log | sed 's/^/  /'
    echo "  --- end ---"
    failures=$((failures + 1))
    return 1
  fi
}

echo "=== kj-atlas Comprehensive Verification ==="
echo ""

# ------------------------------------------------------------------
# 1. Python syntax
# ------------------------------------------------------------------
check "Python syntax (all source files)" \
  bash -c "find src/kj_atlas_api -name '*.py' | while read f; do $VENV_PYTHON -c 'import py_compile; py_compile.compile(\"'\"\$f\"'\", doraise=True)' 2>/dev/null || exit 1; done"

# ------------------------------------------------------------------
# 2. Ruff lint (core auth files)
# ------------------------------------------------------------------
check "Ruff lint (auth modules)" \
  $VENV_PYTHON -m ruff check \
    src/kj_atlas_api/trusted_auth_edge.py \
    src/kj_atlas_api/active_tenant_session.py \
    src/kj_atlas_api/auth_context.py \
    src/kj_atlas_api/tenant_context.py \
    src/kj_atlas_api/saas_request_context.py \
    src/kj_atlas_api/settings.py \
    src/kj_atlas_api/main.py \
    src/kj_atlas_api/routes/admin.py

# ------------------------------------------------------------------
# 3. Unit tests (auth core)
# ------------------------------------------------------------------
check "Unit tests (auth core: JWT, JWKS, tenant, session)" \
  $VENV_PYTHON -m pytest tests/test_trusted_auth_edge.py \
    tests/test_jwks_store.py \
    tests/test_claim_tenant_resolver.py \
    tests/test_active_tenant_session_persister.py \
    tests/test_trusted_saas_runtime.py \
    tests/test_verified_tenant_context.py \
    tests/test_tenant_context_resolution.py \
    tests/test_auth_context_resolution.py \
    -q

# ------------------------------------------------------------------
# 4. Integration tests (E2E auth)
# ------------------------------------------------------------------
check "Integration tests (E2E tenant isolation + OAuth login + coordinated)" \
  $VENV_PYTHON -m pytest tests/test_saas_e2e_tenant_isolation.py \
    tests/test_saas_oauth_login_e2e.py \
    tests/test_saml_broker_jwt_coordinated_flow.py \
    -q

# ------------------------------------------------------------------
# 5. Admin API tests
# ------------------------------------------------------------------
check "Admin API tests (IdP registration + policy)" \
  $VENV_PYTHON -m pytest tests/test_admin_identity_provider_registration.py -q

# ------------------------------------------------------------------
# 6. Federation + settings
# ------------------------------------------------------------------
check "Federation + settings + session tests" \
  $VENV_PYTHON -m pytest tests/test_auth_federation_level2.py \
    tests/test_settings_env_prefix_migration.py \
    tests/test_session_context.py \
    tests/test_session_context_routes.py \
    tests/test_tenant_session_precondition.py \
    -q

# ------------------------------------------------------------------
# 7. LLM tests (mock integration)
# ------------------------------------------------------------------
check "LLM integration tests (mock — all 6 AI tasks)" \
  $VENV_PYTHON -m pytest tests/test_llm_provider.py \
    tests/test_llm_settings.py \
    tests/test_ai_prompt.py \
    tests/test_ai_provider_error_contract.py \
    tests/test_ai_provider_status_route.py \
    tests/test_ai_relations_route.py \
    tests/test_llm_integration.py \
    -m "not ollama" -q

# ------------------------------------------------------------------
# 8. Docs check
# ------------------------------------------------------------------
check "Documentation contract checks" \
  $VENV_PYTHON "$(git rev-parse --show-toplevel 2>/dev/null || echo '/mnt/d/GIT/kj-atlas')/01_Plans/docs_check.py"

# ------------------------------------------------------------------
# 9. API/MCP verification (non-Web paths; requires a running backend)
# ------------------------------------------------------------------
# These curl/tsx-based checks exercise the admin CLI/API and MCP paths an
# operator actually uses. They need a live backend (uvicorn on :8000), so
# they are skipped with a note when it is not reachable — never a failure.
ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null || echo '/mnt/d/GIT/kj-atlas')"
API_BASE="${KJ_ATLAS_VERIFY_API_BASE:-http://127.0.0.1:8000}"
if curl -s -o /dev/null -w '%{http_code}' --max-time 2 "$API_BASE/healthz" 2>/dev/null | grep -q 200; then
  check "API read path (verify_api.sh)" \
    bash "$ROOT_DIR/03_Implement/backend/scripts/verify_api.sh" "$API_BASE"
  check "API write path (verify_api_write.sh)" \
    bash "$ROOT_DIR/03_Implement/backend/scripts/verify_api_write.sh" "$API_BASE"
  check "API inquiry CAS path (verify_api_inquiry.sh)" \
    bash "$ROOT_DIR/03_Implement/backend/scripts/verify_api_inquiry.sh" "$API_BASE"
  # MCP client path (generative-AI verification). Requires the mcp package's
  # tsx runtime; a missing/empty doc reports not_found (exit 0, valid signal).
  if [ -x "$ROOT_DIR/03_Implement/mcp/node_modules/.bin/tsx" ]; then
    check "MCP client path (verify_mcp.ts)" \
      bash -c "cd '$ROOT_DIR/03_Implement/mcp' && KJ_ATLAS_MCP_API_BASE_URL='$API_BASE' npm run verify -- ${KJ_ATLAS_MCP_VERIFY_DOC:-doc_phase1_canvas} reviewed-only"
  else
    echo "  SKIP: MCP client path — mcp package deps not installed (cd 03_Implement/mcp && npm install)"
  fi
else
  echo "  SKIP: API/MCP verification — no backend at $API_BASE (start uvicorn kj_atlas_api.main:app --port 8000 to enable)"
fi

# ------------------------------------------------------------------
# Summary
# ------------------------------------------------------------------
echo ""
echo "=== Verification Summary ==="
if [ $failures -eq 0 ]; then
  echo -e "${GREEN}All checks passed.${NC}"
else
  echo -e "${RED}${failures} check(s) failed.${NC}"
  exit 1
fi
