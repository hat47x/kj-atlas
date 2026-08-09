#!/usr/bin/env bash
# ADR-0064: Automated Keycloak setup for kj-atlas SaaS authentication.
#
# Usage:
#   docker compose -f docker-compose.yml -f broker/docker-compose.yml up -d
#   bash setup_keycloak.sh
#
# Creates: kj-atlas realm, backend client, tenant_ref mapper, test users.
set -euo pipefail

KEYCLOAK_BASE="${KEYCLOAK_BASE:-http://localhost:18080}"
ADMIN_USER="${KEYCLOAK_ADMIN:-admin}"
ADMIN_PASS="${KEYCLOAK_ADMIN_PASSWORD:-admin}"
REALM="kj-atlas"
CLIENT_ID="kj-atlas-backend"
CLIENT_SECRET="kj-atlas-backend-secret"

# ------------------------------------------------------------------
# Step 1: Get admin token
# ------------------------------------------------------------------
echo "1. Authenticating as admin..."
ADMIN_TOKEN=$(curl -s -X POST "${KEYCLOAK_BASE}/realms/master/protocol/openid-connect/token" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" \
  -d "username=${ADMIN_USER}" \
  -d "password=${ADMIN_PASS}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")

echo "   Token obtained."

# ------------------------------------------------------------------
# Step 2: Create realm
# ------------------------------------------------------------------
echo "2. Creating realm '${REALM}'..."
curl -s -X POST "${KEYCLOAK_BASE}/admin/realms" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"realm\": \"${REALM}\",
    \"enabled\": true,
    \"loginWithEmailAllowed\": false,
    \"duplicateEmailsAllowed\": false,
    \"defaultSignatureAlgorithm\": \"RS256\",
    \"accessTokenLifespan\": 3600,
    \"ssoSessionIdleTimeout\": 3600
  }" > /dev/null
echo "   Realm created."

# ------------------------------------------------------------------
# Step 3: Create OIDC client (confidential, PKCE)
# ------------------------------------------------------------------
echo "3. Creating client '${CLIENT_ID}'..."
curl -s -X POST "${KEYCLOAK_BASE}/admin/realms/${REALM}/clients" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"clientId\": \"${CLIENT_ID}\",
    \"secret\": \"${CLIENT_SECRET}\",
    \"enabled\": true,
    \"publicClient\": false,
    \"standardFlowEnabled\": true,
    \"directAccessGrantsEnabled\": false,
    \"redirectUris\": [\"http://localhost:5173/*\"],
    \"webOrigins\": [\"http://localhost:5173\"],
    \"protocol\": \"openid-connect\",
    \"attributes\": {
      \"pkce.code.challenge.method\": \"S256\"
    }
  }" > /dev/null
echo "   Client created."

# ------------------------------------------------------------------
# Step 4: Add tenant_ref claim mapper
# ------------------------------------------------------------------
echo "4. Adding tenant_ref claim mapper..."
CLIENT_UUID=$(curl -s "${KEYCLOAK_BASE}/admin/realms/${REALM}/clients?clientId=${CLIENT_ID}" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" | python3 -c "import json,sys; print(json.load(sys.stdin)[0]['id'])")

curl -s -X POST "${KEYCLOAK_BASE}/admin/realms/${REALM}/clients/${CLIENT_UUID}/protocol-mappers/models" \
  -H "Authorization: Bearer ${ADMIN_TOKEN}" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"tenant_ref\",
    \"protocol\": \"openid-connect\",
    \"protocolMapper\": \"oidc-usermodel-attribute-mapper\",
    \"config\": {
      \"user.attribute\": \"tenant_ref\",
      \"claim.name\": \"tenant_ref\",
      \"access.token.claim\": \"true\",
      \"id.token.claim\": \"true\",
      \"userinfo.token.claim\": \"true\",
      \"jsonType.label\": \"String\"
    }
  }" > /dev/null
echo "   Mapper created."

# ------------------------------------------------------------------
# Step 5: Create test users
# ------------------------------------------------------------------
echo "5. Creating test users..."
for USER in alice bob; do
  curl -s -X POST "${KEYCLOAK_BASE}/admin/realms/${REALM}/users" \
    -H "Authorization: Bearer ${ADMIN_TOKEN}" \
    -H "Content-Type: application/json" \
    -d "{
      \"username\": \"${USER}\",
      \"email\": \"${USER}@example.com\",
      \"enabled\": true,
      \"credentials\": [{\"type\": \"password\", \"value\": \"password\", \"temporary\": false}],
      \"attributes\": {
        \"tenant_ref\": [\"org-123\"]
      }
    }" > /dev/null
  echo "   User '${USER}' created (tenant_ref=org-123)."
done

echo ""
echo "=== Setup complete ==="
echo "Realm:      ${REALM}"
echo "Client ID:  ${CLIENT_ID}"
echo "Users:      alice / bob (password: password, tenant_ref: org-123)"
echo ""
echo "OIDC Discovery: ${KEYCLOAK_BASE}/realms/${REALM}/.well-known/openid-configuration"
echo "JWKS:           ${KEYCLOAK_BASE}/realms/${REALM}/protocol/openid-connect/certs"
echo ""
echo "Next: Register the broker in kj-atlas:"
echo "  curl -X POST http://localhost:18000/admin/provision/identity-providers \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"issuer\":\"${KEYCLOAK_BASE}/realms/${REALM}\",\"audience\":\"${CLIENT_ID}\",\"protocol\":\"oidc\",\"jwksUri\":\"${KEYCLOAK_BASE}/realms/${REALM}/protocol/openid-connect/certs\"}'"
