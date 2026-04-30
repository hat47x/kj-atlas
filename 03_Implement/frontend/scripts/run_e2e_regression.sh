#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

SPEC_PATTERN="${1:-ce3_patch_workspace|auth_context_level1_smoke|i18n_locale_query_equivalence}"

echo "[e2e-regression] running playwright subset with pattern: ${SPEC_PATTERN}"
npx playwright test --grep "${SPEC_PATTERN}"
