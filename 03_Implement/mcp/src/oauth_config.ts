// EXT-CONN-01 subslice C (ADR-0054 stage 1, streamable-HTTP transport):
// kj-atlas-mcp acts as an OAuth 2.1 *resource server* only. It never issues
// tokens, registers clients, or runs an authorization endpoint -- it validates
// bearer tokens issued by an external, already-trusted authorization server
// (e.g. the same IdP kj-atlas's own app auth delegates to, ADR-0020). This
// config intentionally has no fields for client secrets, signing keys, or
// token issuance: that surface does not exist in this process.

export type HttpTransportConfig = {
  host: string;
  port: number;
  /** This server's own resource identifier (RFC 8707). Must equal the `aud` tokens are issued for. */
  resource: string;
  /** Exact issuer string tokens must present in `iss`. No wildcard/prefix matching. */
  trustedIssuer: string;
  /** JWKS endpoint of the trusted issuer, used to verify token signatures. */
  jwksUri: string;
  /** Advertised in /.well-known/oauth-protected-resource; not itself trusted for anything. */
  authorizationServers: string[];
};

export class HttpTransportConfigError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "HttpTransportConfigError";
  }
}

function requireEnv(env: NodeJS.ProcessEnv, key: string): string {
  const value = env[key]?.trim();
  if (!value) {
    throw new HttpTransportConfigError(
      `${key} is required when KJ_ATLAS_MCP_TRANSPORT=http (resource-server mode has no safe default issuer/audience).`
    );
  }
  return value;
}

/**
 * Loads and validates the streamable-HTTP transport's OAuth resource-server
 * config. Fails closed: any missing required value throws rather than
 * falling back to an unauthenticated or wildcard-trusting default.
 */
export function loadHttpTransportConfigFromEnv(env: NodeJS.ProcessEnv = process.env): HttpTransportConfig {
  const host = env.KJ_ATLAS_MCP_HTTP_HOST?.trim() || "127.0.0.1";
  const rawPort = env.KJ_ATLAS_MCP_HTTP_PORT?.trim() || "8787";
  const port = Number.parseInt(rawPort, 10);
  if (!Number.isInteger(port) || port <= 0 || port > 65535) {
    throw new HttpTransportConfigError(`KJ_ATLAS_MCP_HTTP_PORT must be a valid port number, got: ${rawPort}`);
  }

  const resource = requireEnv(env, "KJ_ATLAS_MCP_RESOURCE_URL");
  const trustedIssuer = requireEnv(env, "KJ_ATLAS_MCP_TRUSTED_ISSUER");
  const jwksUri = requireEnv(env, "KJ_ATLAS_MCP_JWKS_URI");

  const rawAuthServers = env.KJ_ATLAS_MCP_AUTHORIZATION_SERVERS?.trim();
  const authorizationServers = rawAuthServers ? rawAuthServers.split(",").map((value) => value.trim()).filter(Boolean) : [trustedIssuer];

  return { host, port, resource, trustedIssuer, jwksUri, authorizationServers };
}
