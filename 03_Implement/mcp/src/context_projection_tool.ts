import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  buildContextProjection,
  CONTEXT_PROJECTION_CONSTRAINTS,
} from "../../frontend/src/export/context_bundle_projection.js";
import { DocumentNotFoundError, fetchDocument, type DocumentClientConfig } from "./document_client.js";
import { computeQueryCanonicalHash, logAuditEntry } from "./audit_log.js";

// EXT-CONN-01 subslice B: the ONLY capability this server registers. Read-only
// resources.list() and tools.list() are exercised by
// context_projection_tool.test.ts against a fixed snapshot so a future PR
// cannot silently add a write/ingest/apply/publish/sampling/elicitation
// capability without that test visibly changing (Maintainer代理裁可
// allowlist condition).

export function registerContextProjectionTool(server: McpServer, documentClientConfig: DocumentClientConfig): void {
  server.registerTool(
    "get_context_projection",
    {
      title: "Get context projection",
      description:
        "Read-only, constraint-scoped, SafeMode-respecting projection of a kj-atlas document " +
        "(ADR-0054 stage 1). The output never includes a score, rank, confidence, or priority " +
        "value of any kind. When safeMode is true (the default), no card text is exposed -- only " +
        "structure and counts. " +
        "Unreviewed cards are never exposed on ANY constraint (even safeMode=false reports " +
        "cards=0 for them, SEC-CONTEXT-PROJECTION-01 fail-closed): use this tool for reviewing " +
        "and structuring already-reviewed content, not for initial exploration of unreviewed " +
        "material (DOGFOOD-05).",
      inputSchema: {
        docId: z.string().min(1).describe("Target Document id."),
        constraint: z
          .enum(CONTEXT_PROJECTION_CONSTRAINTS)
          .describe("One of: reviewed-only, evidence, contradiction, summary."),
        safeMode: z
          .boolean()
          .default(true)
          .describe("Withholds card text when true. Defaults to true (the safe default) when omitted."),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async ({ docId, constraint, safeMode }) => {
      const queryCanonicalHash = await computeQueryCanonicalHash({ docId, constraint, safeMode });

      try {
        const doc = await fetchDocument(documentClientConfig, docId);
        const projection = await buildContextProjection({ doc, constraint, safeMode });

        logAuditEntry({
          schemaVersion: "mcp-context-read.v1",
          occurredAt: new Date().toISOString(),
          docId,
          constraint,
          safeMode,
          queryCanonicalHash,
          bundleHash: projection.bundleHash,
          outcome: "ok",
        });

        return {
          content: [{ type: "text" as const, text: JSON.stringify(projection, null, 2) }],
        };
      } catch (error) {
        logAuditEntry({
          schemaVersion: "mcp-context-read.v1",
          occurredAt: new Date().toISOString(),
          docId,
          constraint,
          safeMode,
          queryCanonicalHash,
          bundleHash: null,
          outcome: error instanceof DocumentNotFoundError ? "not_found" : "error",
        });

        const message = error instanceof Error ? error.message : String(error);
        return { content: [{ type: "text" as const, text: message }], isError: true };
      }
    },
  );
}
