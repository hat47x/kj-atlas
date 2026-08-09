import { describe, expect, it } from "vitest";

import { getDerivedIslandEdges, getIslandsForCard, moveCardToIsland } from "./island_edge_aggregate";
import type { DocumentV1, Island } from "./types";

const baseDocument: DocumentV1 = {
  version: 1,
  id: "doc",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "card-a", text: "A", x: 0, y: 0 },
    { id: "card-b", text: "B", x: 100, y: 0 },
    { id: "card-c", text: "C", x: 200, y: 0 },
    { id: "card-z", text: "Z", x: 300, y: 0 },
  ],
  islands: [
    { id: "island-a", cardIds: ["card-a", "card-z"] },
    { id: "island-b", cardIds: ["card-b"] },
    { id: "island-c", cardIds: ["card-c"] },
  ],
  edges: [],
};

describe("getIslandsForCard", () => {
  it("returns direct memberships", () => {
    expect(getIslandsForCard(baseDocument, "card-a")).toEqual(["island-a"]);
    expect(getIslandsForCard(baseDocument, "card-z")).toEqual(["island-a"]);
  });

  it("returns empty for lone wolf cards", () => {
    expect(getIslandsForCard(baseDocument, "missing-card")).toEqual([]);
  });
});

describe("getDerivedIslandEdges", () => {
  it("derives island edges from card and mixed endpoints with provenance", () => {
    const document: DocumentV1 = {
      ...baseDocument,
      edges: [
        { id: "e1", fromId: "card-a", toId: "card-b", type: "related" },
        { id: "e2", fromId: "card-z", toId: "card-b", type: "related" },
        { id: "e3", fromId: "card-c", toId: "island-b", toKind: "island", type: "negate" },
        { id: "e4", fromId: "island-a", fromKind: "island", toId: "island-c", toKind: "island", type: "related" },
      ],
    };

    expect(getDerivedIslandEdges(document)).toEqual([
      {
        id: "derived-island:island-a|island-b|related",
        fromId: "island-a",
        toId: "island-b",
        fromKind: "island",
        toKind: "island",
        type: "related",
        isDerived: true,
        aggregateCount: 2,
        contributingEdgeIds: ["e1", "e2"],
        contributingCardIds: ["card-a", "card-b", "card-z"],
      },
      {
        id: "derived-island:island-b|island-c|negate",
        fromId: "island-b",
        toId: "island-c",
        fromKind: "island",
        toKind: "island",
        type: "negate",
        isDerived: true,
        aggregateCount: 1,
        contributingEdgeIds: ["e3"],
        contributingCardIds: ["card-c"],
      },
    ]);
  });

  it("does not derive from persisted island-to-island edges", () => {
    const document: DocumentV1 = {
      ...baseDocument,
      edges: [{ id: "e-islands", fromId: "island-a", fromKind: "island", toId: "island-b", toKind: "island", type: "related" }],
    };

    expect(getDerivedIslandEdges(document)).toEqual([]);
  });

  it("ignores dangling references to a card id that does not exist in the document", () => {
    const document: DocumentV1 = {
      ...baseDocument,
      edges: [{ id: "e-lone", fromId: "card-z", toId: "outside", type: "related" }],
    };

    expect(getDerivedIslandEdges(document)).toEqual([]);
  });

  it("ignores edges between two genuine lone-wolf cards (no island involvement at all)", () => {
    const document: DocumentV1 = {
      ...baseDocument,
      cards: [...baseDocument.cards, { id: "card-lone1", text: "L1", x: 400, y: 0 }, { id: "card-lone2", text: "L2", x: 500, y: 0 }],
      edges: [{ id: "e-lone-lone", fromId: "card-lone1", toId: "card-lone2", type: "related" }],
    };

    expect(getDerivedIslandEdges(document)).toEqual([]);
  });

  it("promotes a relation to a real lone-wolf card into an island<->card derived edge (UX-SCALE-01 d)", () => {
    const document: DocumentV1 = {
      ...baseDocument,
      cards: [...baseDocument.cards, { id: "card-lone", text: "Lone", x: 400, y: 0 }],
      edges: [
        { id: "e-promote-1", fromId: "card-a", toId: "card-lone", type: "related" },
        { id: "e-promote-2", fromId: "card-z", toId: "card-lone", type: "related" },
      ],
    };

    expect(getDerivedIslandEdges(document)).toEqual([
      {
        id: "derived-card:island-a|card-lone|related",
        fromId: "island-a",
        toId: "card-lone",
        fromKind: "island",
        toKind: "card",
        type: "related",
        isDerived: true,
        aggregateCount: 2,
        contributingEdgeIds: ["e-promote-1", "e-promote-2"],
        contributingCardIds: ["card-a", "card-lone", "card-z"],
      },
    ]);
  });
});

describe("moveCardToIsland", () => {
  const islands: Island[] = [
    { id: "island-a", cardIds: ["card-a", "card-z"] },
    { id: "island-b", cardIds: ["card-b"] },
    { id: "island-c", cardIds: ["card-c"] },
  ];

  it("removes the card from its prior island while adding it to the target (R2(a))", () => {
    const next = moveCardToIsland(islands, "card-a", "island-b");

    expect(next.find((island) => island.id === "island-a")?.cardIds).toEqual(["card-z"]);
    expect(next.find((island) => island.id === "island-b")?.cardIds).toEqual(["card-b", "card-a"]);
    expect(next.find((island) => island.id === "island-c")?.cardIds).toEqual(["card-c"]);
  });

  it("removes the card from every island it belongs to, not just the first match", () => {
    const multiMembership: Island[] = [
      { id: "island-a", cardIds: ["card-a"] },
      { id: "island-b", cardIds: ["card-a", "card-b"] },
      { id: "island-c", cardIds: ["card-c"] },
    ];

    const next = moveCardToIsland(multiMembership, "card-a", "island-c");

    expect(next.find((island) => island.id === "island-a")?.cardIds).toEqual([]);
    expect(next.find((island) => island.id === "island-b")?.cardIds).toEqual(["card-b"]);
    expect(next.find((island) => island.id === "island-c")?.cardIds).toEqual(["card-c", "card-a"]);
  });

  it("is a no-op (same array reference) when the card is already the target's sole member", () => {
    const next = moveCardToIsland(islands, "card-b", "island-b");
    expect(next).toBe(islands);
  });

  it("does not mutate islands that never contained the card and are not the target", () => {
    const next = moveCardToIsland(islands, "card-a", "island-b");
    const unaffected = next.find((island) => island.id === "island-c");
    expect(unaffected).toBe(islands[2]);
  });
});
