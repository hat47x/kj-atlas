import { describe, expect, it } from "vitest";

import { getDerivedIslandEdges, getIslandsForCard } from "./island_edge_aggregate";
import type { DocumentV2 } from "./types";

const baseDocument: DocumentV2 = {
  version: 2,
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
    const document: DocumentV2 = {
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
    const document: DocumentV2 = {
      ...baseDocument,
      edges: [{ id: "e-islands", fromId: "island-a", fromKind: "island", toId: "island-b", toKind: "island", type: "related" }],
    };

    expect(getDerivedIslandEdges(document)).toEqual([]);
  });

  it("ignores lone-wolf contributions", () => {
    const document: DocumentV2 = {
      ...baseDocument,
      edges: [{ id: "e-lone", fromId: "card-z", toId: "outside", type: "related" }],
    };

    expect(getDerivedIslandEdges(document)).toEqual([]);
  });
});
