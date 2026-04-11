export type ContextQueryDraft = {
  queryId: string;
  targetCardIds: string[];
  depth: number;
  scope: "selection" | "document";
  reviewedOnly: boolean;
  safeMode: boolean;
};

export type QueryPreviewState = {
  scope: "selection" | "document";
  depth: number;
  reviewFilter: "reviewed_only" | "all";
  safeMode: boolean;
  targetCount: number;
  canSubmit: boolean;
  blockers: string[];
};

export function buildQueryPreviewState(draft: ContextQueryDraft, previewAcknowledged: boolean): QueryPreviewState {
  const blockers: string[] = [];
  if (draft.queryId.trim().length === 0) blockers.push("queryId is required");
  if (draft.targetCardIds.length === 0) blockers.push("targetCardIds is required");
  if (!previewAcknowledged) blockers.push("preview must be acknowledged before submit");

  return {
    scope: draft.scope,
    depth: draft.depth,
    reviewFilter: draft.reviewedOnly ? "reviewed_only" : "all",
    safeMode: draft.safeMode,
    targetCount: draft.targetCardIds.length,
    canSubmit: blockers.length === 0,
    blockers,
  };
}

export async function runMockContextIntegration(
  draft: ContextQueryDraft,
  previewAcknowledged: boolean,
  postBundle: (query: ContextQueryDraft) => Promise<{ bundleHash: string }>,
): Promise<{ canSubmit: boolean; bundleHash?: string }> {
  const preview = buildQueryPreviewState(draft, previewAcknowledged);
  if (!preview.canSubmit) {
    return { canSubmit: false };
  }
  const response = await postBundle(draft);
  return { canSubmit: true, bundleHash: response.bundleHash };
}
