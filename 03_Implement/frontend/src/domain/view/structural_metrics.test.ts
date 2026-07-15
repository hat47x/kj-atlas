import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../types";
import { computeStructureMetrics } from "./structural_metrics";

function makeDoc(partial: Partial<DocumentV1>): DocumentV1 {
  return {
    version: 1,
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
      isolationRate: 0,
      connectedComponentCount: 1,
      largestComponentRatio: 1,
      connectivityScore: 1,
      averageDegree: 1.5,
      degreeP95: 3,
      degreeSkewRatio: 2,
      bridgeEdgeCount: 3,
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
    expect(metrics.connectedComponentCount).toBe(1);
    expect(metrics.isolationRate).toBe(1);
    expect(metrics.largestComponentRatio).toBe(1);
    expect(metrics.connectivityScore).toBe(1);
    expect(metrics.averageDegree).toBe(0);
    expect(metrics.degreeP95).toBe(0);
    expect(metrics.degreeSkewRatio).toBe(0);
    expect(metrics.bridgeEdgeCount).toBe(0);
  });

  it("detects disconnected and skewed structures", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "1", x: 0, y: 0 },
        { id: "c2", text: "2", x: 1, y: 0 },
        { id: "c3", text: "3", x: 2, y: 0 },
        { id: "c4", text: "4", x: 3, y: 0 },
        { id: "c5", text: "5", x: 4, y: 0 },
        { id: "c6", text: "6", x: 5, y: 0 },
      ],
      islands: [
        { id: "i1", cardIds: ["c1", "c2", "c3", "c4", "c5"], shape: { kind: "rect" } },
        { id: "i2", cardIds: ["c6"], shape: { kind: "rect" } },
      ],
      evidenceLinks: [
        { id: "e1", fromCardId: "c1", toCardId: "c2", type: "supports" },
        { id: "e2", fromCardId: "c1", toCardId: "c3", type: "supports" },
        { id: "e3", fromCardId: "c1", toCardId: "c4", type: "supports" },
        { id: "e4", fromCardId: "c1", toCardId: "c5", type: "supports" },
      ],
    });

    const metrics = computeStructureMetrics(doc);
    expect(metrics.connectedComponentCount).toBe(2);
    expect(metrics.largestComponentRatio).toBe(0.8333);
    expect(metrics.connectivityScore).toBe(0.8);
    expect(metrics.averageDegree).toBe(1.3333);
    expect(metrics.degreeP95).toBe(4);
    expect(metrics.degreeSkewRatio).toBe(3);
    expect(metrics.bridgeEdgeCount).toBe(4);
    expect(metrics.isolatedCardCount).toBe(1);
    expect(metrics.isolationRate).toBe(0.1667);
  });

  it("treats self-loop-only cards as isolated", () => {
    const doc = makeDoc({
      cards: [{ id: "c1", text: "solo", x: 0, y: 0 }],
      islands: [{ id: "i1", cardIds: ["c1"], shape: { kind: "rect" } }],
      evidenceLinks: [{ id: "e1", fromCardId: "c1", toCardId: "c1", type: "supports" }],
    });

    const metrics = computeStructureMetrics(doc);
    expect(metrics.evidenceLinkCount).toBe(1);
    expect(metrics.isolatedCardCount).toBe(1);
    expect(metrics.isolationRate).toBe(1);
    expect(metrics.connectedComponentCount).toBe(1);
    expect(metrics.connectivityScore).toBe(1);
    expect(metrics.averageDegree).toBe(0);
    expect(metrics.degreeP95).toBe(0);
    expect(metrics.degreeSkewRatio).toBe(0);
    expect(metrics.bridgeEdgeCount).toBe(0);
  });

  it("ignores malformed relation endpoints and non-card edges for graph metrics", () => {
    const doc = makeDoc({
      cards: [
        { id: "c1", text: "1", x: 0, y: 0 },
        { id: "c2", text: "2", x: 1, y: 0 },
        { id: "c3", text: "3", x: 2, y: 0 },
      ],
      edges: [
        { id: "r1", fromId: "c1", toId: "c2", type: "related" },
        { id: "r2", fromId: "c1", toId: "unknown", type: "related" },
        { id: "r3", fromId: "c2", toId: "c3", type: "related", toKind: "island" },
      ],
      evidenceLinks: [
        { id: "e1", fromCardId: "c2", toCardId: "c2", type: "supports" },
        { id: "e2", fromCardId: "c2", toCardId: "missing", type: "supports" },
      ],
      islands: [{ id: "i1", cardIds: ["c1", "c2", "c3"], shape: { kind: "rect" } }],
    });

    const metrics = computeStructureMetrics(doc);
    expect(metrics.evidenceLinkCount).toBe(1);
    expect(metrics.connectedComponentCount).toBe(2);
    expect(metrics.largestComponentRatio).toBe(0.6667);
    expect(metrics.connectivityScore).toBe(0.5);
    expect(metrics.averageDegree).toBe(0.6667);
    expect(metrics.degreeP95).toBe(1);
    expect(metrics.degreeSkewRatio).toBe(1);
    expect(metrics.bridgeEdgeCount).toBe(1);
    expect(metrics.isolatedCardCount).toBe(1);
    expect(metrics.isolationRate).toBe(0.3333);
  });

  it("is deterministic regardless of evidence/edge input order", () => {
    const baseDoc = makeDoc({
      cards: [
        { id: "c1", text: "1", x: 0, y: 0 },
        { id: "c2", text: "2", x: 1, y: 0 },
        { id: "c3", text: "3", x: 2, y: 0 },
        { id: "c4", text: "4", x: 3, y: 0 },
      ],
      edges: [
        { id: "r1", fromId: "c1", toId: "c2", type: "related" },
        { id: "r2", fromId: "c3", toId: "c2", type: "related" },
      ],
      evidenceLinks: [
        { id: "e1", fromCardId: "c2", toCardId: "c4", type: "supports" },
        { id: "e2", fromCardId: "c1", toCardId: "c3", type: "supports" },
      ],
    });

    const shuffledDoc = makeDoc({
      ...baseDoc,
      edges: [...baseDoc.edges].reverse(),
      evidenceLinks: [...(baseDoc.evidenceLinks ?? [])].reverse(),
    });

    expect(computeStructureMetrics(shuffledDoc)).toEqual(computeStructureMetrics(baseDoc));
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
    const roundTrip = JSON.parse(JSON.stringify(doc)) as DocumentV1;
    const after = computeStructureMetrics(roundTrip);
    expect(after).toEqual(before);
  });
});
