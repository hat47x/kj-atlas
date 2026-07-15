import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeOutlineQuality } from "./outline_quality";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-quality",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Card 1", x: 10, y: 10 },
      { id: "c2", text: "Card 2", x: 20, y: 20 },
      { id: "c3", text: "Card 3", x: 30, y: 30 },
      { id: "lone", text: "Lone", x: 500, y: 500 },
    ],
    edges: [
      { id: "e1", fromId: "i1", toId: "i2", fromKind: "island", toKind: "island", type: "related" },
    ],
    islands: [
      { id: "i1", cardIds: ["c1"], title: "", summaryText: "draft", summaryReviewed: false },
      { id: "i2", cardIds: ["c2"], title: "", summaryText: "", summaryReviewed: false },
      { id: "i3", cardIds: ["c3"], title: "", summaryText: "", summaryReviewed: true },
    ],
    relationSummaries: [],
  };
}

describe("outline quality", () => {
  it("builds deterministic report and emits expected findings", () => {
    const report = analyzeOutlineQuality(
      buildDoc(),
      { readingMode: "islands+cards", reviewedOnly: false },
      { nowIso: "2026-01-02T00:00:00.000Z", collapsedIslandIds: new Set() },
    );

    expect(report.generatedAt).toBe("2026-01-02T00:00:00.000Z");
    expect(report.stats.totalIslands).toBe(3);
    expect(report.stats.disconnectedIslands).toBe(1);
    expect(report.findings.map((finding) => finding.code)).toEqual([
      "Q001",
      "Q002",
      "Q003",
      "Q004",
      "Q005",
      "Q007",
      "Q008",
    ]);

    const loneCardFinding = report.findings.find((finding) => finding.code === "Q007");
    expect(loneCardFinding?.entityRefs).toEqual([{ kind: "card", id: "lone" }]);
  });

  it("emits Q006 for long reading paths without collapse usage", () => {
    const doc = buildDoc();
    doc.cards = Array.from({ length: 31 }, (_, index) => ({
      id: `card-${index}`,
      text: `Card ${index}`,
      x: index,
      y: index,
    }));
    doc.islands = [
      {
        id: "island-1",
        cardIds: doc.cards.map((card) => card.id),
        title: "Island 1",
        summaryText: "Reviewed",
        summaryReviewed: true,
      },
    ];

    const report = analyzeOutlineQuality(doc, { readingMode: "islands+cards", reviewedOnly: false }, { collapsedIslandIds: new Set() });
    expect(report.findings.some((finding) => finding.code === "Q006")).toBe(true);
  });

  it("adds deterministic note when relation summary store is absent", () => {
    const doc = buildDoc();
    delete doc.relationSummaries;

    const report = analyzeOutlineQuality(doc, { readingMode: "islands", reviewedOnly: false }, { nowIso: "2026-01-02T00:00:00.000Z" });
    const finding = report.findings.find((entry) => entry.code === "Q004");
    expect(finding?.detail).toContain("No relation summary store found in document");
  });

});
