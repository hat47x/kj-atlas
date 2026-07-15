import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { buildTraceAnalyticsMd, computeTraceAnalytics } from "./trace_analytics";

const fixtureDoc: DocumentV1 = {
  version: 1,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "SECRET_TEXT_DO_NOT_LEAK root", x: 0, y: 0 },
    { id: "c2", text: "node 2", x: 0, y: 0 },
    { id: "c3", text: "node 3", x: 0, y: 0 },
    { id: "c4", text: "node 4", x: 0, y: 0 },
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
  it("computes deterministic analytics for both traces", () => {
    const run1 = computeTraceAnalytics(fixtureDoc, "c1", { kind: "both", maxHops: 3, includeCycleDetection: true, safeMode: true });
    const run2 = computeTraceAnalytics(fixtureDoc, "c1", { kind: "both", maxHops: 3, includeCycleDetection: true, safeMode: true });

    expect(run1).toEqual(run2);
    expect(run1.byRelationType).toEqual({ supports: 2, contradicts: 2 });
    expect(run1.depthHistogram).toEqual({ 0: 1, 1: 2, 2: 1 });
    expect(run1.topHubs[0]).toEqual({ cardId: "c3", degree: 3 });
    expect(run1.cycles?.count).toBe(1);
  });

  it("supports evidence-only and contradiction-only modes", () => {
    const evidence = computeTraceAnalytics(fixtureDoc, "c1", { kind: "evidence", safeMode: true });
    const contradiction = computeTraceAnalytics(fixtureDoc, "c1", { kind: "contradiction", safeMode: true });

    expect(evidence.byRelationType).toEqual({ supports: 2 });
    expect(contradiction.byRelationType).toEqual({ contradicts: 2 });
  });


  it("orders equal-degree hubs by card id", () => {
    const analytics = computeTraceAnalytics(fixtureDoc, "c1", { kind: "both", topHubCount: 4, safeMode: true });
    const degreeTwo = analytics.topHubs.filter((hub) => hub.degree === 2).map((hub) => hub.cardId);
    expect(degreeTwo).toEqual(["c1", "c2"]);
  });

  it("includes evidence link count, isolated nodes, and source density deterministically", () => {
    const analytics = computeTraceAnalytics(fixtureDoc, "c1", { kind: "both", safeMode: true });

    expect(analytics.evidenceLinkCount).toBe(4);
    expect(analytics.isolatedNodeCount).toBe(0);
    expect(analytics.isolatedNodeIds).toEqual([]);
    expect(analytics.sourceDensity).toBe(1);
  });

  it("detects isolated nodes and keeps deterministic ordering", () => {
    const docWithIsolated: DocumentV1 = {
      ...fixtureDoc,
      cards: [...fixtureDoc.cards, { id: "c0", text: "isolated", x: 0, y: 0 }, { id: "c5", text: "isolated2", x: 0, y: 0 }],
    };
    const analytics = computeTraceAnalytics(docWithIsolated, "c1", { kind: "both", safeMode: true });

    expect(analytics.evidenceLinkCount).toBe(4);
    expect(analytics.isolatedNodeCount).toBe(2);
    expect(analytics.isolatedNodeIds).toEqual(["c0", "c5"]);
    expect(analytics.sourceDensity).toBe(0.6667);

    const markdown = buildTraceAnalyticsMd(analytics);
    expect(markdown).toContain("## Isolated nodes");
    expect(markdown).toContain("- card:c0");
    expect(markdown).toContain("- card:c5");
  });

  it("builds safe markdown with ids/counts only", () => {
    const analytics = computeTraceAnalytics(fixtureDoc, "c1", { kind: "both", safeMode: true });
    const markdown = buildTraceAnalyticsMd(analytics);

    expect(markdown).toContain("# Trace Analytics");
    expect(markdown).toContain("supports: 2");
    expect(markdown).toContain("card:c3 degree:3");
    expect(markdown).toContain("- evidenceLinkCount: 4");
    expect(markdown).toContain("- isolatedNodeCount: 0");
    expect(markdown).toContain("- sourceDensity: 1");
    expect(markdown).toContain("Safe mode enforced: ids/counts only.");
    expect(markdown).not.toContain("SECRET_TEXT_DO_NOT_LEAK");
  });
});
