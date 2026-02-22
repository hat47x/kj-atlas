import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { buildTraceAnalyticsMd, computeTraceAnalytics } from "./trace_analytics";

const doc: DocumentV2 = {
  version: 2,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "A", x: 0, y: 0 },
    { id: "c2", text: "B", x: 0, y: 0 },
    { id: "c3", text: "C", x: 0, y: 0 },
    { id: "c4", text: "D", x: 0, y: 0 },
  ],
  edges: [],
  islands: [],
  relationSummaries: [],
  evidenceLinks: [
    { id: "e1", type: "supports", fromCardId: "c1", toCardId: "c2" },
    { id: "e2", type: "supports", fromCardId: "c2", toCardId: "c3" },
    { id: "e3", type: "contradicts", fromCardId: "c3", toCardId: "c1" },
    { id: "e4", type: "contradicts", fromCardId: "c3", toCardId: "c4" },
  ],
};

describe("computeTraceAnalytics", () => {
  it("computes deterministic analytics including cycle count", () => {
    const run1 = computeTraceAnalytics(doc, "c1", { maxHops: 3, includeCycleDetection: true, safeMode: true });
    const run2 = computeTraceAnalytics(doc, "c1", { maxHops: 3, includeCycleDetection: true, safeMode: true });

    expect(run1).toEqual(run2);
    expect(run1.evidenceLinkCountsByType).toEqual({ supports: 2, contradicts: 2 });
    expect(run1.depthDistribution).toEqual([
      { depth: 0, count: 1 },
      { depth: 1, count: 2 },
      { depth: 2, count: 1 },
    ]);
    expect(run1.topHubs[0]).toEqual({ cardId: "c3", degree: 3 });
    expect(run1.cycleCount).toBe(1);
  });

  it("builds markdown with ids/counts only and safe mode note", () => {
    const analytics = computeTraceAnalytics(doc, "c1", { safeMode: true });
    const markdown = buildTraceAnalyticsMd(analytics);

    expect(markdown).toContain("# Trace Analytics");
    expect(markdown).toContain("supports: 2");
    expect(markdown).toContain("card:c3 degree:3");
    expect(markdown).toContain("Safe mode enforced: ids/counts only.");
    expect(markdown).not.toContain("\nA\n");
  });
});
