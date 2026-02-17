import { describe, expect, it } from "vitest";
import { buildPatchForExport } from "./patch_generate";
import { verifyPatchFingerprint } from "./patch_fingerprint";

describe("patch_generate", () => {
  it("embeds patchFingerprint and metadata", async () => {
    const patch = await buildPatchForExport(
      {
        kind: "kj-atlas-patch",
        version: 1,
        ops: [{ id: "op-1", kind: "delete_card", cardId: "c1" }],
      },
      { author: "A", authorNote: "note", sourceApp: "kj-atlas" }
    );

    expect(typeof patch.patchFingerprint).toBe("string");
    expect(patch.author).toBe("A");
    expect((await verifyPatchFingerprint(patch)).ok).toBe(true);
    expect((await verifyPatchFingerprint({ ...patch, ops: [{ id: "op-1", kind: "delete_card", cardId: "c2" }] })).ok).toBe(false);
  });
});
