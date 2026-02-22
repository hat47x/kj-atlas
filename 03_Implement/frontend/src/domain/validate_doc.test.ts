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

  it("rejects unknown root fields", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      unknownField: true,
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("document: unknown field 'unknownField'");
  });

  it("accepts polygon geometry", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
              { x: 100, y: 100 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("accepts legacy polygon geometry payload", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            polygon: {
              points: [
                { x: 0, y: 0 },
                { x: 100, y: 0 },
                { x: 100, y: 100 },
              ],
            },
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("rejects polygon shape with fewer than 3 points", () => {
    const result = validateDocumentV2Strict({
      ...validDocument,
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(false);
    if (result.ok) return;

    expect(result.errors).toContain("islands[0].shape.points: must contain at least 3 points for polygon");
  });
});
