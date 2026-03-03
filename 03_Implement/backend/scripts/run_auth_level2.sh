#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
DIAG_DIR="${LEVEL2_DIAG_DIR:-$BACKEND_DIR/.tmp/level2-diagnostics}"

mkdir -p "$DIAG_DIR"

cd "$BACKEND_DIR"
export PYTHONPATH=src

python -m pytest -m level2 tests/test_auth_federation_level2.py -vv

echo "Level2 diagnostics: $DIAG_DIR"
