import { describe, expect, it } from "vitest";

import { diffDocuments } from "./doc_diff";
import type { DocumentV1 } from "../types";

function buildBaseDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2024-01-01T00:00:00.000Z",
    updatedAt: "2024-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-1", text: "a", x: 0, y: 0 },
      { id: "card-2", text: "b", x: 1, y: 1 },
    ],
    edges: [],
    islands: [
      { id: "island-1", cardIds: ["card-1"], summaryText: "sum-a", summaryReviewed: false },
    ],
    relationSummaries: [
      {
        id: "rs-1",
        createdAt: "2024-01-01T00:00:00.000Z",
        islandAId: "island-1",
        islandBId: "island-2",
        relationType: "related",
        derived: false,
        text: "rel-a",
        reviewed: false,
        groundingCardIds: [],
        groundingEdgeIds: [],
        warnings: ["warn-a"],
        sourceSignature: "sig-1",
      },
    ],
    readingOrder: ["card-1", "island-1"],
    narratives: [],
  };
}

describe("diffDocuments", () => {
  it("detects structural changes across cards, islands, relation summaries, and reading order", () => {
    const a = buildBaseDocument();
    const b: DocumentV1 = {
      ...buildBaseDocument(),
      cards: [
        { id: "card-1", text: "a-changed", x: 0, y: 0 },
        { id: "card-3", text: "c", x: 3, y: 3 },
      ],
      islands: [
        { id: "island-1", cardIds: ["card-1", "card-3"], summaryText: "sum-b", summaryReviewed: true },
        { id: "island-2", cardIds: ["card-3"] },
      ],
      relationSummaries: [
        {
          ...a.relationSummaries![0],
          text: "rel-b",
          reviewed: true,
          warnings: ["warn-b"],
        },
        {
          ...a.relationSummaries![0],
          id: "rs-2",
          sourceSignature: "sig-2",
        },
      ],
      readingOrder: ["island-1", "card-1"],
    };

    const diff = diffDocuments(a, b);

    expect(diff.cards.added).toEqual(["card-3"]);
    expect(diff.cards.removed).toEqual(["card-2"]);
    expect(diff.cards.changedText).toEqual([{ id: "card-1", aText: "a", bText: "a-changed" }]);

    expect(diff.islands.added).toEqual(["island-2"]);
    expect(diff.islands.removed).toEqual([]);
    expect(diff.islands.membershipChanged).toEqual([
      { id: "island-1", addedCardIds: ["card-3"], removedCardIds: [] },
    ]);
    expect(diff.islands.summaryChanged).toEqual([
      { id: "island-1", aSummary: "sum-a", bSummary: "sum-b", aReviewed: false, bReviewed: true },
    ]);

    expect(diff.relationSummaries.added).toEqual(["rs-2"]);
    expect(diff.relationSummaries.removed).toEqual([]);
    expect(diff.relationSummaries.changedText).toEqual([{ id: "rs-1", aText: "rel-a", bText: "rel-b" }]);
    expect(diff.relationSummaries.changedReviewed).toEqual([{ id: "rs-1", aReviewed: false, bReviewed: true }]);
    expect(diff.relationSummaries.warningsChanged).toEqual([
      { id: "rs-1", aWarnings: ["warn-a"], bWarnings: ["warn-b"] },
    ]);

    expect(diff.readingOrder.changed).toBe(true);
    expect(diff.readingOrder.firstDifferingIndex).toBe(0);
  });

  it("returns stable, sorted id outputs", () => {
    const base = buildBaseDocument();
    const a: DocumentV1 = {
      ...base,
      cards: [...base.cards, { id: "z", text: "z", x: 0, y: 0 }, { id: "a", text: "a", x: 0, y: 0 }],
      islands: [...base.islands, { id: "z-island", cardIds: [] }, { id: "a-island", cardIds: [] }],
      relationSummaries: [
        ...base.relationSummaries!,
        { ...base.relationSummaries![0], id: "r-z", sourceSignature: "z-sig" },
        { ...base.relationSummaries![0], id: "r-a", sourceSignature: "a-sig" },
      ],
    };

    const diff = diffDocuments(a, base);
    expect(diff.cards.removed).toEqual(["a", "z"]);
    expect(diff.islands.removed).toEqual(["a-island", "z-island"]);
    expect(diff.relationSummaries.removed).toEqual(["r-a", "r-z"]);
  });

  it("tracks relation summary diffs by relation summary id", () => {
    const base = buildBaseDocument();
    const a: DocumentV1 = {
      ...base,
      relationSummaries: [
        { ...base.relationSummaries![0], id: "rs-a", sourceSignature: "same-sig", text: "t1" },
      ],
    };
    const b: DocumentV1 = {
      ...base,
      relationSummaries: [
        { ...base.relationSummaries![0], id: "rs-b", sourceSignature: "same-sig", text: "t2" },
      ],
    };

    const diff = diffDocuments(a, b);
    expect(diff.relationSummaries.added).toEqual(["rs-b"]);
    expect(diff.relationSummaries.removed).toEqual(["rs-a"]);
    expect(diff.relationSummaries.changedText).toEqual([]);
  });

  it("does not mutate input documents", () => {
    const a = buildBaseDocument();
    const b = {
      ...buildBaseDocument(),
      cards: [...buildBaseDocument().cards, { id: "card-3", text: "c", x: 0, y: 0 }],
    } satisfies DocumentV1;

    const aSnapshot = structuredClone(a);
    const bSnapshot = structuredClone(b);

    diffDocuments(a, b);

    expect(a).toEqual(aSnapshot);
    expect(b).toEqual(bSnapshot);
  });


});
