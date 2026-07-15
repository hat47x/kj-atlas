import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import type { PatchDocument } from "./patch_apply";
import { lintPatchAgainstCurrentDoc } from "./patch_lint";

function makeDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "base", x: 0, y: 0 }],
    islands: [{ id: "i1", cardIds: ["c1"] }],
    edges: [],
    relationSummaries: [],
    evidenceLinks: [],
  };
}

describe("lintPatchAgainstCurrentDoc", () => {
  it("returns P001 error for islands referencing missing cards", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op-island", kind: "upsert_island", island: { id: "i2", cardIds: ["missing-card"] } }],
    };

    const result = lintPatchAgainstCurrentDoc(makeDoc(), patch);
    expect(result.issues.some((issue) => issue.code === "P001" && issue.severity === "error" && issue.opId === "op-island")).toBe(true);
  });

  it("returns P007 for duplicate op ids", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "dup", kind: "delete_card", cardId: "c1" },
        { id: "dup", kind: "delete_island", islandId: "i1" },
      ],
    };

    const result = lintPatchAgainstCurrentDoc(makeDoc(), patch);
    expect(result.issues.some((issue) => issue.code === "P007" && issue.severity === "error" && issue.opId === "dup")).toBe(true);
  });

  it("attributes P002 to delete op when island endpoint is removed", () => {
    const doc = makeDoc();
    doc.edges = [{ id: "e1", fromId: "i1", toId: "c1", fromKind: "island", toKind: "card", type: "related" }];

    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op-delete-island", kind: "delete_island", islandId: "i1" }],
    };

    const result = lintPatchAgainstCurrentDoc(doc, patch);
    expect(result.issues.some((issue) => issue.code === "P002" && issue.opId === "op-delete-island")).toBe(true);
  });

  it("returns warnings without blocking codes for delete-card hazards", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [{ id: "op-delete", kind: "delete_card", cardId: "c1" }],
    };

    const result = lintPatchAgainstCurrentDoc(makeDoc(), patch);

    expect(result.issues.some((issue) => issue.code === "P003" && issue.severity === "warn" && issue.opId === "op-delete")).toBe(true);
    expect(result.issues.some((issue) => issue.code === "P001" && issue.severity === "error")).toBe(true);
  });

  it("returns P009 for evidence links referencing missing cards", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        {
          id: "op-evidence",
          kind: "upsert_evidence_link",
          evidenceLink: { id: "el-1", type: "supports", fromCardId: "c1", toCardId: "missing" },
        },
      ],
    };

    const result = lintPatchAgainstCurrentDoc(makeDoc(), patch);
    expect(result.issues.some((issue) => issue.code === "P009" && issue.severity === "error" && issue.opId === "op-evidence")).toBe(true);
  });

});
