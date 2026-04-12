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

export function buildQueryPreviewState(draft: ContextQueryDraft): QueryPreviewState {
  const blockers: string[] = [];
  if (draft.queryId.trim().length === 0) blockers.push("queryId is required");
  if (draft.goal.trim().length === 0) blockers.push("goal is required");
  if (draft.depth < 0 || draft.depth > 5) blockers.push("depth must be between 0 and 5");
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
  | { canSubmit: false; statusCode: 422; errorCode: "preview_required" | "invalid_query"; blockers: string[] }
  | { canSubmit: true; statusCode: 200; bundleHash: string; excludedReason: string[] };

export async function runMockContextIntegration(
  draft: ContextQueryDraft,
  postBundle: (query: ContextQueryDraft) => Promise<ContextBundleMock>,
): Promise<RunMockContextIntegrationResult> {
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
  return { canSubmit: true, statusCode: 200, bundleHash: response.bundleHash, excludedReason: response.excludedReason };
}
