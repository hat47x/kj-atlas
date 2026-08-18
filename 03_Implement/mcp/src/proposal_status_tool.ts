import { z } from "zod";
import type { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import {
  fetchProposalStatus,
  type DocumentClientConfig,
} from "./document_client.js";

// EXT-CONN-01 subslice B: read-only capability extension. Like
// get_context_projection, this tool is READ-ONLY (annotations.readOnlyHint):
// it lets a generative-AI verifier confirm a document's CE4 proposal lifecycle
// (proposal-only vs decided) via GET /ai/proposals/status -- never a write.
// The context_projection_tool.test.ts "tools/list exposes exactly one read-only
// tool" invariant is updated to expect both read-only tools.

export function registerProposalStatusTool(
  server: McpServer,
  documentClientConfig: DocumentClientConfig,
): void {
  server.registerTool(
    "get_proposal_status",
    {
      title: "Get proposal lifecycle status",
      description:
        "Read-only CE4 proposal lifecycle status for a kj-atlas document: whether each " +
        "AI proposal is still proposal-only (status=proposed) or was decided by a human " +
        "(accepted/rejected/held, with decidedAt). Read-only -- never mutates anything. " +
        "Use it to verify that an AI proposal has not been auto-applied and to trace the " +
        "human decision (CE4 traceability).",
      inputSchema: {
        docId: z.string().min(1).describe("Target Document id."),
      },
      annotations: {
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false,
      },
    },
    async ({ docId }) => {
      try {
        const proposals = await fetchProposalStatus(documentClientConfig, docId);
        return {
          content: [{ type: "text" as const, text: JSON.stringify({ docId, proposals }, null, 2) }],
        };
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        return { content: [{ type: "text" as const, text: message }], isError: true };
      }
    },
  );
}
