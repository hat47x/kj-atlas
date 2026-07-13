import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer } from "./server.js";
import { loadDocumentClientConfigFromEnv } from "./document_client.js";

// stdout is reserved exclusively for the MCP JSON-RPC stream once connected
// -- all diagnostics (including audit_log.ts's entries) go to stderr.

async function main(): Promise<void> {
  const server = createServer(loadDocumentClientConfigFromEnv());
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? (error.stack ?? error.message) : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
});
