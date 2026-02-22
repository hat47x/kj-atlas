import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../types";
import { computeStructureMetrics } from "./structural_metrics";

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

describe("computeStructureMetrics", () => {
  it("computes whole-diagram structural metrics deterministically", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "SECRET-1", x: 0, y: 0, textReviewed: true },
        { id: "c2", text: "SECRET-2", x: 1, y: 0, textReviewed: false },
        { id: "c3", text: "SECRET-3", x: 2, y: 0 },
        { id: "c4", text: "SECRET-4", x: 3, y: 0 },
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

    expect(computeStructureMetrics(doc)).toEqual({
      cardCount: 4,
      islandCount: 3,
      evidenceLinkCount: 2,
      evidenceLinkDensity: 0.5,
      isolatedCardCount: 0,
      islandSizeDistribution: [
        { size: 1, islands: 2 },
        { size: 2, islands: 1 },
      ],
      contradictionRatio: 0.5,
      reviewedCoverage: 0.25,
    });
  });

  it("omits optional ratios when typed relations and reviewed flags are unavailable", () => {
    const doc = makeDoc({
      cards: [{ id: "c1", text: "1", x: 0, y: 0 }],
      islands: [{ id: "i1", cardIds: ["c1"], shape: { kind: "rect" } }],
    });

    const metrics = computeStructureMetrics(doc);
    expect(metrics.contradictionRatio).toBeNull();
    expect(metrics.reviewedCoverage).toBeNull();
  });

  it("is unchanged by export/import round-trip", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "Alpha", x: 0, y: 0, textReviewed: true },
        { id: "c2", text: "Beta", x: 1, y: 0, textReviewed: false },
      ],
      islands: [{ id: "i1", cardIds: ["c1", "c2"], shape: { kind: "rect" } }],
      evidenceLinks: [{ id: "e1", fromCardId: "c1", toCardId: "c2", type: "supports" }],
    });

    const before = computeStructureMetrics(doc);
    const roundTrip = JSON.parse(JSON.stringify(doc)) as DocumentV2;
    const after = computeStructureMetrics(roundTrip);
    expect(after).toEqual(before);
  });
});
