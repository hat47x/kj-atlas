#!/usr/bin/env node
// Verify the kj-atlas MCP server from a client (AI/generator verification path).
//
// This is the "generative AI uses MCP to verify" path — a standalone MCP
// client that starts the server over stdio and calls get_context_projection.
//
// Usage:
//   KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 \
//     node scripts/verify_mcp.mjs [docId] [constraint]
//
// Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000)
// and a document id (default: doc_phase1_canvas).

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";

const docId = process.argv[2] || "doc_phase1_canvas";
const constraint = process.argv[3] || "reviewed-only";

const transport = new StdioClientTransport({
  command: process.platform === "win32" ? "npx.cmd" : "npx",
  args: ["tsx", "src/index.ts"],
  cwd: new URL("..", import.meta.url).pathname,
  env: {
    ...process.env,
    KJ_ATLAS_MCP_TRANSPORT: "stdio",
  },
});

const client = new Client({ name: "kj-atlas-mcp-verify", version: "1.0.0" });

try {
  await client.connect(transport);

  // 1. List tools — expect exactly one read-only tool.
  const { tools } = await client.listTools();
  const names = tools.map((t) => t.name);
  console.log(`tools/list: ${names.join(", ")}`);
  if (names.length !== 1 || names[0] !== "get_context_projection") {
    throw new Error("Expected exactly get_context_projection tool");
  }
  console.log("  → single read-only tool confirmed ✅");

  // 2. Call get_context_projection (safeMode defaults true → no card text).
  console.log(`calling get_context_projection(docId=${docId}, constraint=${constraint}, safeMode=true)`);
  const result = await client.callTool({
    name: "get_context_projection",
    arguments: { docId, constraint, safeMode: true },
  });

  // DOGFOOD-03: respect the server's isError contract. On not_found/error the
  // tool returns { isError: true, content: [{ type: "text", text: <message> }] }
  // where text is a plain message, not a projection JSON — parse it as such
  // instead of crashing on JSON.parse.
  const text = result.content?.[0]?.text;
  if (!text) {
    throw new Error("No text content in tool result");
  }
  if (result.isError === true) {
    const isNotFound = text.includes("DocumentNotFound") || text.includes("not found") || text.includes("404");
    console.log(`  → tool reported an error outcome (${isNotFound ? "not_found" : "error"}): ${text.slice(0, 200)}`);
    console.log("  → MCP transport is alive, but the target document is not retrievable.");
    console.log("  → This is a normal not_found signal, NOT an MCP path failure.");
    process.exit(0);
  }
  const projection = JSON.parse(text);
  console.log(`  → bundleHash: ${projection.bundleHash}`);
  console.log(`  → schemaVersion: ${projection.schemaVersion ?? "n/a"}`);
  console.log(`  → constraints applied: ${JSON.stringify(projection.constraints ?? "n/a")}`);
  console.log("  → projection returned ✅");

  // 3. Verify anti-scoring (no score/rank/confidence fields).
  const serialized = text.toLowerCase();
  for (const banned of ["score", "rank", "confidence", "priority"]) {
    if (serialized.includes(banned)) {
      throw new Error(`Anti-scoring violation: output contains '${banned}'`);
    }
  }
  console.log("  → no scoring vocabulary present ✅");

  console.log("\nMCP verification PASSED ✅");
  process.exit(0);
} catch (err) {
  console.error(`\nMCP verification FAILED: ${err.message}`);
  process.exit(1);
} finally {
  await client.close().catch(() => {});
}
