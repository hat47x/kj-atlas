import { canonicalizeJson } from "../../frontend/src/domain/patch/patch_fingerprint.js";
import type { ContextProjectionConstraint } from "../../frontend/src/export/context_bundle_projection.js";

// EXT-CONN-01 subslice B, AC-3: every read gets a bundleHash/queryCanonicalHash
// correlation. This does NOT call the backend's POST /docs/{id}/context-audit
// (CE-4) endpoint: that contract's `channel` enum is fixed to "api"|"cli"|"gui"
// and its `command` field is a backend-enforced whitelist with no slot for an
// MCP-originated read (App.tsx documents this same gap for EXT-AGENT-02's own
// import path). Adding an "mcp" channel/command is a shared-contract change
// beyond what this subslice's Maintainer代理裁可 approved (MCP SDK dependency +
// package only) -- deferred to subslice C or a dedicated backend issue. Until
// then, every read is logged locally as structured JSON to stderr (never
// stdout -- that is reserved for the MCP stdio JSON-RPC stream), which is
// deterministic, traceable, and does not require a backend change.

async function sha256Hex(input: string): Promise<string> {
  const encoder = new TextEncoder();
  const bytes = encoder.encode(input);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest))
    .map((value) => value.toString(16).padStart(2, "0"))
    .join("");
}

export async function computeQueryCanonicalHash(input: {
  docId: string;
  constraint: ContextProjectionConstraint;
  safeMode: boolean;
}): Promise<string> {
  return sha256Hex(canonicalizeJson(input));
}

export type AuditLogEntry = {
  schemaVersion: "mcp-context-read.v1";
  occurredAt: string;
  docId: string;
  constraint: ContextProjectionConstraint;
  safeMode: boolean;
  queryCanonicalHash: string;
  /** null only when outcome !== "ok" (no projection was built to hash). */
  bundleHash: string | null;
  outcome: "ok" | "not_found" | "error";
};

/**
 * Synchronous, local-only write. Throws if stderr itself cannot be written to
 * -- callers must let that propagate as a tool error (AC-3: a missing
 * correlation must never be treated as a successful read), not swallow it.
 */
export function logAuditEntry(entry: AuditLogEntry): void {
  process.stderr.write(`${JSON.stringify(entry)}\n`);
}
