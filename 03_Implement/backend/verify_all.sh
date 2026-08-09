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
# 7. Docs check
# ------------------------------------------------------------------
check "Documentation contract checks" \
  $VENV_PYTHON "$(git rev-parse --show-toplevel 2>/dev/null || echo '/mnt/d/GIT/kj-atlas')/01_Plans/docs_check.py"

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
