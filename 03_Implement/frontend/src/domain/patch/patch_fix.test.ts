import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import type { PatchDocument } from "./patch_apply";
import { applyFixesToPatch, proposeFixes } from "./patch_fix";
import { lintPatchAgainstCurrentDoc } from "./patch_lint";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-fix",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Card 1", x: 0, y: 0 },
      { id: "c2", text: "Card 2", x: 1, y: 1 },
    ],
    islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
    edges: [],
    relationSummaries: [],
  };
}

describe("patch fix proposals", () => {
  it("proposes and applies safe fixes for P001/P002/P005", () => {
    const currentDoc = makeDoc();
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "op-delete-c2", kind: "delete_card", cardId: "c2" },
        { id: "op-upsert-island", kind: "upsert_island", island: { id: "i1", cardIds: ["c1", "c2", "missing-card"] } },
        {
          id: "op-upsert-edge",
          kind: "upsert_edge",
          edge: { id: "e-missing", fromId: "c1", toId: "missing-card", fromKind: "card", toKind: "card", type: "related" },
        },
        {
          id: "op-upsert-relation",
          kind: "upsert_relation_summary",
          relationSummary: {
            id: "r1",
            createdAt: "2024-01-01T00:00:00.000Z",
            islandAId: "i1",
            islandBId: "i1",
            relationType: "related",
            derived: false,
            text: "summary",
            reviewed: false,
            groundingCardIds: ["missing-card"],
            groundingEdgeIds: ["e-missing"],
            sourceSignature: "sig-1",
          },
        },
      ],
    };

    const lintBefore = lintPatchAgainstCurrentDoc(currentDoc, patch);
    const beforeCodes = new Set(lintBefore.issues.map((issue) => issue.code));
    expect(beforeCodes.has("P001")).toBe(true);
    expect(beforeCodes.has("P002")).toBe(true);
    expect(beforeCodes.has("P005")).toBe(true);

    const proposals = proposeFixes(currentDoc, patch, lintBefore);
    expect(proposals.some((proposal) => proposal.targetIssueCodes.includes("P001"))).toBe(true);
    expect(proposals.some((proposal) => proposal.targetIssueCodes.includes("P002"))).toBe(true);
    expect(proposals.some((proposal) => proposal.targetIssueCodes.includes("P005"))).toBe(true);

    const fixedPatch = applyFixesToPatch(
      patch,
      proposals.map((proposal) => proposal.fixId),
      proposals
    );

    const lintAfter = lintPatchAgainstCurrentDoc(currentDoc, fixedPatch);
    expect(lintAfter.issues.filter((issue) => issue.code === "P001")).toHaveLength(0);
    expect(lintAfter.issues.filter((issue) => issue.code === "P002")).toHaveLength(0);
  });

  it("does not auto-propose unsupported P006/P007 fixes", () => {
    const currentDoc = makeDoc();
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      baseDocSignature: "mismatch:123",
      ops: [
        { id: "dup", kind: "delete_card", cardId: "c1" },
        { id: "dup", kind: "delete_island", islandId: "i1" },
      ],
    };

    const lintResult = lintPatchAgainstCurrentDoc(currentDoc, patch);
    const proposals = proposeFixes(currentDoc, patch, lintResult);

    expect(proposals.some((proposal) => proposal.targetIssueCodes.includes("P006"))).toBe(false);
    expect(proposals.some((proposal) => proposal.targetIssueCodes.includes("P007"))).toBe(false);
  });
});
