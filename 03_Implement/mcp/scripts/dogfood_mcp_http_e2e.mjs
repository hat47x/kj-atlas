// Dogfood: full MCP HTTP e2e — real mock IdP (JWKS) + real signed JWT +
// real backend document. Proves a remote generative-AI client can connect
// over streamable HTTP and call get_context_projection end-to-end.
import http from "node:http";
import { connect } from "node:net";
import { spawn } from "node:child_process";
import { setTimeout as sleep } from "node:timers/promises";
import { exportJWK, generateKeyPair, SignJWT } from "jose";
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StreamableHTTPClientTransport } from "@modelcontextprotocol/sdk/client/streamableHttp.js";

const TRUSTED_ISSUER = "https://dogfood-idp.example/";
const RESOURCE = "https://mcp.kj-atlas.example/";
const KID = "dogfood-key-1";
const JWKS_PORT = 8799;
const MCP_PORT = 8788;
const DOC_ID = process.argv[2] || "dogfood_probe";

// 1. Generate keypair + serve JWKS (mock IdP).
const { privateKey, publicKey } = await generateKeyPair("RS256");
const publicJwk = await exportJWK(publicKey);
publicJwk.kid = KID;
publicJwk.alg = "RS256";
const jwksServer = http.createServer((req, res) => {
  res.writeHead(200, { "content-type": "application/json" });
  res.end(JSON.stringify({ keys: [publicJwk] }));
});
await new Promise((r) => jwksServer.listen(JWKS_PORT, "127.0.0.1", r));
const JWKS_URI = `http://127.0.0.1:${JWKS_PORT}/.well-known/jwks.json`;

// 2. Sign a bearer token.
const token = await new SignJWT({ sub: "dogfood-client" })
  .setProtectedHeader({ alg: "RS256", kid: KID })
  .setIssuer(TRUSTED_ISSUER)
  .setAudience(RESOURCE)
  .setIssuedAt()
  .setExpirationTime("5m")
  .sign(privateKey);

// 3. Start the MCP HTTP server as a child process.
const mcp = spawn("node", ["./node_modules/.bin/tsx", "src/index.ts"], {
  cwd: new URL("..", import.meta.url).pathname,
  env: {
    ...process.env,
    KJ_ATLAS_MCP_TRANSPORT: "http",
    KJ_ATLAS_MCP_HTTP_HOST: "127.0.0.1",
    KJ_ATLAS_MCP_HTTP_PORT: String(MCP_PORT),
    KJ_ATLAS_MCP_RESOURCE_URL: RESOURCE,
    KJ_ATLAS_MCP_TRUSTED_ISSUER: TRUSTED_ISSUER,
    KJ_ATLAS_MCP_JWKS_URI: JWKS_URI,
    KJ_ATLAS_MCP_AUTHORIZATION_SERVERS: TRUSTED_ISSUER,
    KJ_ATLAS_MCP_API_BASE_URL: "http://127.0.0.1:8000",
  },
  stdio: ["ignore", "pipe", "pipe"],
});
mcp.stderr.on("data", (d) => process.stderr.write(`[mcp] ${d}`));

// Wait for the MCP HTTP port to accept connections (up to ~15s).
for (let i = 0; i < 30; i++) {
  const reachable = await new Promise((resolve) => {
    const sock = connect(MCP_PORT, "127.0.0.1", () => { sock.destroy(); resolve(true); });
    sock.on("error", () => resolve(false));
  });
  if (reachable) break;
  await sleep(500);
}
await sleep(500);

try {
  const client = new Client({ name: "dogfood-http", version: "1.0.0" });
  const transport = new StreamableHTTPClientTransport(new URL(`http://127.0.0.1:${MCP_PORT}/mcp`), {
    requestInit: { headers: { authorization: `Bearer ${token}` } },
  });
  await client.connect(transport);
  const { tools } = await client.listTools();
  console.log(`tools: ${tools.map((t) => t.name).join(", ")}`);

  const result = await client.callTool({
    name: "get_context_projection",
    arguments: { docId: DOC_ID, constraint: "reviewed-only", safeMode: true },
  });
  const text = result.content?.[0]?.text ?? "";
  const projection = JSON.parse(text);
  console.log(`bundleHash: ${projection.bundleHash.slice(0, 12)}…  cards: ${projection.cards.length}`);
  console.log("HTTP e2e PASSED ✅ (auth + initialize + tools/list + tool call over real backend)");
  await client.close();
} finally {
  mcp.kill();
  jwksServer.close();
}
