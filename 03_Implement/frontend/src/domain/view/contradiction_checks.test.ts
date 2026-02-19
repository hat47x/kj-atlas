import { describe, expect, it } from "vitest";

import { analyzeContradictions } from "./contradiction_checks";
import type { DocumentV2 } from "../types";

function createBaseDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [
      { id: "island-a", cardIds: [], summaryText: "導入" },
      { id: "island-b", cardIds: [] },
    ],
    relationSummaries: [],
  };
}

describe("analyzeContradictions", () => {
  it("detects C001 when same island pair has related + negate edges", () => {
    const doc = createBaseDoc();
    doc.edges = [
      { id: "edge-1", fromId: "island-a", toId: "island-b", fromKind: "island", toKind: "island", type: "related" },
      { id: "edge-2", fromId: "island-b", toId: "island-a", fromKind: "island", toKind: "island", type: "negate" },
    ];

    const report = analyzeContradictions(doc, "2026-01-01T00:00:00.000Z");
    const c001 = report.signals.find((signal) => signal.code === "C001");

    expect(c001).toBeDefined();
    expect(c001?.severity).toBe("warn");
    expect(c001?.entityRefs.some((entity) => entity.kind === "edge" && entity.idOrSignature === "edge-1")).toBe(true);
    expect(c001?.entityRefs.some((entity) => entity.kind === "edge" && entity.idOrSignature === "edge-2")).toBe(true);
  });

  it("is deterministic for the same document", () => {
    const doc = createBaseDoc();
    doc.edges = [
      { id: "edge-1", fromId: "island-a", toId: "island-b", fromKind: "island", toKind: "island", type: "related" },
      { id: "edge-2", fromId: "island-b", toId: "island-a", fromKind: "island", toKind: "island", type: "negate" },
    ];
    doc.relationSummaries = [
      {
        id: "summary-1",
        createdAt: "2026-01-01T00:00:00.000Z",
        islandAId: "island-a",
        islandBId: "island-b",
        relationType: "related",
        derived: false,
        text: "一方で差異がある",
        reviewed: true,
        groundingCardIds: [],
        groundingEdgeIds: [],
        sourceSignature: "sig-1",
      },
      {
        id: "summary-2",
        createdAt: "2026-01-01T00:00:00.000Z",
        islandAId: "island-b",
        islandBId: "island-a",
        relationType: "related",
        derived: false,
        text: "同じ方向を支持する",
        reviewed: true,
        groundingCardIds: [],
        groundingEdgeIds: [],
        sourceSignature: "sig-2",
      },
    ];

    const first = analyzeContradictions(doc, "2026-01-01T00:00:00.000Z");
    const second = analyzeContradictions(doc, "2026-01-01T00:00:00.000Z");

    expect(second).toEqual(first);
  });

  it("detects C003 only when conflict/alignment markers exist across different summaries", () => {
    const doc = createBaseDoc();
    doc.relationSummaries = [
      {
        id: "summary-1",
        createdAt: "2026-01-01T00:00:00.000Z",
        islandAId: "island-a",
        islandBId: "island-b",
        relationType: "related",
        derived: false,
        text: "しかし視点は異なる",
        reviewed: true,
        groundingCardIds: [],
        groundingEdgeIds: [],
        sourceSignature: "sig-1",
      },
      {
        id: "summary-2",
        createdAt: "2026-01-01T00:00:00.000Z",
        islandAId: "island-a",
        islandBId: "island-b",
        relationType: "related",
        derived: false,
        text: "同じ方向を支持する",
        reviewed: true,
        groundingCardIds: [],
        groundingEdgeIds: [],
        sourceSignature: "sig-2",
      },
    ];

    const report = analyzeContradictions(doc, "2026-01-01T00:00:00.000Z");
    expect(report.signals.some((signal) => signal.code === "C003")).toBe(true);

    doc.relationSummaries = [
      {
        ...doc.relationSummaries[0],
        id: "summary-3",
        text: "しかし同じ方向を支持する",
        sourceSignature: "sig-3",
      },
    ];
    const singleSummaryReport = analyzeContradictions(doc, "2026-01-01T00:00:00.000Z");
    expect(singleSummaryReport.signals.some((signal) => signal.code === "C003")).toBe(false);
  });
});
