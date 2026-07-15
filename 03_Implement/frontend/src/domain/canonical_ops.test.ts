import { describe, expect, it } from "vitest";

import { applyCanonicalization } from "./canonical_ops";
import type { DocumentV1 } from "./types";

const baseDoc: DocumentV1 = {
  version: 1,
  id: "doc-1",
  createdAt: "2025-01-01T00:00:00.000Z",
  updatedAt: "2025-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "a", text: "A", x: 10, y: 20 },
    { id: "b", text: "B", x: 50, y: 60 },
    { id: "c", text: "C", x: 100, y: 120 },
  ],
  edges: [],
  islands: [
    { id: "island-with-source", cardIds: ["a", "x"] },
    { id: "island-without-source", cardIds: ["x", "y"] },
  ],
  readingOrder: ["x", "b", "y", "a", "z"],
};

describe("applyCanonicalization", () => {
  it("creates canonical card, links source cards, and updates derived fields without mutating input", () => {
    const result = applyCanonicalization(baseDoc, {
      sourceCardIds: ["a", "b"],
      mergedText: "Merged",
      canonicalId: "canon-1",
    });

    const canonicalCard = result.document.cards.find((card) => card.id === "canon-1");
    expect(canonicalCard).toEqual({
      id: "canon-1",
      text: "Merged",
      x: 30,
      y: 40,
      sources: ["a", "b"],
      textReviewed: false,
    });

    expect(result.document.cards.find((card) => card.id === "a")?.canonicalId).toBe("canon-1");
    expect(result.document.cards.find((card) => card.id === "b")?.canonicalId).toBe("canon-1");

    expect(result.document.islands.find((island) => island.id === "island-with-source")?.cardIds).toEqual([
      "a",
      "x",
      "canon-1",
    ]);
    expect(result.document.islands.find((island) => island.id === "island-without-source")?.cardIds).toEqual([
      "x",
      "y",
    ]);

    expect(result.document.readingOrder).toEqual(["x", "canon-1", "y", "z"]);

    expect(baseDoc.cards).toEqual([
      { id: "a", text: "A", x: 10, y: 20 },
      { id: "b", text: "B", x: 50, y: 60 },
      { id: "c", text: "C", x: 100, y: 120 },
    ]);
    expect(baseDoc.islands.find((island) => island.id === "island-with-source")?.cardIds).toEqual(["a", "x"]);
    expect(baseDoc.readingOrder).toEqual(["x", "b", "y", "a", "z"]);
  });

  it("deduplicates source ids and avoids duplicate canonical in island", () => {
    const doc: DocumentV1 = {
      ...baseDoc,
      islands: [{ id: "island-1", cardIds: ["a", "canon-1"] }],
      readingOrder: ["a", "b", "c"],
    };

    const result = applyCanonicalization(doc, {
      sourceCardIds: ["a", "a", "b"],
      mergedText: "Merged",
      canonicalId: "canon-1",
    });

    expect(result.document.cards.find((card) => card.id === "canon-1")?.sources).toEqual(["a", "b"]);
    expect(result.document.islands[0].cardIds).toEqual(["a", "canon-1"]);
    expect(result.document.readingOrder).toEqual(["canon-1", "c"]);
  });

  it("throws when fewer than two source ids are provided", () => {
    expect(() =>
      applyCanonicalization(baseDoc, {
        sourceCardIds: ["a"],
        mergedText: "Merged",
        canonicalId: "canon-1",
      })
    ).toThrow(/at least 2 source/);
  });

  it("uses canonicalIdFactory when canonicalId is not provided", () => {
    const result = applyCanonicalization(baseDoc, {
      sourceCardIds: ["a", "b"],
      mergedText: "Merged",
      canonicalIdFactory: () => "canon-generated",
    });

    expect(result.canonicalId).toBe("canon-generated");
    expect(result.document.cards.find((card) => card.id === "canon-generated")?.sources).toEqual(["a", "b"]);
  });

  it("throws when neither canonicalId nor canonicalIdFactory is provided", () => {
    expect(() =>
      applyCanonicalization(baseDoc, {
        sourceCardIds: ["a", "b"],
        mergedText: "Merged",
      })
    ).toThrow(/canonicalId or canonicalIdFactory/);
  });
});
