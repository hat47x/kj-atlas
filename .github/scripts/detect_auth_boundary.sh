#!/usr/bin/env bash
set -euo pipefail

base_ref="${1:-}"
head_ref="${2:-HEAD}"

if [[ -z "$base_ref" ]]; then
  echo "false"
  exit 0
fi

changed_files="$(git diff --name-only "$base_ref" "$head_ref")"
if [[ -z "$changed_files" ]]; then
  echo "false"
  exit 0
fi

pattern='^(03_Implement/backend/src/kj_atlas_api/(auth_context\.py|settings\.py|access_control\.py|routes/docs\.py)|03_Implement/backend/tests/test_auth_.*\.py|03_Implement/backend/tests/fixtures/provider_profile_.*\.json|03_Implement/backend/tests/level2/.*|01_Plans/adr/ADR-0020-oidc-saml-mock-idp-sp-profile\.md|04_Documentation/e2e_testing\.md)$'

if printf '%s\n' "$changed_files" | rg -q "$pattern"; then
  echo "true"
else
  echo "false"
fi
