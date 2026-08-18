import { canonicalizeJson } from "../../frontend/src/domain/patch/patch_fingerprint.js";
import type { ContextProjectionConstraint } from "../../frontend/src/export/context_bundle_projection.js";
import type { DocumentClientConfig } from "./document_client.js";

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

const CE4_AUDIT_SCHEMA_VERSION = "ce4.audit.v1" as const;

/**
 * EXT-CONN-01 channel wiring (subslice C / dedicated backend issue): report an
 * MCP-originated read to the backend's POST /docs/{doc_id}/context-audit (CE-4)
 * endpoint with `channel="mcp"`, so an MCP-projected read is traceable in the
 * same audit trail as api/cli/gui callers. This closes the gap recorded in the
 * old "Non-goals" note (channel enum had no mcp slot) -- the backend now accepts
 * it and api.md documents it.
 *
 * Best-effort by design: the read's own correlation is the local AuditLogEntry
 * above (synchronous, stderr, always written). The CE-4 emit is an additional
 * backend-visible sink for an already-successful read -- if it fails we record a
 * structured warning to stderr and continue instead of turning a successful
 * read into an error.
 */
export async function emitContextAuditEvent(
  config: DocumentClientConfig,
  input: { docId: string; safeMode: boolean; queryCanonicalHash: string; bundleHash: string },
): Promise<void> {
  const url = `${config.baseUrl}/docs/${encodeURIComponent(input.docId)}/context-audit`;
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (config.apiKey) {
    headers["X-API-Key"] = config.apiKey;
  }
  const body = {
    operation: "query",
    safeMode: input.safeMode,
    equivalenceKey: input.queryCanonicalHash,
    bundleHash: input.bundleHash,
    queryHash: input.queryCanonicalHash,
    dryRun: true,
    sideEffect: "none",
    command: "context-query",
    channel: "mcp",
    schemaVersion: CE4_AUDIT_SCHEMA_VERSION,
  };
  try {
    const response = await fetch(url, { method: "POST", headers, body: JSON.stringify(body) });
    if (!response.ok) {
      process.stderr.write(
        `${JSON.stringify({
          schemaVersion: "mcp-context-read.v1",
          occurredAt: new Date().toISOString(),
          docId: input.docId,
          message: "CE-4 audit emit failed (best-effort; local audit entry remains the correlation)",
          status: response.status,
          body,
        })}\n`,
      );
    }
  } catch (error) {
    process.stderr.write(
      `${JSON.stringify({
        schemaVersion: "mcp-context-read.v1",
        occurredAt: new Date().toISOString(),
        docId: input.docId,
        message: "CE-4 audit emit error (best-effort; local audit entry remains the correlation)",
        error: error instanceof Error ? error.message : String(error),
      })}\n`,
    );
  }
}
