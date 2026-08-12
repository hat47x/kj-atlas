import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { createServer } from "./server.js";
import { loadDocumentClientConfigFromEnv } from "./document_client.js";
import { loadHttpTransportConfigFromEnv } from "./oauth_config.js";
import { buildHttpApp } from "./http_server.js";

// stdout is reserved exclusively for the MCP JSON-RPC stream once connected
// (stdio mode) -- all diagnostics (including audit_log.ts's entries) go to
// stderr. In http mode nothing reserves stdout this way, but diagnostics
// still go to stderr for consistency with the stdio deployment.

async function main(): Promise<void> {
  const transportKind = (process.env.KJ_ATLAS_MCP_TRANSPORT?.trim() || "stdio").toLowerCase();

  if (transportKind === "stdio") {
    const server = createServer(loadDocumentClientConfigFromEnv());
    const transport = new StdioServerTransport();
    await server.connect(transport);
    return;
  }

  if (transportKind === "http") {
    const httpConfig = loadHttpTransportConfigFromEnv();
    const app = buildHttpApp(httpConfig, loadDocumentClientConfigFromEnv());
    await new Promise<void>((resolve) => {
      app.listen(httpConfig.port, httpConfig.host, () => {
        process.stderr.write(
          `kj-atlas-mcp: streamable-HTTP transport listening on http://${httpConfig.host}:${httpConfig.port}${"\n"}`
        );
        resolve();
      });
    });
    return;
  }

  throw new Error(`Unknown KJ_ATLAS_MCP_TRANSPORT: ${transportKind} (expected "stdio" or "http")`);
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? (error.stack ?? error.message) : String(error);
  process.stderr.write(`${message}\n`);
  process.exitCode = 1;
});
