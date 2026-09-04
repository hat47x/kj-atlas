import {
  AdminModelApiError,
  type ControlPlaneCredential,
  type ModelAllowlistSnapshot,
} from "./model_allowlist_api";

export type ModelAllowlistApi = Readonly<{
  getTenantAllowlist: (
    tenantId: string,
    credential?: ControlPlaneCredential,
  ) => Promise<ModelAllowlistSnapshot>;
  putTenantAllowlist: (
    tenantId: string,
    modelIds: string[],
    expectedRevision: string,
    credential?: ControlPlaneCredential,
  ) => Promise<ModelAllowlistSnapshot>;
}>;

export type ModelAllowlistDiff = Readonly<{
  onlyInDraft: string[];
  onlyOnServer: string[];
}>;

export type SaveAllowlistOutcome =
  | Readonly<{
      kind: "saved";
      snapshot: ModelAllowlistSnapshot;
    }>
  | Readonly<{
      kind: "conflict";
      attemptedModelIds: string[];
      current: ModelAllowlistSnapshot;
      diff: ModelAllowlistDiff;
    }>;

export function diffModelAllowlist(
  attemptedModelIds: readonly string[],
  currentModelIds: readonly string[],
): ModelAllowlistDiff {
  const attempted = new Set(attemptedModelIds);
  const current = new Set(currentModelIds);
  return {
    onlyInDraft: [...attempted].filter((modelId) => !current.has(modelId)).sort(),
    onlyOnServer: [...current].filter((modelId) => !attempted.has(modelId)).sort(),
  };
}

export async function saveAllowlistDraft(
  api: ModelAllowlistApi,
  tenantId: string,
  modelIds: string[],
  expectedRevision: string,
  credential: ControlPlaneCredential = {},
): Promise<SaveAllowlistOutcome> {
  try {
    return {
      kind: "saved",
      snapshot: await api.putTenantAllowlist(
        tenantId,
        modelIds,
        expectedRevision,
        credential,
      ),
    };
  } catch (error) {
    if (
      error instanceof AdminModelApiError
      && error.status === 409
      && error.code === "model_allowlist_conflict"
    ) {
      // Conflict recovery is intentionally read-only. The attempted PUT is never
      // retried here. The administrator must review the refreshed server state,
      // adopt its revision as a new editing baseline, and press Save again.
      const current = await api.getTenantAllowlist(tenantId, credential);
      return {
        kind: "conflict",
        attemptedModelIds: [...modelIds],
        current,
        diff: diffModelAllowlist(modelIds, current.modelIds),
      };
    }
    throw error;
  }
}

export function parseModelIdDraft(raw: string): string[] {
  return raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);
}

export function duplicateModelIds(modelIds: readonly string[]): string[] {
  const seen = new Set<string>();
  const duplicates = new Set<string>();
  for (const modelId of modelIds) {
    if (seen.has(modelId)) {
      duplicates.add(modelId);
    }
    seen.add(modelId);
  }
  return [...duplicates].sort();
}
