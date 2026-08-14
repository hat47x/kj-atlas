import type { DocumentV1 } from "../../frontend/src/domain/types.js";

// EXT-CONN-01 subslice B: fetches the DocumentV1 this server projects from,
// via the same GET /docs/{doc_id} contract the frontend uses (02_Architecture/api.md
// §2.2). This process is not served behind the frontend's nginx proxy, so it
// needs an absolute base URL and (when the deployment enables KJ_ATLAS_API_KEY)
// must send X-API-Key itself -- the browser client never does, relying on the
// same-origin proxy instead.

export type DocumentClientConfig = {
  baseUrl: string;
  apiKey?: string;
};

const SUPPORTED_RUNTIME_PROFILES = new Set(["local-dev", "evaluation", "enterprise-production"]);

export function validateMcpRuntimeProfile(env: NodeJS.ProcessEnv = process.env): string {
  const runtimeProfile = env.KJ_ATLAS_RUNTIME_PROFILE?.trim().toLowerCase() || "local-dev";
  if (runtimeProfile === "saas-multitenant") {
    throw new Error(
      "KJ_ATLAS_RUNTIME_PROFILE=saas-multitenant is unavailable until tenant-bound MCP credentials are implemented.",
    );
  }
  if (!SUPPORTED_RUNTIME_PROFILES.has(runtimeProfile)) {
    throw new Error(`Unsupported KJ_ATLAS_RUNTIME_PROFILE: ${runtimeProfile}`);
  }
  return runtimeProfile;
}

export function loadDocumentClientConfigFromEnv(env: NodeJS.ProcessEnv = process.env): DocumentClientConfig {
  validateMcpRuntimeProfile(env);
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

export async function fetchDocument(config: DocumentClientConfig, docId: string): Promise<DocumentV1> {
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

  return (await response.json()) as DocumentV1;
}

// ADR-0073 / 第2反復: the document's row lifecycle metadata (creator and
// lifecycle state) — payload-independent, exposed so a generative-AI client can
// verify the lifecycle features (created_by / archive) via MCP.
export type DocumentLifecycleMetadata = {
  id: string;
  title?: string;
  created_by?: string;
  lifecycle_state: string;
  updated_at: string;
};

/** Fetch the document's lifecycle metadata via GET /docs (list), matching by id. */
export async function fetchDocumentMetadata(
  config: DocumentClientConfig,
  docId: string,
): Promise<DocumentLifecycleMetadata | null> {
  const url = `${config.baseUrl}/docs`;
  const headers: Record<string, string> = {};
  if (config.apiKey) {
    headers["X-API-Key"] = config.apiKey;
  }

  try {
    const response = await fetch(url, { headers });
    if (!response.ok) {
      return null; // metadata is advisory — the content fetch remains authoritative
    }
    const list = (await response.json()) as DocumentLifecycleMetadata[];
    if (!Array.isArray(list)) return null;
    return list.find((item) => item.id === docId) ?? null;
  } catch {
    return null; // never break the main projection over an advisory metadata fetch
  }
}
