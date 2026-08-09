/**
 * ADR-0064: JWT access token storage.
 *
 * Stores the JWT access token in sessionStorage (cleared when the
 * browser tab closes). The token is attached to API requests via the
 * X-Kj-Atlas-Authorization header.
 */

const ACCESS_TOKEN_KEY = "kj_atlas_access_token";
const REFRESH_TOKEN_KEY = "kj_atlas_refresh_token";

export interface TokenSet {
  accessToken: string;
  refreshToken?: string;
}

/** Store tokens from a successful OAuth token exchange. */
export function storeTokens(tokens: TokenSet): void {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, tokens.accessToken);
  if (tokens.refreshToken) {
    sessionStorage.setItem(REFRESH_TOKEN_KEY, tokens.refreshToken);
  }
}

/** Retrieve the stored access token, or null if not authenticated. */
export function getAccessToken(): string | null {
  return sessionStorage.getItem(ACCESS_TOKEN_KEY);
}

/** Retrieve the stored refresh token. */
export function getRefreshToken(): string | null {
  return sessionStorage.getItem(REFRESH_TOKEN_KEY);
}

/** Clear all stored tokens (logout). */
export function clearTokens(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
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
