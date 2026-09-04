import { describe, expect, it, vi } from "vitest";

import { AdminModelApiError } from "./model_allowlist_api";
import {
  diffModelAllowlist,
  duplicateModelIds,
  parseModelIdDraft,
  saveAllowlistDraft,
  type ModelAllowlistApi,
} from "./model_allowlist_admin";

const REV_A = "a".repeat(64);
const REV_B = "b".repeat(64);

function apiFixture(): ModelAllowlistApi {
  return {
    getTenantAllowlist: vi.fn(),
    putTenantAllowlist: vi.fn(),
  };
}

describe("model allowlist admin conflict contract", () => {
  it("does not retry PUT after conflict and reloads current state once", async () => {
    const api = apiFixture();
    vi.mocked(api.putTenantAllowlist).mockRejectedValue(
      new AdminModelApiError(409, "changed", {
        code: "model_allowlist_conflict",
        currentRevision: REV_B,
      }),
    );
    vi.mocked(api.getTenantAllowlist).mockResolvedValue({
      tenantId: "tenant-a",
      modelIds: ["model-a", "model-c"],
      revision: REV_B,
    });

    const outcome = await saveAllowlistDraft(
      api,
      "tenant-a",
      ["model-a", "model-b"],
      REV_A,
    );

    expect(api.putTenantAllowlist).toHaveBeenCalledTimes(1);
    expect(api.getTenantAllowlist).toHaveBeenCalledTimes(1);
    expect(outcome).toEqual({
      kind: "conflict",
      attemptedModelIds: ["model-a", "model-b"],
      current: {
        tenantId: "tenant-a",
        modelIds: ["model-a", "model-c"],
        revision: REV_B,
      },
      diff: {
        onlyInDraft: ["model-b"],
        onlyOnServer: ["model-c"],
      },
    });
  });

  it("does not turn non-conflict failures into a read or retry", async () => {
    const api = apiFixture();
    vi.mocked(api.putTenantAllowlist).mockRejectedValue(
      new AdminModelApiError(503, "unavailable", { code: "database_unavailable" }),
    );

    await expect(
      saveAllowlistDraft(api, "tenant-a", ["model-a"], REV_A),
    ).rejects.toMatchObject({ status: 503 });

    expect(api.putTenantAllowlist).toHaveBeenCalledTimes(1);
    expect(api.getTenantAllowlist).not.toHaveBeenCalled();
  });

  it("returns the successful response without a follow-up read", async () => {
    const api = apiFixture();
    vi.mocked(api.putTenantAllowlist).mockResolvedValue({
      tenantId: "tenant-a",
      modelIds: ["model-a"],
      revision: REV_B,
    });

    const outcome = await saveAllowlistDraft(api, "tenant-a", ["model-a"], REV_A);

    expect(outcome.kind).toBe("saved");
    expect(api.putTenantAllowlist).toHaveBeenCalledTimes(1);
    expect(api.getTenantAllowlist).not.toHaveBeenCalled();
  });
});

describe("model allowlist draft helpers", () => {
  it("preserves the administrator draft while exposing set differences", () => {
    expect(diffModelAllowlist(["model-b", "model-a"], ["model-a", "model-c"])).toEqual({
      onlyInDraft: ["model-b"],
      onlyOnServer: ["model-c"],
    });
  });

  it("does not silently deduplicate model ids", () => {
    const parsed = parseModelIdDraft("model-a\nmodel-b\nmodel-a\n");
    expect(parsed).toEqual(["model-a", "model-b", "model-a"]);
    expect(duplicateModelIds(parsed)).toEqual(["model-a"]);
  });
});
