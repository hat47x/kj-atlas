#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
export KJ_ATLAS_LEVEL2_DIAG_DIR="${KJ_ATLAS_LEVEL2_DIAG_DIR:-$BACKEND_DIR/.artifacts/auth-level2/legacy-federation}"

mkdir -p "$KJ_ATLAS_LEVEL2_DIAG_DIR"

"$BACKEND_DIR/tests/scripts/run_auth_level2.sh"

echo "Level2 diagnostics: $KJ_ATLAS_LEVEL2_DIAG_DIR"
