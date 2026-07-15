export type ContextQueryDraft = {
  queryId: string;
  goal: string;
  scope: "document" | "view" | "island";
  depth: number;
  constraints: Record<string, unknown>;
  reviewFilter: "reviewedOnly" | "includeUnreviewed";
  safeModePolicy: "strict";
  outputMode: "summary" | "proposal" | "candidate";
  previewConfirmed: boolean;
};

export type ContextBundleMock = {
  queryCanonicalHash: string;
  bundleHash: string;
  selected: unknown[];
  relations: unknown[];
  evidence: unknown[];
  contradictions: unknown[];
  reviewFlags: { reviewed: number; unreviewed: number };
  truncationMeta: Record<string, unknown>;
  excludedReason: string[];
};

export type QueryPreviewState = {
  scope: ContextQueryDraft["scope"];
  depth: number;
  reviewFilter: ContextQueryDraft["reviewFilter"];
  safeModePolicy: ContextQueryDraft["safeModePolicy"];
  outputMode: ContextQueryDraft["outputMode"];
  previewConfirmed: boolean;
  canSubmit: boolean;
  blockers: string[];
};

function toStableValue(value: unknown): unknown {
  if (Array.isArray(value)) {
    return value.map((item) => toStableValue(item));
  }
  if (value && typeof value === "object") {
    const entries = Object.entries(value as Record<string, unknown>).sort(([left], [right]) => left.localeCompare(right));
    return Object.fromEntries(entries.map(([key, entryValue]) => [key, toStableValue(entryValue)]));
  }
  return value;
}

export function toCanonicalQueryKey(draft: ContextQueryDraft): string {
  return JSON.stringify(toStableValue({
    queryId: draft.queryId,
    goal: draft.goal,
    scope: draft.scope,
    depth: draft.depth,
    constraints: draft.constraints,
    reviewFilter: draft.reviewFilter,
    safeModePolicy: draft.safeModePolicy,
    outputMode: draft.outputMode,
    previewConfirmed: draft.previewConfirmed,
  }));
}

export async function toCanonicalQueryHash(draft: ContextQueryDraft): Promise<string> {
  const bytes = new TextEncoder().encode(toCanonicalQueryKey(draft));
  const digest = await globalThis.crypto.subtle.digest("SHA-256", bytes);
  return Array.from(new Uint8Array(digest), (byte) => byte.toString(16).padStart(2, "0")).join("");
}

export function buildQueryPreviewState(draft: ContextQueryDraft): QueryPreviewState {
  const blockers: string[] = [];
  if (draft.queryId.trim().length === 0) blockers.push("queryId is required");
  if (draft.goal.trim().length === 0) blockers.push("goal is required");
  if (draft.depth < 0 || draft.depth > 5) blockers.push("depth must be between 0 and 5");
  if (draft.safeModePolicy === "strict" && draft.reviewFilter === "includeUnreviewed") {
    blockers.push("safeMode strict requires reviewFilter=reviewedOnly");
  }
  if (!draft.previewConfirmed) blockers.push("previewConfirmed must be true before submit");

  return {
    scope: draft.scope,
    depth: draft.depth,
    reviewFilter: draft.reviewFilter,
    safeModePolicy: draft.safeModePolicy,
    outputMode: draft.outputMode,
    previewConfirmed: draft.previewConfirmed,
    canSubmit: blockers.length === 0,
    blockers,
  };
}

export type RunMockContextIntegrationResult =
  | { canSubmit: false; statusCode: 400; errorCode: "unknown_contract_key"; unknownKeys: string[] }
  | { canSubmit: false; statusCode: 422; errorCode: "invalid_bundle_contract"; invalidReasons: string[] }
  | { canSubmit: false; statusCode: 422; errorCode: "preview_required" | "invalid_query"; blockers: string[] }
  | { canSubmit: false; statusCode: 409; errorCode: "nondeterministic_bundle"; reason: "query_hash_mismatch" }
  | { canSubmit: true; statusCode: 200; queryCanonicalHash: string; bundleHash: string; sourceBundleHash: string; excludedReason: string[] };

