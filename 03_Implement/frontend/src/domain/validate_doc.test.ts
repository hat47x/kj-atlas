import { describe, expect, it } from "vitest";

import { validateDocumentV2Strict } from "./validate_doc";

describe("validateDocumentV2Strict", () => {
  const now = new Date().toISOString();

  const validDocument = {
    version: 2,
    id: "doc_v2",
    createdAt: now,
    updatedAt: now,
    transform: {
      panX: 0,
      panY: 0,
      zoom: 1,
    },
    cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
    edges: [],
    islands: [],
  };

  it("accepts valid DocumentV2", () => {
    const result = validateDocumentV2Strict(validDocument);
    expect(result.ok).toBe(true);
  });

  it("accepts patchApplyLog entries", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      patchApplyLog: [
        {
          id: "log-1",
          createdAt: now,
          patchVersion: "1",
          patchTitle: "sample.patch.json",
          baseDocSignature: "doc_v2:base",
          patchSourceSignature: "fnv1a:1234abcd",
          appliedOpIds: ["op-1"],
          stats: {
            upsertCards: 1,
            deleteCards: 0,
            upsertIslands: 0,
            deleteIslands: 0,
            upsertEdges: 0,
            deleteEdges: 0,
            upsertRelationSummaries: 0,
            deleteRelationSummaries: 0,
          },
          conflictMeta: {
            totalConflicts: 1,
            chosenYours: 0,
            chosenTheirs: 1,
            chosenSkip: 0,
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("rejects unknown root fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      unknownField: true,
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      return;
    }

    expect(result.errors).toContain("document: unknown field 'unknownField'");
  });

  it("rejects v1 payload", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      version: 1,
    });

    expect(result.ok).toBe(false);
    if (result.ok) {
      return;
    }

    expect(result.errors).toContain("document.version: must be the number 2 (DocumentV2 only)");
  });
});
