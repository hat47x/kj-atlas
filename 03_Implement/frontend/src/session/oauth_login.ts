/**
 * ADR-0064: OAuth 2.0 / OIDC login redirect with PKCE.
 *
 * Generates PKCE parameters and redirects the browser to the identity
 * broker's authorization endpoint. The broker handles the actual login
 * and returns an authorization code via redirect. The callback page
 * exchanges the code for a JWT and stores it for API requests.
 */

import { t } from "../i18n/translate";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

/** Build-time broker base URL. Falls back to the mock IdP in development. */
function resolveBrokerBaseUrl(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const env = (import.meta as any).env as Record<string, string> | undefined;
  return env?.KJ_ATLAS_BROKER_BASE_URL?.trim() || "http://localhost:18081";
}

/** OAuth 2.0 client ID registered with the broker. */
function resolveClientId(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const env = (import.meta as any).env as Record<string, string> | undefined;
  return env?.KJ_ATLAS_BROKER_CLIENT_ID?.trim() || "mock-client";
}

// ---------------------------------------------------------------------------
// PKCE (Proof Key for Code Exchange) — S256
// ---------------------------------------------------------------------------

function base64url(buffer: ArrayBuffer): string {
  const bytes = new Uint8Array(buffer);
  let binary = "";
  for (let i = 0; i < bytes.byteLength; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function generatePkce(): Promise<{
  codeVerifier: string;
  codeChallenge: string;
}> {
  const verifierBytes = new Uint8Array(32);
  crypto.getRandomValues(verifierBytes);
  const codeVerifier = base64url(verifierBytes.buffer);

  const encoder = new TextEncoder();
  const digest = await crypto.subtle.digest(
    "SHA-256",
    encoder.encode(codeVerifier),
  );
  const codeChallenge = base64url(digest);

  return { codeVerifier, codeChallenge };
}

function generateState(): string {
  const stateBytes = new Uint8Array(16);
  crypto.getRandomValues(stateBytes);
  return base64url(stateBytes.buffer);
}

// ---------------------------------------------------------------------------
// Storage keys
// ---------------------------------------------------------------------------

const PKCE_VERIFIER_KEY = "kj_atlas_pkce_verifier";
const OAUTH_STATE_KEY = "kj_atlas_oauth_state";

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Initiate the OAuth 2.0 authorization code grant flow with PKCE.
 *
 * Stores PKCE verifier and state in sessionStorage so the callback page
 * can verify them. Redirects the browser to the broker's authorization
 * endpoint.
 */
export async function redirectToBrokerLogin(): Promise<void> {
  const { codeVerifier, codeChallenge } = await generatePkce();
  const state = generateState();

  sessionStorage.setItem(PKCE_VERIFIER_KEY, codeVerifier);
  sessionStorage.setItem(OAUTH_STATE_KEY, state);

  const brokerBase = resolveBrokerBaseUrl();
  const clientId = resolveClientId();
  const redirectUri = `${window.location.origin}/oauth/callback`;

  const params = new URLSearchParams({
    response_type: "code",
    client_id: clientId,
    redirect_uri: redirectUri,
    scope: "openid",
    code_challenge: codeChallenge,
    code_challenge_method: "S256",
    state,
  });

  window.location.href = `${brokerBase}/oauth/authorize?${params.toString()}`;
}

/**
 * Label for the login button (i18n key).
 */
export function loginButtonLabel(): string {
  return t("tenant_session.bootstrap.login") || "Sign in";
}
