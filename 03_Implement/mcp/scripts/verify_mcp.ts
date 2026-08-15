#!/usr/bin/env node
// Verify the kj-atlas MCP server from a client (AI/generator verification path).
//
// This is the "generative AI uses MCP to verify" path — a standalone MCP
// client that starts the server over stdio and calls get_context_projection.
//
// Usage (must run under tsx — a .ts script that imports a .ts module and uses
// TS `as` syntax; plain Node 20 rejects these with ERR_UNKNOWN_FILE_EXTENSION
// / SyntaxError):
//   KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 \
//     npm run verify -- [docId] [constraint]     # from 03_Implement/mcp
//   KJ_ATLAS_MCP_API_BASE_URL=http://127.0.0.1:8000 \
//     npx tsx scripts/verify_mcp.ts [docId] [constraint]   # from this dir
//
// Requires a running backend (uvicorn kj_atlas_api.main:app --port 8000)
// and a document id (default: doc_phase1_canvas).

import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
// DOGFOOD-06: shared interpretation logic (unit-tested in
// src/mcp_verify_result.test.ts) so the abnormal-case handling is locked.
import { interpretProjectionResult } from "../src/mcp_verify_result.ts";

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

  // DOGFOOD-03/06: respect the server's isError contract via the shared,
  // unit-tested interpreter. On not_found/error the tool returns
  // { isError: true, text: <plain message> } — never JSON.parsed here.
  const text = result.content?.[0]?.text;
  if (!text) {
    throw new Error("No text content in tool result");
  }
  const interpreted = interpretProjectionResult(text, result.isError === true);
  if (interpreted.outcome !== "ok") {
    console.log(`  → tool reported ${interpreted.outcome}: ${interpreted.errorMessage?.slice(0, 200)}`);
    console.log("  → MCP transport is alive, but the target document is not retrievable.");
    console.log("  → This is a normal not_found/error signal, NOT an MCP path failure.");
    process.exit(0);
  }
  const projection = interpreted.projection as {
    bundleHash: string;
    schemaVersion?: string;
    constraints?: unknown;
    cards?: Array<{ holdState?: string | null }>;
    counts?: { reviewed: number; unreviewed: number; redacted: number };
    voids?: Array<{ id: string; kind: string; resolved: boolean }>;
    narrativeChecks?: Array<{ id: string; issueDirections: string[] }>;
    documentMetadata?: { id: string; title?: string; created_by?: string; lifecycle_state: string; updated_at: string } | null;
  };
  console.log(`  → bundleHash: ${projection.bundleHash}`);
  console.log(`  → schemaVersion: ${projection.schemaVersion ?? "n/a"}`);
  console.log(`  → constraints applied: ${JSON.stringify(projection.constraints ?? "n/a")}`);
  // DOGFOOD-08: surface working-state metadata so the generative-AI path
  // can respect hold/shelve state. holdState is a structural value (no
  // text), safe to project even in SafeMode.
  const cards = Array.isArray(projection.cards) ? projection.cards : [];
  const held = cards.filter((c) => c.holdState === "held").length;
  const pending = cards.filter((c) => c.holdState === "pending").length;
  const shelved = cards.filter((c) => c.holdState === "shelved").length;
  console.log(
    `  → cards: ${cards.length} (held:${held}, pending:${pending}, shelved:${shelved}, no-state:${cards.length - held - pending - shelved})`
  );
  if (projection.counts) {
    console.log(
      `  → counts: reviewed:${projection.counts.reviewed}, unreviewed:${projection.counts.unreviewed}, redacted:${projection.counts.redacted}`
    );
  }
  if (held + pending + shelved > 0) {
    console.log("  → work-state (holdState) projected ✅ (DOGFOOD-08)");
  }
  // 優先3 (voids / narrative A/B): structural state a generative-AI can verify.
  const voids = Array.isArray(projection.voids) ? projection.voids : [];
  if (voids.length > 0) {
    console.log(`  → voids: ${voids.length} (${voids.map((v) => v.kind).join(", ")}) ✅ (KJ-VOIDS-01)`);
  } else {
    console.log("  → voids: 0 (none stored)");
  }
  const narrativeChecks = Array.isArray(projection.narrativeChecks) ? projection.narrativeChecks : [];
  if (narrativeChecks.length > 0) {
    const dirs = narrativeChecks.flatMap((c) => c.issueDirections);
    console.log(`  → narrative checks: ${narrativeChecks.length} (directions: ${dirs.length ? dirs.join(", ") : "none"}) ✅ (KJ-AB-CROSS-CHECK-01)`);
  } else {
    console.log("  → narrative checks: 0 (none stored)");
  }
  // 第2反復: lifecycle metadata (created_by / lifecycle_state) for lifecycle
  // verification. Advisory — null when the list endpoint is unavailable.
  const documentMetadata = projection.documentMetadata;
  if (documentMetadata) {
    const lifecycleState = documentMetadata.lifecycle_state;
    if (lifecycleState !== "active" && lifecycleState !== "archived") {
      throw new Error(`Unexpected lifecycle_state: ${lifecycleState}`);
    }
    console.log(
      `  → lifecycle: ${lifecycleState}${documentMetadata.created_by ? `, created_by=${documentMetadata.created_by}` : ""} ✅ (ADR-0073)`,
    );
    if (lifecycleState === "archived") {
      console.log("  → archived documents are read-only: PUT /docs/{id} is rejected 423 Locked (ADR-0073 D2=A, verified in verify_api_write.sh)");
    }
  } else {
    console.log("  → lifecycle metadata: n/a (list endpoint unavailable or doc absent)");
  }
  console.log("  → projection returned ✅");

  // 3. Verify anti-scoring (no score/rank/confidence fields).
  const serialized = text.toLowerCase();
  for (const banned of ["score", "rank", "confidence", "priority"]) {
    if (serialized.includes(banned)) {
      throw new Error(`Anti-scoring violation: output contains '${banned}'`);
    }
  }
  console.log("  → no scoring vocabulary present ✅");

  // 4. Bundle determinism (runbook scenario): identical inputs -> identical
  //    bundleHash. The projection is deterministic given the document.
  const second = await client.callTool({
    name: "get_context_projection",
    arguments: { docId, constraint, safeMode: true },
  });
  const secondText = second.content?.[0]?.text;
  if (typeof secondText !== "string") {
    throw new Error("No text content in second projection result");
  }
  const secondInterpreted = interpretProjectionResult(secondText, second.isError === true);
  if (secondInterpreted.outcome !== "ok") {
    throw new Error(`Second projection failed: ${secondInterpreted.outcome}`);
  }
  const secondProjection = secondInterpreted.projection as { bundleHash: string };
  if (secondProjection.bundleHash !== projection.bundleHash) {
    throw new Error(
      `Bundle not deterministic: ${projection.bundleHash} != ${secondProjection.bundleHash}`,
    );
  }
  console.log(`  → bundle deterministic (hash stable across calls) ✅`);

  console.log("\nMCP verification PASSED ✅");
  process.exit(0);
} catch (err) {
  console.error(`\nMCP verification FAILED: ${err.message}`);
  process.exit(1);
} finally {
  await client.close().catch(() => {});
}
