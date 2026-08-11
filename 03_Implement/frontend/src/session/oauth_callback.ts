/**
 * ADR-0064: OAuth 2.0 callback handler.
 *
 * Called early in the app lifecycle to detect and handle the redirect
 * from the identity broker's authorization endpoint. The broker appends
 * `?code=...&state=...` to the redirect URI after successful login.
 *
 * This module validates the state parameter (CSRF protection), exchanges
 * the authorization code for tokens at the broker's token endpoint,
 * stores the tokens, and cleans up the URL.
 */

import { storeTokens } from "./token_store";

// ---------------------------------------------------------------------------
// Storage keys (must match oauth_login.ts)
// ---------------------------------------------------------------------------

const PKCE_VERIFIER_KEY = "kj_atlas_pkce_verifier";
const OAUTH_STATE_KEY = "kj_atlas_oauth_state";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

function resolveBrokerBaseUrl(): string {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const env = (import.meta as any).env as Record<string, string> | undefined;
  return env?.KJ_ATLAS_BROKER_BASE_URL?.trim() || "http://localhost:18081";
}

// ---------------------------------------------------------------------------
// Callback handler
// ---------------------------------------------------------------------------

/**
 * Result of processing an OAuth callback.
 */
export interface OAuthCallbackResult {
  /** True if a callback was detected and processed. */
  handled: boolean;
  /** Error message if the callback failed. */
  error?: string;
}

/**
 * Check for and process an OAuth 2.0 authorization callback.
 *
 * If the current URL contains `code` and `state` parameters from a
 * broker redirect, this function validates the state, exchanges the
 * code for tokens, and stores them. The URL is cleaned up afterward.
 *
 * Must be called before any other app initialization that depends
 * on authentication state.
 */
export async function handleOAuthCallback(): Promise<OAuthCallbackResult> {
  const params = new URLSearchParams(window.location.search);
  const code = params.get("code");
  const state = params.get("state");

  // No OAuth callback parameters — normal app flow.
  if (!code || !state) {
    return { handled: false };
  }

  // Validate state parameter (CSRF protection).
  const storedState = sessionStorage.getItem(OAUTH_STATE_KEY);
  sessionStorage.removeItem(OAUTH_STATE_KEY);
  if (state !== storedState) {
    return { handled: true, error: "oauth_state_mismatch" };
  }

  // Retrieve PKCE verifier.
  const codeVerifier = sessionStorage.getItem(PKCE_VERIFIER_KEY);
  sessionStorage.removeItem(PKCE_VERIFIER_KEY);
  if (!codeVerifier) {
    return { handled: true, error: "oauth_missing_pkce_verifier" };
  }

  // Exchange code for tokens at the broker's token endpoint.
  const brokerBase = resolveBrokerBaseUrl();
  const redirectUri = `${window.location.origin}${window.location.pathname}`;

  try {
    const response = await fetch(`${brokerBase}/oauth/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        redirect_uri: redirectUri,
        client_id: "mock-client",
        code_verifier: codeVerifier,
      }),
    });

    if (!response.ok) {
      return { handled: true, error: `oauth_token_error_${response.status}` };
    }

    const data: unknown = await response.json();
    const tokenData = data as Record<string, unknown>;

    // The authorization code is single-use but still must not remain in the
    // address bar or browser history after the broker accepted it.
    const cleanUrl = `${window.location.origin}${window.location.pathname}`;
    window.history.replaceState(null, "", cleanUrl);

    if (typeof tokenData.access_token !== "string") {
      return { handled: true, error: "oauth_invalid_token_response" };
    }

    if ("refresh_token" in tokenData) {
      return { handled: true, error: "oauth_refresh_token_not_allowed" };
    }

    storeTokens({
      accessToken: tokenData.access_token as string,
    });

    return { handled: true };
  } catch {
    return { handled: true, error: "oauth_network_error" };
  }
}
