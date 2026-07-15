import { describe, expect, it } from "vitest";

import {
  buildIslandRelationExplanation,
  formatIslandRelationExplanationMarkdown,
  type IslandRelationEdgeSelection,
} from "./island_relation_explain";
import type { DocumentV1 } from "./types";

const document: DocumentV1 = {
  version: 1,
  id: "doc-1",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "card-1", text: "first", x: 0, y: 0 },
    { id: "card-2", text: "second", x: 10, y: 0 },
    { id: "card-3", text: "third", x: 20, y: 0 },
    { id: "card-4", text: "fourth", x: 30, y: 0 },
  ],
  islands: [
    { id: "island-a", title: "Island A", cardIds: ["card-1", "card-4"] },
    { id: "island-b", title: "Island B", cardIds: ["card-2", "card-3"] },
  ],
  edges: [],
  readingOrder: ["card-3", "card-2", "card-1", "card-4"],
};

describe("buildIslandRelationExplanation", () => {
  it("builds persisted edge explanation", () => {
    const selection: IslandRelationEdgeSelection = {
      edgeId: "edge-islands",
      fromIslandId: "island-a",
      toIslandId: "island-b",
      type: "related",
      isDerived: false,
      contributingCardIds: ["card-2", "card-1"],
    };

    const explanation = buildIslandRelationExplanation(document, selection);

    expect(explanation.title).toBe("Relation: Island A ↔ Island B");
    expect(explanation.groundingEdgeIds).toEqual(["edge-islands"]);
    expect(explanation.groundingCardIds).toEqual(["card-2", "card-1"]);
    expect(explanation.body).toContain("Type: RELATED");
    expect(explanation.body).toContain("Grounding cards:");
    expect(explanation.body).not.toContain("derived from");
  });

  it("builds derived edge explanation with deterministic top 10 cards", () => {
    const selection: IslandRelationEdgeSelection = {
      edgeId: "derived-island:island-a|island-b|negate",
      fromIslandId: "island-a",
      toIslandId: "island-b",
      type: "negate",
      isDerived: true,
      contributingEdgeIds: ["edge-2", "edge-1", "edge-2"],
      contributingCardIds: [
        "card-2",
        "card-1",
        "card-4",
        "card-3",
        "card-11",
        "card-10",
        "card-9",
        "card-8",
        "card-7",
        "card-6",
        "card-5",
      ],
    };

    const explanation = buildIslandRelationExplanation(document, selection);

    expect(explanation.groundingEdgeIds).toEqual(["edge-1", "edge-2"]);
    expect(explanation.groundingCardIds).toEqual([
      "card-3",
      "card-2",
      "card-1",
      "card-4",
      "card-10",
      "card-11",
      "card-5",
      "card-6",
      "card-7",
      "card-8",
    ]);
    expect(explanation.body).toContain("Type: NEGATE");
    expect(explanation.body).toContain("This relation is derived from 2 underlying links.");
  });

  it("exports stable markdown", () => {
    const explanation = buildIslandRelationExplanation(document, {
      edgeId: "edge-islands",
      fromIslandId: "island-a",
      toIslandId: "island-b",
      type: "related",
      isDerived: false,
      contributingCardIds: ["card-2", "card-1"],
    });

    expect(formatIslandRelationExplanationMarkdown(explanation)).toMatchInlineSnapshot(`
      "## Relation: Island A ↔ Island B
      
      Type: RELATED
      Grounding cards:
      - card-2: second
      - card-1: first
      
      Grounding edge IDs: edge-islands
      Grounding card IDs: card-2, card-1"
    `);
  });
});
