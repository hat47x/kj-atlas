/**
 * ADR-0064: JWT access token storage.
 *
 * Holds the short-lived JWT access token in module memory only. Reloading the
 * page deliberately requires authentication again. Refresh tokens are never
 * accepted or persisted by the application.
 */

export interface TokenSet {
  accessToken: string;
}

let accessToken: string | null = null;

/** Store tokens from a successful OAuth token exchange. */
export function storeTokens(tokens: TokenSet): void {
  accessToken = tokens.accessToken;
}

/** Retrieve the stored access token, or null if not authenticated. */
export function getAccessToken(): string | null {
  return accessToken;
}

/** Clear all stored tokens (logout). */
export function clearTokens(): void {
  accessToken = null;
}

/** Build the Authorization header value for API requests. */
export function authorizationHeader(): Record<string, string> {
  const token = getAccessToken();
  if (!token) {
    return {};
  }
  return { "X-Kj-Atlas-Authorization": `Bearer ${token}` };
}

/** True if the user has a stored access token. */
export function isAuthenticated(): boolean {
  return getAccessToken() !== null;
}
