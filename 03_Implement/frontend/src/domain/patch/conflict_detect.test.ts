import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { detectPatchConflicts } from "./conflict_detect";
import type { PatchDocument } from "./patch_apply";

function makeDoc(text: string): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text, x: 0, y: 0 }],
    edges: [],
    islands: [],
    narratives: [],
  };
}

describe("detectPatchConflicts", () => {
  it("detects divergent updates on same entity", () => {
    const baseline = makeDoc("base");
    const current = makeDoc("yours");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "upsert_card", card: { id: "c1", text: "theirs", x: 0, y: 0 } }],
    };

    const report = detectPatchConflicts(baseline, current, patch);

    expect(report.conflicts).toHaveLength(1);
    expect(report.conflicts[0]?.opId).toBe("op1");
    expect(report.nonConflictingOpIds).toHaveLength(0);
  });

  it("does not flag conflict when only patch side changed", () => {
    const baseline = makeDoc("base");
    const current = makeDoc("base");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "upsert_card", card: { id: "c1", text: "theirs", x: 0, y: 0 } }],
    };

    const report = detectPatchConflicts(baseline, current, patch);

    expect(report.conflicts).toHaveLength(0);
    expect(report.nonConflictingOpIds).toEqual(["op1"]);
  });

  it("detects update-vs-delete conflicts", () => {
    const baseline = makeDoc("base");
    const current = makeDoc("updated-by-you");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "delete_card", cardId: "c1" }],
    };

    const report = detectPatchConflicts(baseline, current, patch);

    expect(report.conflicts).toHaveLength(1);
    expect(report.conflicts[0]?.reason).toBe("update vs delete");
  });
});
