import { describe, expect, it } from "vitest";

import { buildQueryPreviewState, runMockContextIntegration, toCanonicalQueryKey, type ContextQueryDraft } from "./query_preview";

function baseDraft(): ContextQueryDraft {
  return {
    queryId: "q-ce1-frontend",
    goal: "Summarize contradictions around selected islands",
    depth: 1,
    scope: "view",
    constraints: { tokenBudget: 1200 },
    reviewFilter: "reviewedOnly",
    safeModePolicy: "strict",
    outputMode: "summary",
    previewConfirmed: true,
  };
}

describe("query preview state", () => {
  it("blocks submit until previewConfirmed is true", () => {
    const preview = buildQueryPreviewState({ ...baseDraft(), previewConfirmed: false });
    expect(preview.canSubmit).toBe(false);
    expect(preview.blockers).toContain("previewConfirmed must be true before submit");
  });

  it("allows submit after required fields and preview confirmation", () => {
    const preview = buildQueryPreviewState(baseDraft());
    expect(preview.canSubmit).toBe(true);
    expect(preview.reviewFilter).toBe("reviewedOnly");
  });

  it("blocks unreviewed filter when safeModePolicy is strict", () => {
    const preview = buildQueryPreviewState({ ...baseDraft(), reviewFilter: "includeUnreviewed" });
    expect(preview.canSubmit).toBe(false);
    expect(preview.blockers).toContain("safeMode strict requires reviewFilter=reviewedOnly");
  });

  it("returns 422 preview_required when preview is not confirmed", async () => {
    const draft = { ...baseDraft(), previewConfirmed: false };
    const result = await runMockContextIntegration(draft, async () => {
      throw new Error("should not be called");
    });
    expect(result).toEqual({
      canSubmit: false,
      statusCode: 422,
      errorCode: "preview_required",
      blockers: ["previewConfirmed must be true before submit"],
    });
  });

  it("reproduces mock integration flow with bundleHash", async () => {
    const draft = baseDraft();
    const result = await runMockContextIntegration(draft, async () => ({
      bundleHash: "hash-123",
      selected: [],
      relations: [],
      evidence: [],
      contradictions: [],
      reviewFlags: { reviewed: 2, unreviewed: 0 },
      truncationMeta: { truncated: false },
      excludedReason: ["unreviewed_filtered"],
    }));
    expect(result).toEqual({ canSubmit: true, statusCode: 200, bundleHash: "hash-123", excludedReason: ["unreviewed_filtered"] });
  });

  it("builds a deterministic canonical key for semantically equal inputs", () => {
    const first = baseDraft();
    const second: ContextQueryDraft = {
      ...baseDraft(),
      constraints: {
        modelTier: "local",
        tokenBudget: 1200,
        nested: { beta: true, alpha: "x" },
      },
    };
    const third: ContextQueryDraft = {
      ...baseDraft(),
      constraints: {
        nested: { alpha: "x", beta: true },
        tokenBudget: 1200,
        modelTier: "local",
      },
    };

    expect(toCanonicalQueryKey(first)).toBe(toCanonicalQueryKey(baseDraft()));
    expect(toCanonicalQueryKey(second)).toBe(toCanonicalQueryKey(third));
  });
});
