import { describe, expect, it } from "vitest";

import {
  buildQueryPreviewState,
  runMockContextIntegration,
  toCanonicalQueryHash,
  toCanonicalQueryKey,
  type ContextBundleMock,
  type ContextQueryDraft,
} from "./query_preview";

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

  it("returns 400 unknown_contract_key when query contains keys outside ContextQueryV1", async () => {
    const invalidDraft = { ...baseDraft(), extraFlag: true } as ContextQueryDraft & { extraFlag: boolean };
    const result = await runMockContextIntegration(invalidDraft, async () => {
      throw new Error("should not be called");
    });
    expect(result).toEqual({
      canSubmit: false,
      statusCode: 400,
      errorCode: "unknown_contract_key",
      unknownKeys: ["extraFlag"],
    });
  });

  it("reproduces mock integration flow with bundleHash", async () => {
    const draft = baseDraft();
    const queryCanonicalHash = await toCanonicalQueryHash(draft);
    const result = await runMockContextIntegration(draft, async () => ({
      queryCanonicalHash,
      bundleHash: "hash-123",
      selected: [],
      relations: [],
      evidence: [],
      contradictions: [],
      reviewFlags: { reviewed: 2, unreviewed: 0 },
      truncationMeta: { truncated: false },
      excludedReason: ["unreviewed_filtered"],
    }));
    expect(result).toEqual({
      canSubmit: true,
      statusCode: 200,
      queryCanonicalHash,
      bundleHash: "hash-123",
      sourceBundleHash: "hash-123",
      excludedReason: ["unreviewed_filtered"],
    });
  });

  it("returns 409 nondeterministic_bundle when response query hash mismatches", async () => {
    const draft = baseDraft();
    const result = await runMockContextIntegration(draft, async () => ({
      queryCanonicalHash: "mismatch",
      bundleHash: "hash-123",
      selected: [],
      relations: [],
      evidence: [],
      contradictions: [],
      reviewFlags: { reviewed: 2, unreviewed: 0 },
      truncationMeta: { truncated: false },
      excludedReason: [],
    }));
    expect(result).toEqual({
      canSubmit: false,
      statusCode: 409,
      errorCode: "nondeterministic_bundle",
      reason: "query_hash_mismatch",
    });
  });

  it("returns 422 invalid_bundle_contract when fixture breaks ContextBundleV1 signature", async () => {
    const draft = baseDraft();
    const result = await runMockContextIntegration(draft, async () => ({
      queryCanonicalHash: await toCanonicalQueryHash(draft),
      bundleHash: "",
      selected: [],
      relations: [],
      evidence: [],
      contradictions: [],
      reviewFlags: { reviewed: 2, unreviewed: 0 },
      truncationMeta: { truncated: false },
      excludedReason: ["ok", 1] as unknown as string[],
    }));
    expect(result).toEqual({
      canSubmit: false,
      statusCode: 422,
      errorCode: "invalid_bundle_contract",
      invalidReasons: ["bundleHash must be non-empty string", "excludedReason must be string[]"],
    });
  });

  it("keeps transport and handoff metadata out of logical ContextBundleV1", async () => {
    const draft = baseDraft();
    const result = await runMockContextIntegration(draft, async () => ({
      queryCanonicalHash: await toCanonicalQueryHash(draft),
      bundleHash: "hash-123",
      selected: [],
      relations: [],
      evidence: [],
      contradictions: [],
      reviewFlags: { reviewed: 2, unreviewed: 0 },
      truncationMeta: { truncated: false },
      excludedReason: [],
      queryId: draft.queryId,
      schemaVersion: "1.0.0",
      sourceBundleHash: "hash-123",
    } as unknown as ContextBundleMock));

    expect(result).toEqual({
      canSubmit: false,
      statusCode: 422,
      errorCode: "invalid_bundle_contract",
      invalidReasons: ["unknown ContextBundleV1 keys: queryId, schemaVersion, sourceBundleHash"],
    });
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

  it("hashes the canonical query as lowercase sha256 hex", async () => {
    const hash = await toCanonicalQueryHash(baseDraft());
    expect(hash).toMatch(/^[0-9a-f]{64}$/);
    expect(hash).toBe("f8f19c1dd1fdfff86c2a4b394bd3d10493c06001d3ef1783d54bf6620939fd46");
  });
});
