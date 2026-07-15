import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { applyPatchWithResolutions, applyPatchWithResolutionsDetailed, type PatchDocument } from "./patch_apply";

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
    evidenceLinks: [],
  };
}

describe("applyPatchWithResolutions", () => {
  it("applies only resolved 'theirs' in conflicts", () => {
    const baseline = makeDoc("base");
    const current = makeDoc("yours");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "upsert_card", card: { id: "c1", text: "theirs", x: 0, y: 0 } }],
    };

    const withSkip = applyPatchWithResolutions(current, patch, { op1: "skip" }, baseline);
    expect(withSkip.cards[0]?.text).toBe("yours");

    const withTheirs = applyPatchWithResolutions(current, patch, { op1: "theirs" }, baseline);
    expect(withTheirs.cards[0]?.text).toBe("theirs");
  });

  it("applies selected non-conflicting operations", () => {
    const current = makeDoc("base");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "op1", kind: "upsert_card", card: { id: "c1", text: "next", x: 0, y: 0 } },
        { id: "op2", kind: "upsert_card", card: { id: "c2", text: "new", x: 1, y: 1 } },
      ],
    };

    const next = applyPatchWithResolutions(current, patch, {}, undefined, new Set(["op2"]));
    expect(next.cards.find((card) => card.id === "c1")?.text).toBe("base");
    expect(next.cards.find((card) => card.id === "c2")?.text).toBe("new");
  });

  it("falls back to H4 behavior without baseline", () => {
    const current = makeDoc("base");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "upsert_card", card: { id: "c1", text: "theirs", x: 0, y: 0 } }],
    };

    const next = applyPatchWithResolutions(current, patch, { op1: "skip" }, undefined, new Set(["op1"]));
    expect(next.cards[0]?.text).toBe("theirs");
  });

  it("collects applied op ids and conflict choices", () => {
    const baseline = makeDoc("base");
    const current = makeDoc("yours");
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "op1", kind: "upsert_card", card: { id: "c1", text: "theirs", x: 0, y: 0 } },
        { id: "op2", kind: "upsert_card", card: { id: "c2", text: "new", x: 1, y: 1 } },
      ],
    };

    const result = applyPatchWithResolutionsDetailed(current, patch, { op1: "yours" }, baseline, new Set(["op1", "op2"]));

    expect(result.meta.appliedOpIds).toEqual(["op2"]);
    expect(result.meta.stats.upsertCards).toBe(1);
    expect(result.meta.conflictMeta).toEqual({
      totalConflicts: 1,
      chosenYours: 1,
      chosenTheirs: 0,
      chosenSkip: 0,
    });
  });


  it("removes evidence links that reference a deleted card", () => {
    const current = makeDoc("base");
    current.cards.push({ id: "c2", text: "other", x: 1, y: 1 });
    current.evidenceLinks = [{ id: "el-1", type: "supports", fromCardId: "c1", toCardId: "c2" }];

    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op1", kind: "delete_card", cardId: "c1" }],
    };

    const next = applyPatchWithResolutions(current, patch, {}, undefined, new Set(["op1"]));
    expect(next.evidenceLinks).toEqual([]);
  });

});
