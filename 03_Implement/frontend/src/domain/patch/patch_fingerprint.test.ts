import { describe, expect, it } from "vitest";
import type { PatchV1 } from "./patch_types";
import { canonicalizeJson, computePatchFingerprint, verifyPatchFingerprint } from "./patch_fingerprint";

describe("patch_fingerprint", () => {
  it("canonicalizeJson sorts object keys and normalizes ops by op id", () => {
    const value = {
      b: 1,
      a: {
        z: true,
        y: [
          { id: "2", kind: "delete_card", cardId: "c2" },
          { id: "1", kind: "delete_card", cardId: "c1" },
        ],
      },
      ops: [
        { id: "op-b", kind: "delete_card", cardId: "c2" },
        { id: "op-a", kind: "delete_card", cardId: "c1" },
      ],
    };

    expect(canonicalizeJson(value)).toContain('"ops":[{"cardId":"c1","id":"op-a","kind":"delete_card"},{"cardId":"c2","id":"op-b","kind":"delete_card"}]');
  });

  it("compute/verify fingerprint", async () => {
    const patch: PatchV1 = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op-1", kind: "delete_card", cardId: "c1" }],
    };

    const patchFingerprint = await computePatchFingerprint(patch);
    const verified = await verifyPatchFingerprint({ ...patch, patchFingerprint });
    expect(verified.ok).toBe(true);

    const mismatch = await verifyPatchFingerprint({ ...patch, patchFingerprint: "deadbeef" });
    expect(mismatch.ok).toBe(false);
    expect(mismatch.actual).toBe(patchFingerprint);
  });
});
