import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { analyzeOutlineQuality } from "./outline_quality";
import { generateRecommendations } from "./recommendations";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-reco",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Card 1", x: 0, y: 0 },
      { id: "c2", text: "Card 2", x: 10, y: 10 },
      { id: "lone", text: "Lone", x: 20, y: 20 },
    ],
    edges: [],
    islands: [
      { id: "i1", cardIds: ["c1"], title: "", summaryText: "draft", summaryReviewed: false },
      { id: "i2", cardIds: ["c2"], title: "", summaryText: "", summaryReviewed: false },
    ],
    relationSummaries: [],
  };
}

describe("generateRecommendations", () => {
  it("maps findings into deterministic recommendations and order", () => {
    const doc = buildDoc();
    const report = analyzeOutlineQuality(doc, { readingMode: "islands+cards", reviewedOnly: false }, { nowIso: "2026-01-01T00:00:00.000Z" });

    const recommendations = generateRecommendations(report, doc, { readingMode: "islands+cards", reviewedOnly: false });

    expect(recommendations.map((item) => item.rationaleCodes[0])).toEqual(["Q001", "Q003", "Q005", "Q004", "Q007"]);
    expect(recommendations[0]?.targetEntities).toEqual([
      { kind: "island", id: "i1" },
      { kind: "island", id: "i2" },
    ]);
    expect(recommendations[1]?.priority).toBe(1);
    expect(recommendations[4]?.targetEntities).toEqual([{ kind: "card", id: "lone" }]);
  });

  it("sets Q003 priority to 2 in reviewed-only mode", () => {
    const doc = buildDoc();
    const report = analyzeOutlineQuality(doc, { readingMode: "islands", reviewedOnly: true }, { nowIso: "2026-01-01T00:00:00.000Z" });

    const recommendations = generateRecommendations(report, doc, { readingMode: "islands", reviewedOnly: true });
    const q003 = recommendations.find((item) => item.rationaleCodes.includes("Q003"));

    expect(q003?.priority).toBe(2);
  });
});
