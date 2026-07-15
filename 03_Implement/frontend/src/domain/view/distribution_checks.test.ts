import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeDistribution, rankDistributionIslands } from "./distribution_checks";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    relationSummaries: [],
  };
}

describe("analyzeDistribution", () => {
  it("is deterministic and emits D001 for overloaded islands", () => {
    const doc = buildDoc();
    doc.cards = Array.from({ length: 28 }, (_, index) => ({ id: `card-${index}`, text: "", x: 0, y: 0 }));
    doc.islands = [
      { id: "island-a", cardIds: Array.from({ length: 24 }, (_, index) => `card-${index}`), title: "A" },
      { id: "island-b", cardIds: ["card-24", "card-25"], title: "B" },
      { id: "island-c", cardIds: ["card-26"], title: "C" },
      { id: "island-d", cardIds: ["card-27"], title: "D" },
    ];

    const first = analyzeDistribution(doc, "2026-01-01T00:00:00.000Z");
    const second = analyzeDistribution(doc, "2026-01-01T00:00:00.000Z");

    expect(second).toEqual(first);
    expect(first.findings.some((finding) => finding.code === "D001")).toBe(true);
    expect(first.stats.islandsOverloadedCount).toBe(1);
  });

  it("detects fragmentation, isolation, and low density", () => {
    const doc = buildDoc();
    doc.cards = Array.from({ length: 5 }, (_, index) => ({ id: `card-${index}`, text: "", x: 0, y: 0 }));
    doc.islands = [
      { id: "island-a", cardIds: ["card-0"] },
      { id: "island-b", cardIds: ["card-1"] },
      { id: "island-c", cardIds: ["card-2"] },
      { id: "island-d", cardIds: ["card-3", "card-4"] },
    ];

    const report = analyzeDistribution(doc, "2026-01-01T00:00:00.000Z");

    expect(report.findings.some((finding) => finding.code === "D002")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "D003")).toBe(true);
    expect(report.findings.some((finding) => finding.code === "D004")).toBe(true);
    expect(report.stats.isolatedIslandsCount).toBe(4);
  });

  it("ranks loaded/isolated islands deterministically", () => {
    const doc = buildDoc();
    doc.cards = Array.from({ length: 9 }, (_, index) => ({ id: `card-${index}`, text: "", x: 0, y: 0 }));
    doc.islands = [
      { id: "island-b", cardIds: ["card-0", "card-1", "card-2"] },
      { id: "island-a", cardIds: ["card-3", "card-4", "card-5"] },
      { id: "island-c", cardIds: ["card-6", "card-7"] },
      { id: "island-d", cardIds: ["card-8"] },
    ];
    doc.edges = [
      { id: "edge-1", fromKind: "island", toKind: "island", fromId: "island-a", toId: "island-c", type: "related" },
    ];

    const ranked = rankDistributionIslands(doc, 3);

    expect(ranked.loaded.map((row) => row.id)).toEqual(["island-a", "island-b", "island-c"]);
    expect(ranked.isolated.map((row) => row.id)).toEqual(["island-b", "island-d"]);
  });
});
