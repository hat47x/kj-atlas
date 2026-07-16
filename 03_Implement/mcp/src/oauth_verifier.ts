import { createRemoteJWKSet, jwtVerify, errors as joseErrors, type JWTVerifyGetKey } from "jose";
import { InvalidTokenError } from "@modelcontextprotocol/sdk/server/auth/errors.js";
import type { OAuthTokenVerifier } from "@modelcontextprotocol/sdk/server/auth/provider.js";
import type { AuthInfo } from "@modelcontextprotocol/sdk/server/auth/types.js";

// EXT-CONN-01 subslice C: the entire trust boundary for the HTTP transport
// lives here. `jwtVerify` enforces signature, `iss`, `aud`, and expiry against
// the *trusted issuer's* JWKS -- there is no path that accepts an unsigned or
// wrongly-issued token. Any verification failure becomes InvalidTokenError so
// bearerAuth.ts's middleware answers 401 (not 500, which would happen for an
// uncaught generic Error -- see @modelcontextprotocol/sdk's requireBearerAuth).

export type BearerTokenVerifierConfig = {
  trustedIssuer: string;
  resource: string;
};

/**
 * Builds the OAuthTokenVerifier the streamable-HTTP transport's bearer-auth
 * middleware calls on every request. `getKey` defaults to a remote JWKS
 * fetch (production); tests inject a local JWKS via `createLocalJWKSet` so
 * they never depend on network access or a running mock IdP process.
 */
export function createBearerTokenVerifier(config: BearerTokenVerifierConfig, getKey: JWTVerifyGetKey): OAuthTokenVerifier {
  return {
    async verifyAccessToken(token: string): Promise<AuthInfo> {
      let payload;
      try {
        ({ payload } = await jwtVerify(token, getKey, {
          issuer: config.trustedIssuer,
          audience: config.resource,
        }));
      } catch (error) {
        // Fail closed on every jose failure mode (bad signature, wrong
        // issuer/audience, expired, malformed, key-fetch failure, ...):
        // reject the request, never fall through to "treat as valid."
        const reason = error instanceof joseErrors.JOSEError ? error.code : "verification_failed";
        throw new InvalidTokenError(`Access token rejected: ${reason}`);
      }

      if (typeof payload.exp !== "number") {
        // bearerAuth.ts's middleware itself requires a numeric expiresAt and
        // rejects otherwise, but failing closed here keeps that invariant
        // local to the one place that actually reads the JWT claims.
        throw new InvalidTokenError("Access token has no exp claim");
      }

      // Prefer an explicit client_id claim (RFC 8693/DCR convention), then
      // OIDC's azp (authorized party), then sub -- covers the external IdPs
      // this resource server has no control over the token shape of.
      const clientId = [payload.client_id, payload.azp, payload.sub].find(
        (value): value is string => typeof value === "string" && value.length > 0
      );
      if (!clientId) {
        throw new InvalidTokenError("Access token has no client_id, azp, or sub claim");
      }

      const scope = payload.scope;
      const scopes = typeof scope === "string" ? scope.split(" ").filter(Boolean) : [];

      return {
        token,
        clientId,
        scopes,
        expiresAt: payload.exp,
        resource: new URL(config.resource),
      };
    },
  };
}

export function createRemoteBearerTokenVerifier(config: BearerTokenVerifierConfig & { jwksUri: string }): OAuthTokenVerifier {
  return createBearerTokenVerifier(config, createRemoteJWKSet(new URL(config.jwksUri)));
}
