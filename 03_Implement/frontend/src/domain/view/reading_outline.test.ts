import { describe, expect, it } from "vitest";

import type { DocumentV2 } from "../types";
import { buildReadingOutlineMd } from "./reading_outline";
import { analyzeOutlineQuality } from "./outline_quality";

function buildDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc-outline",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-top", text: "Top card line\nline 2", x: 100, y: 20 },
      { id: "card-bottom", text: "Bottom card", x: 120, y: 220 },
      { id: "lone", text: "Lone card", x: 800, y: 800 },
    ],
    edges: [],
    islands: [
      { id: "island-bottom", cardIds: ["card-bottom"], title: "Bottom", summaryText: "Bottom draft", summaryReviewed: false },
      { id: "island-top", cardIds: ["card-top"], title: "Top", summaryText: "Top reviewed", summaryReviewed: true },
    ],
    relationSummaries: [
      {
        id: "rel-1",
        createdAt: "2026-01-01T00:00:00.000Z",
        islandAId: "island-top",
        islandBId: "island-bottom",
        relationType: "related",
        derived: false,
        text: "Draft relation",
        reviewed: false,
        groundingCardIds: [],
        groundingEdgeIds: [],
        sourceSignature: "sig-1",
      },
    ],
  };
}

describe("reading outline", () => {
  it("respects reading order and reviewedOnly filter", () => {
    const markdown = buildReadingOutlineMd(buildDoc(), {
      readingNavEnabled: true,
      readingIndex: 0,
      readingMode: "islands",
      reviewedOnly: true,
      safeMode: false,
    });

    expect(markdown).toContain("## [Island] Top");
    expect(markdown).not.toContain("## [Island] Bottom");
  });

  it("marks unreviewed summaries when included", () => {
    const markdown = buildReadingOutlineMd(
      buildDoc(),
      {
        readingNavEnabled: true,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: false,
      },
      { includeUnreviewedSummaries: true },
    );

    expect(markdown).toContain("> [UNREVIEWED] Bottom draft");
    expect(markdown).toContain("- [Relation] Bottom (island-bottom)");
    expect(markdown).toContain("> [UNREVIEWED] Draft relation");
  });

  it("hides unreviewed drafts in safe mode", () => {
    const markdown = buildReadingOutlineMd(
      buildDoc(),
      {
        readingNavEnabled: true,
        readingIndex: 0,
        readingMode: "islands",
        reviewedOnly: false,
        safeMode: true,
      },
      { includeUnreviewedSummaries: true },
    );

    expect(markdown).toContain("> [UNREVIEWED HIDDEN]");
    expect(markdown).not.toContain("> [UNREVIEWED] Bottom draft");
  });

  it("includes cards in islands+cards mode", () => {
    const markdown = buildReadingOutlineMd(buildDoc(), {
      readingNavEnabled: true,
      readingIndex: 0,
      readingMode: "islands+cards",
      reviewedOnly: false,
      safeMode: false,
    });

    expect(markdown).toContain("### [Card] Top card line");
    expect(markdown).toContain("### [Card] Lone card");
  });

  it("appends diagnostics section when enabled", () => {
    const doc = buildDoc();
    const diagnostics = analyzeOutlineQuality(doc, { readingMode: "islands+cards", reviewedOnly: false }, { nowIso: "2026-01-01T01:23:45.000Z" });

    const markdown = buildReadingOutlineMd(
      doc,
      {
        readingNavEnabled: true,
        readingIndex: 0,
        readingMode: "islands+cards",
        reviewedOnly: false,
        safeMode: true,
      },
      { appendDiagnostics: true, diagnosticsReport: diagnostics },
    );

    expect(markdown).toContain("## Diagnostics");
    expect(markdown).toContain("| totalIslands | 2 |");
    expect(markdown).toContain("Q007 Lone cards are present");
    expect(markdown).not.toContain("Bottom draft");
  });
});
