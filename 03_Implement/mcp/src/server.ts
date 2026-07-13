import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { registerContextProjectionTool } from "./context_projection_tool.js";
import type { DocumentClientConfig } from "./document_client.js";

export function createServer(documentClientConfig: DocumentClientConfig): McpServer {
  const server = new McpServer({ name: "kj-atlas-mcp", version: "0.1.0" });
  registerContextProjectionTool(server, documentClientConfig);
  return server;
}
