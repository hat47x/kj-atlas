import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import type { AddressInfo } from "node:net";
import type { Server } from "node:http";
import { SignJWT, exportJWK, generateKeyPair, createLocalJWKSet, type JWTVerifyGetKey } from "jose";
import type { HttpTransportConfig } from "./oauth_config.js";

// Full-stack test of the auth boundary: a real Express app on an OS-assigned
// ephemeral localhost port, hit with real fetch() calls and real signed JWTs.
// createRemoteJWKSet (the one call in oauth_verifier.ts that would otherwise
// reach a real network IdP) is swapped for a local, in-test JWKS via a scoped
// `jose` mock -- no network access and no running IdP process required.

const state = vi.hoisted(() => ({ getKey: undefined as JWTVerifyGetKey | undefined }));

vi.mock("jose", async (importOriginal) => {
  const actual = await importOriginal<typeof import("jose")>();
  return {
    ...actual,
    createRemoteJWKSet: () => {
      if (!state.getKey) {
        throw new Error("test getKey not configured -- call beforeEach before touching createRemoteJWKSet");
      }
      return state.getKey;
    },
  };
});

const { createServer: createMcpServer } = await import("./server.js");
const { buildHttpApp } = await import("./http_server.js");

const TRUSTED_ISSUER = "https://idp.example/";
const RESOURCE = "https://mcp.kj-atlas.example/";
const KID = "test-key-1";

type PrivateKey = Awaited<ReturnType<typeof generateKeyPair>>["privateKey"];

async function startServer(): Promise<{ baseUrl: string; server: Server; privateKey: PrivateKey }> {
  const { privateKey, publicKey } = await generateKeyPair("RS256");
  const publicJwk = await exportJWK(publicKey);
  publicJwk.kid = KID;
  publicJwk.alg = "RS256";
  state.getKey = createLocalJWKSet({ keys: [publicJwk] });

  const config: HttpTransportConfig = {
    host: "127.0.0.1",
    port: 0,
    resource: RESOURCE,
    trustedIssuer: TRUSTED_ISSUER,
    jwksUri: "https://idp.example/.well-known/jwks.json",
    authorizationServers: [TRUSTED_ISSUER],
  };

  const mcpServer = createMcpServer({ baseUrl: "http://127.0.0.1:0" });
  const app = buildHttpApp(config, mcpServer);

  return await new Promise((resolve, reject) => {
    const server = app.listen(0, "127.0.0.1", () => {
      const port = (server.address() as AddressInfo).port;
      resolve({ baseUrl: `http://127.0.0.1:${port}`, server, privateKey });
    });
    server.on("error", reject);
  });
}

async function signToken(
  privateKey: PrivateKey,
  audience: string,
  claims: Record<string, unknown> = { sub: "test-client" },
  expiresIn = "5m",
): Promise<string> {
  return new SignJWT(claims)
    .setProtectedHeader({ alg: "RS256", kid: KID })
    .setIssuer(TRUSTED_ISSUER)
    .setAudience(audience)
    .setIssuedAt()
    .setExpirationTime(expiresIn)
    .sign(privateKey);
}

describe("buildHttpApp", () => {
  let context: Awaited<ReturnType<typeof startServer>>;

  beforeEach(async () => {
    context = await startServer();
  });

  afterEach(() => {
    context.server.close();
    state.getKey = undefined;
  });

  it("serves the OAuth protected-resource metadata without requiring auth (RFC 9728)", async () => {
    const response = await fetch(`${context.baseUrl}/.well-known/oauth-protected-resource`);
    const body = (await response.json()) as { resource: string; authorization_servers: string[] };

    expect(response.status).toBe(200);
    expect(body.resource).toBe(RESOURCE);
    expect(body.authorization_servers).toEqual([TRUSTED_ISSUER]);
  });

  it("rejects POST /mcp with no Authorization header (401 + WWW-Authenticate)", async () => {
    const response = await fetch(`${context.baseUrl}/mcp`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: {} }),
    });

    expect(response.status).toBe(401);
    expect(response.headers.get("www-authenticate")).toContain("Bearer");
    expect(response.headers.get("www-authenticate")).toContain("resource_metadata=");
  });

  it("rejects POST /mcp with an expired token (401)", async () => {
    const token = await signToken(context.privateKey, RESOURCE, { sub: "test-client" }, "-60s");
    const response = await fetch(`${context.baseUrl}/mcp`, {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: {} }),
    });

    expect(response.status).toBe(401);
  });

  it("rejects a token issued for a different resource/audience", async () => {
    const token = await signToken(context.privateKey, "https://a-different-service.invalid/");
    const response = await fetch(`${context.baseUrl}/mcp`, {
      method: "POST",
      headers: { "content-type": "application/json", authorization: `Bearer ${token}` },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method: "initialize", params: {} }),
    });

    expect(response.status).toBe(401);
  });

  it("passes a validly-signed token through to the MCP transport (past the 401 boundary)", async () => {
    const token = await signToken(context.privateKey, RESOURCE);
    const response = await fetch(`${context.baseUrl}/mcp`, {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json, text/event-stream",
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "test-client", version: "0.0.0" } },
      }),
    });

    expect(response.status).not.toBe(401);
  });
});
