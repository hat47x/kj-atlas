import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../types";
import { computeDiagramStructuralMetrics } from "./structural_metrics";

function makeDoc(partial: Partial<DocumentV2>): DocumentV2 {
  return {
    version: 2,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    ...partial,
  };
}

describe("computeDiagramStructuralMetrics", () => {
  it("computes whole-diagram structural metrics deterministically", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "1", x: 0, y: 0 },
        { id: "c2", text: "2", x: 1, y: 0 },
        { id: "c3", text: "3", x: 2, y: 0 },
        { id: "c4", text: "4", x: 3, y: 0 },
      ],
      islands: [
        { id: "i1", cardIds: ["c1", "c2"], shape: { kind: "rect" } },
        { id: "i2", cardIds: ["c3"], shape: { kind: "rect" } },
        { id: "i3", cardIds: ["c4", "c4", "missing"], shape: { kind: "rect" } },
      ],
      edges: [
        { id: "r1", fromId: "c1", toId: "c3", type: "related" },
        { id: "r2", fromId: "c4", toId: "c1", type: "negate" },
      ],
      evidenceLinks: [
        { id: "e1", fromCardId: "c1", toCardId: "c2", type: "supports" },
        { id: "e2", fromCardId: "c3", toCardId: "c1", type: "contradicts" },
      ],
    });

    expect(computeDiagramStructuralMetrics(doc)).toEqual({
      cardCount: 4,
      islandCount: 3,
      evidenceLinkDensity: 0.1667,
      isolatedCardsCount: 1,
      islandSizeDistribution: [
        { size: 1, islands: 2 },
        { size: 2, islands: 1 },
      ],
      contradictionRatio: 0.5,
    });
  });

  it("sets contradictionRatio to null when typed relations are unavailable", () => {
    const doc = makeDoc({
      cards: [{ id: "c1", text: "1", x: 0, y: 0 }],
      islands: [{ id: "i1", cardIds: ["c1"], shape: { kind: "rect" } }],
    });

    expect(computeDiagramStructuralMetrics(doc).contradictionRatio).toBeNull();
  });

  it("derives contradictionRatio from edge relation types when evidence links are absent", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "1", x: 0, y: 0 },
        { id: "c2", text: "2", x: 1, y: 0 },
      ],
      edges: [
        { id: "e1", fromId: "c1", toId: "c2", type: "related" },
        { id: "e2", fromId: "c2", toId: "c1", type: "negate" },
      ],
      islands: [{ id: "i1", cardIds: ["c1", "c2"], shape: { kind: "rect" } }],
    });

    expect(computeDiagramStructuralMetrics(doc).contradictionRatio).toBe(0.5);
  });

});
