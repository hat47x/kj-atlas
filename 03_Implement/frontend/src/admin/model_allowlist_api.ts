import { csrfHeader } from "../session/csrf";

function resolveApiBase(): string {
  const rawValue = (import.meta.env.KJ_ATLAS_FRONTEND_API_BASE ?? "/api").trim();
  if (rawValue.length === 0) {
    return "/api";
  }
  const normalized = rawValue.endsWith("/") ? rawValue.slice(0, -1) : rawValue;
  return normalized.startsWith("/") ? normalized : "/api";
}

const API_BASE = resolveApiBase();
const REVISION_PATTERN = /^[0-9a-f]{64}$/;

export type ControlPlaneCredential = Readonly<{
  adminApiKey?: string;
}>;

export type ModelAllowlistSnapshot = Readonly<{
  tenantId: string;
  modelIds: string[];
  revision: string;
}>;

export class AdminModelApiError extends Error {
  readonly status: number;
  readonly code?: string;
  readonly currentRevision?: string;

  constructor(
    status: number,
    message: string,
    options: Readonly<{ code?: string; currentRevision?: string }> = {},
  ) {
    super(message);
    this.status = status;
    this.code = options.code;
    this.currentRevision = options.currentRevision;
  }
}

function controlPlaneHeaders(
  credential: ControlPlaneCredential,
  mutation: boolean,
): Record<string, string> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  const adminApiKey = credential.adminApiKey?.trim();
  if (adminApiKey) {
    headers["X-Admin-Api-Key"] = adminApiKey;
  }
  if (mutation) {
    Object.assign(headers, csrfHeader());
  }
  return headers;
}

async function parseError(response: Response): Promise<AdminModelApiError> {
  let message = response.statusText || "Request failed";
  let code: string | undefined;
  let currentRevision: string | undefined;
  try {
    const body = (await response.json()) as {
      detail?: unknown;
    };
    const detail = body.detail;
    if (typeof detail === "string") {
      message = detail;
    } else if (detail && typeof detail === "object") {
      const contract = detail as Record<string, unknown>;
      if (typeof contract.message === "string") {
        message = contract.message;
      }
      if (typeof contract.code === "string") {
        code = contract.code;
      }
      if (
        typeof contract.currentRevision === "string"
        && REVISION_PATTERN.test(contract.currentRevision)
      ) {
        currentRevision = contract.currentRevision;
      }
    }
  } catch {
    // Keep the HTTP status text when the body is not a valid JSON error contract.
  }
  return new AdminModelApiError(response.status, message, { code, currentRevision });
}

function parseAllowlistSnapshot(value: unknown): ModelAllowlistSnapshot {
  if (!value || typeof value !== "object") {
    throw new AdminModelApiError(500, "Invalid model allowlist response shape");
  }
  const body = value as Record<string, unknown>;
  if (
    typeof body.tenantId !== "string"
    || !Array.isArray(body.modelIds)
    || body.modelIds.some((modelId) => typeof modelId !== "string")
    || typeof body.revision !== "string"
    || !REVISION_PATTERN.test(body.revision)
  ) {
    throw new AdminModelApiError(500, "Invalid model allowlist response shape");
  }
  return {
    tenantId: body.tenantId,
    modelIds: [...body.modelIds] as string[],
    revision: body.revision,
  };
}

export async function getTenantModelAllowlist(
  tenantId: string,
  credential: ControlPlaneCredential = {},
): Promise<ModelAllowlistSnapshot> {
  const response = await fetch(
    `${API_BASE}/admin/provision/models/tenants/${encodeURIComponent(tenantId)}/allowlist`,
    {
      method: "GET",
      headers: controlPlaneHeaders(credential, false),
      credentials: "same-origin",
      cache: "no-store",
    },
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  const snapshot = parseAllowlistSnapshot(await response.json());
  if (snapshot.tenantId !== tenantId) {
    throw new AdminModelApiError(500, "Tenant id mismatch in model allowlist response");
  }
  return snapshot;
}

export async function putTenantModelAllowlist(
  tenantId: string,
  modelIds: string[],
  expectedRevision: string,
  credential: ControlPlaneCredential = {},
): Promise<ModelAllowlistSnapshot> {
  const response = await fetch(
    `${API_BASE}/admin/provision/models/tenants/${encodeURIComponent(tenantId)}/allowlist`,
    {
      method: "PUT",
      headers: {
        ...controlPlaneHeaders(credential, true),
        "Content-Type": "application/json",
      },
      credentials: "same-origin",
      cache: "no-store",
      body: JSON.stringify({ modelIds, expectedRevision }),
    },
  );
  if (!response.ok) {
    throw await parseError(response);
  }
  const snapshot = parseAllowlistSnapshot(await response.json());
  if (snapshot.tenantId !== tenantId) {
    throw new AdminModelApiError(500, "Tenant id mismatch in model allowlist response");
  }
  return snapshot;
}

export const modelAllowlistApi = {
  getTenantAllowlist: getTenantModelAllowlist,
  putTenantAllowlist: putTenantModelAllowlist,
};
