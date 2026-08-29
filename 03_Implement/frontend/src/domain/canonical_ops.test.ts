import { describe, expect, it } from "vitest";

import { applyCanonicalization } from "./canonical_ops";
import { checkIslandMembershipIntegrity } from "./validate_doc";
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

  // DOMAIN-ISLAND-MEMBERSHIP-01 AC-2 (F-5 / R2(a), canonicalization write path).
  // This pins CURRENT behavior; it is not an endorsement of it. updateIslands()
  // decides each island against the ORIGINAL cardIds in a single map() pass and
  // has no "remove from the other islands" step (unlike moveCardToIsland() in
  // island_edge_aggregate.ts), so a merge whose sources span two islands puts
  // the canonical card in BOTH. Which island such a merge result should belong
  // to is an open product question the issue explicitly defers, so the behavior
  // is left unchanged here and only made visible.
  it("adds the canonical card to both islands when source cards span two islands", () => {
    const doc: DocumentV1 = {
      ...baseDoc,
      islands: [
        { id: "island-a", cardIds: ["a", "x"] },
        { id: "island-b", cardIds: ["b", "y"] },
      ],
    };

    const result = applyCanonicalization(doc, {
      sourceCardIds: ["a", "b"],
      mergedText: "Merged",
      canonicalId: "canon-1",
    });

    // Current behavior: added to both, and neither source card is removed.
    expect(result.document.islands.find((island) => island.id === "island-a")?.cardIds).toEqual([
      "a",
      "x",
      "canon-1",
    ]);
    expect(result.document.islands.find((island) => island.id === "island-b")?.cardIds).toEqual([
      "b",
      "y",
      "canon-1",
    ]);

    // ...which is exactly the cross-island duplicate membership that the
    // advisory diagnostic added by AC-1 exists to surface (advisory only —
    // the document stays valid and saveable).
    expect(checkIslandMembershipIntegrity(result.document)).toEqual([
      "islands: card 'canon-1' belongs to 2 islands (island-a, island-b): a card should belong to at most one island",
    ]);
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
