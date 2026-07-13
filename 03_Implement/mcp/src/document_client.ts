import type { DocumentV2 } from "../../frontend/src/domain/types.js";

// EXT-CONN-01 subslice B: fetches the DocumentV2 this server projects from,
// via the same GET /docs/{doc_id} contract the frontend uses (02_Architecture/api.md
// §2.2). This process is not served behind the frontend's nginx proxy, so it
// needs an absolute base URL and (when the deployment enables KJ_ATLAS_API_KEY)
// must send X-API-Key itself -- the browser client never does, relying on the
// same-origin proxy instead.

export type DocumentClientConfig = {
  baseUrl: string;
  apiKey?: string;
};

export function loadDocumentClientConfigFromEnv(env: NodeJS.ProcessEnv = process.env): DocumentClientConfig {
  const rawBaseUrl = env.KJ_ATLAS_MCP_API_BASE_URL?.trim();
  const baseUrl = rawBaseUrl && rawBaseUrl.length > 0 ? rawBaseUrl : "http://127.0.0.1:8000";
  const apiKey = env.KJ_ATLAS_API_KEY?.trim() || undefined;
  return { baseUrl: baseUrl.endsWith("/") ? baseUrl.slice(0, -1) : baseUrl, apiKey };
}

export class DocumentNotFoundError extends Error {
  constructor(public readonly docId: string) {
    super(`Document not found: ${docId}`);
    this.name = "DocumentNotFoundError";
  }
}

export class DocumentFetchError extends Error {
  constructor(public readonly docId: string, public readonly status: number) {
    super(`Failed to fetch document ${docId}: HTTP ${status}`);
    this.name = "DocumentFetchError";
  }
}

export async function fetchDocument(config: DocumentClientConfig, docId: string): Promise<DocumentV2> {
  const url = `${config.baseUrl}/docs/${encodeURIComponent(docId)}`;
  const headers: Record<string, string> = {};
  if (config.apiKey) {
    headers["X-API-Key"] = config.apiKey;
  }

  const response = await fetch(url, { headers });

  if (response.status === 404) {
    throw new DocumentNotFoundError(docId);
  }
  if (!response.ok) {
    throw new DocumentFetchError(docId, response.status);
  }

  return (await response.json()) as DocumentV2;
}