const CONTEXT_QUERY_V1_KEYS = new Set([
  "queryId",
  "goal",
  "scope",
  "depth",
  "constraints",
  "reviewFilter",
  "safeModePolicy",
  "outputMode",
  "previewConfirmed",
]);

const CONTEXT_BUNDLE_V1_KEYS = new Set([
  "queryCanonicalHash",
  "bundleHash",
  "selected",
  "relations",
  "evidence",
  "contradictions",
  "reviewFlags",
  "truncationMeta",
  "excludedReason",
]);

function validateContextBundleV1(bundle: ContextBundleMock): string[] {
  const reasons: string[] = [];
  const unknownKeys = Object.keys(bundle as Record<string, unknown>)
    .filter((key) => !CONTEXT_BUNDLE_V1_KEYS.has(key))
    .sort((left, right) => left.localeCompare(right));
  if (unknownKeys.length > 0) reasons.push(`unknown ContextBundleV1 keys: ${unknownKeys.join(", ")}`);
  if (typeof bundle.queryCanonicalHash !== "string" || bundle.queryCanonicalHash.length === 0) reasons.push("queryCanonicalHash must be non-empty string");
  if (typeof bundle.bundleHash !== "string" || bundle.bundleHash.length === 0) reasons.push("bundleHash must be non-empty string");
  if (!Array.isArray(bundle.selected)) reasons.push("selected must be array");
  if (!Array.isArray(bundle.relations)) reasons.push("relations must be array");
  if (!Array.isArray(bundle.evidence)) reasons.push("evidence must be array");
  if (!Array.isArray(bundle.contradictions)) reasons.push("contradictions must be array");
  if (!bundle.reviewFlags || typeof bundle.reviewFlags.reviewed !== "number" || typeof bundle.reviewFlags.unreviewed !== "number") {
    reasons.push("reviewFlags must include numeric reviewed/unreviewed");
  }
  if (!bundle.truncationMeta || typeof bundle.truncationMeta !== "object" || Array.isArray(bundle.truncationMeta)) {
    reasons.push("truncationMeta must be object");
  }
  if (!Array.isArray(bundle.excludedReason) || bundle.excludedReason.some((item) => typeof item !== "string")) {
    reasons.push("excludedReason must be string[]");
  }
  return reasons;
}

function findUnknownContractKeys(draft: ContextQueryDraft): string[] {
  return Object.keys(draft as Record<string, unknown>)
    .filter((key) => !CONTEXT_QUERY_V1_KEYS.has(key))
    .sort((left, right) => left.localeCompare(right));
}

export async function runMockContextIntegration(
  draft: ContextQueryDraft,
  postBundle: (query: ContextQueryDraft) => Promise<ContextBundleMock>,
): Promise<RunMockContextIntegrationResult> {
  const unknownKeys = findUnknownContractKeys(draft);
  if (unknownKeys.length > 0) {
    return {
      canSubmit: false,
      statusCode: 400,
      errorCode: "unknown_contract_key",
      unknownKeys,
    };
  }

  const preview = buildQueryPreviewState(draft);
  if (!preview.canSubmit) {
    const hasPreviewGateBlocker = preview.blockers.includes("previewConfirmed must be true before submit");
    return {
      canSubmit: false,
      statusCode: 422,
      errorCode: hasPreviewGateBlocker ? "preview_required" : "invalid_query",
      blockers: preview.blockers,
    };
  }

  const response = await postBundle(draft);
  const bundleErrors = validateContextBundleV1(response);
  if (bundleErrors.length > 0) {
    return {
      canSubmit: false,
      statusCode: 422,
      errorCode: "invalid_bundle_contract",
      invalidReasons: bundleErrors,
    };
  }
  const queryCanonicalHash = await toCanonicalQueryHash(draft);
  if (response.queryCanonicalHash !== queryCanonicalHash) {
    return {
      canSubmit: false,
      statusCode: 409,
      errorCode: "nondeterministic_bundle",
      reason: "query_hash_mismatch",
    };
  }

  return {
    canSubmit: true,
    statusCode: 200,
    queryCanonicalHash: response.queryCanonicalHash,
    bundleHash: response.bundleHash,
    sourceBundleHash: response.bundleHash,
    excludedReason: response.excludedReason,
  };
}
