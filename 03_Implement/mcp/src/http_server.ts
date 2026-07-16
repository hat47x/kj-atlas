import express, { type Express } from "express";
import rateLimit from "express-rate-limit";
import { StreamableHTTPServerTransport } from "@modelcontextprotocol/sdk/server/streamableHttp.js";
import { requireBearerAuth } from "@modelcontextprotocol/sdk/server/auth/middleware/bearerAuth.js";
import { metadataHandler } from "@modelcontextprotocol/sdk/server/auth/handlers/metadata.js";
import type { OAuthProtectedResourceMetadata } from "@modelcontextprotocol/sdk/shared/auth.js";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import type { HttpTransportConfig } from "./oauth_config.js";
import { createRemoteBearerTokenVerifier } from "./oauth_verifier.js";

// EXT-CONN-01 subslice C: read-only MCP over streamable HTTP, fronted by
// OAuth 2.1 resource-server auth. THREAT_MODEL.md §6 covers the public-facing
// analysis this file implements (auth, rate limiting, failure behavior).

const MCP_PATH = "/mcp";
const PROTECTED_RESOURCE_METADATA_PATH = "/.well-known/oauth-protected-resource";

/**
 * A conservative default: 60 req/min per client IP, applied to every route
 * including the metadata endpoint. There is exactly one tool behind this
 * server and no legitimate client needs a tighter loop than that; failing
 * closed toward "too slow" is preferable to leaving this open to abuse.
 */
const RATE_LIMIT_WINDOW_MS = 60_000;
const RATE_LIMIT_MAX_REQUESTS = 60;

export function buildHttpApp(config: HttpTransportConfig, server: McpServer): Express {
  const app = express();
  app.disable("x-powered-by");
  app.use(express.json({ limit: "1mb" }));

  const limiter = rateLimit({
    windowMs: RATE_LIMIT_WINDOW_MS,
    limit: RATE_LIMIT_MAX_REQUESTS,
    standardHeaders: true,
    legacyHeaders: false,
  });
  app.use(limiter);

  const resourceMetadataUrl = new URL(PROTECTED_RESOURCE_METADATA_PATH, config.resource).toString();

  const protectedResourceMetadata: OAuthProtectedResourceMetadata = {
    resource: config.resource,
    authorization_servers: config.authorizationServers,
    bearer_methods_supported: ["header"],
    // No score/rank/confidence/priority fields exist on this MCP server's
    // tool output (ADR-0041 CVI anti-scoring); nothing here echoes that
    // vocabulary into the discovery document either.
    resource_name: "kj-atlas read-only context projection",
  };
  // metadataHandler returns a Router (it restricts to GET/OPTIONS and adds
  // CORS internally) -- it must be mounted with app.use so Express strips
  // the mount path before the router's own "/" route is matched; app.get
  // would leave req.url unstripped and the router's route would never hit.
  app.use(PROTECTED_RESOURCE_METADATA_PATH, metadataHandler(protectedResourceMetadata));

  const verifier = createRemoteBearerTokenVerifier({
    trustedIssuer: config.trustedIssuer,
    resource: config.resource,
    jwksUri: config.jwksUri,
  });
  const requireAuth = requireBearerAuth({ verifier, resourceMetadataUrl });

  // Stateless mode (sessionIdGenerator: undefined): this server has exactly
  // one read-only, idempotent tool and holds no per-client state worth
  // paying session-fixation/session-storage risk to keep across requests.
  const transport = new StreamableHTTPServerTransport({ sessionIdGenerator: undefined });
  const connectPromise = server.connect(transport);

  app.post(MCP_PATH, requireAuth, async (req, res) => {
    await connectPromise;
    await transport.handleRequest(req, res, req.body);
  });

  // GET/DELETE are part of the streamable-HTTP spec (server-initiated
  // notifications, explicit session teardown) but this server never opens a
  // session to notify on or tear down -- still gated behind auth so an
  // unauthenticated caller learns nothing from the response shape either way.
  app.get(MCP_PATH, requireAuth, async (req, res) => {
    await transport.handleRequest(req, res);
  });
  app.delete(MCP_PATH, requireAuth, async (req, res) => {
    await transport.handleRequest(req, res);
  });

  return app;
}
