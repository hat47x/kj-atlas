import { describe, expect, it } from "vitest";

import { buildQueryPreviewState, runMockContextIntegration, type ContextQueryDraft } from "./query_preview";

function baseDraft(): ContextQueryDraft {
  return {
    queryId: "q-ce1-frontend",
    targetCardIds: ["c1"],
    depth: 1,
    scope: "selection",
    reviewedOnly: true,
    safeMode: true,
  };
}

describe("query preview state", () => {
  it("blocks submit until preview is acknowledged", () => {
    const preview = buildQueryPreviewState(baseDraft(), false);
    expect(preview.canSubmit).toBe(false);
    expect(preview.blockers).toContain("preview must be acknowledged before submit");
  });

  it("allows submit after required fields and preview acknowledgement", () => {
    const preview = buildQueryPreviewState(baseDraft(), true);
    expect(preview.canSubmit).toBe(true);
    expect(preview.reviewFilter).toBe("reviewed_only");
  });

  it("reproduces mock integration flow", async () => {
    const draft = baseDraft();
    const result = await runMockContextIntegration(draft, true, async () => ({ bundleHash: "hash-123" }));
    expect(result).toEqual({ canSubmit: true, bundleHash: "hash-123" });
  });
});
