import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { buildReadingOutlineMd } from "./reading_outline";
import { analyzeOutlineQuality } from "./outline_quality";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
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

  it("appends suggested next steps when enabled", () => {
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
      {
        appendRecommendations: true,
        recommendations: [
          {
            id: "rec-1",
            priority: 1,
            category: "clarity",
            title: "島タイトルを整理する",
            description: "多くの島にタイトルが無く、読解の起点が不明確です。",
            rationaleCodes: ["Q001"],
            suggestedActions: ["各島に1行の要約タイトルを付与する"],
            impactLevel: "high",
          },
        ],
      },
    );

    expect(markdown).toContain("## Suggested Next Steps");
    expect(markdown).toContain("1. 島タイトルを整理する [high]");
    expect(markdown).toContain("Action: 各島に1行の要約タイトルを付与する");
    expect(markdown).not.toContain("rec-1");
    expect(diagnostics.findings.length).toBeGreaterThan(0);
  });

  it("omits the KA fields section by default (DOMAIN-KA-01, default OFF)", () => {
    const doc = buildDoc();
    doc.cards[0] = { ...doc.cards[0], ka: { voice: "しんどい", value: "安心感" } };

    const markdown = buildReadingOutlineMd(doc, {
      readingNavEnabled: true,
      readingIndex: 0,
      readingMode: "islands+cards",
      reviewedOnly: false,
      safeMode: false,
    });

    expect(markdown).not.toContain("## KA Fields");
  });

  it("appends a separate KA fields section when opted in, never merged into a card's body text", () => {
    const doc = buildDoc();
    doc.cards[0] = { ...doc.cards[0], ka: { voice: "しんどい", value: "安心感" } };

    const markdown = buildReadingOutlineMd(
      doc,
      {
        readingNavEnabled: true,
        readingIndex: 0,
        readingMode: "islands+cards",
        reviewedOnly: false,
        safeMode: false,
      },
      { appendKaFields: true },
    );

    expect(markdown).toContain("## KA Fields (inner voice / value)");
    expect(markdown).toContain("Card card-top — Inner voice: しんどい / Value: 安心感");
    // Not interleaved into the card's own outline entry.
    const cardEntryLine = markdown.split("\n").find((line) => line.includes("[Card] Top card line"));
    expect(cardEntryLine).toBeDefined();
    expect(cardEntryLine).not.toContain("しんどい");
  });

  it("hides the KA fields section under SafeMode, same channel as card.text", () => {
    const doc = buildDoc();
    doc.cards[0] = { ...doc.cards[0], ka: { voice: "しんどい", value: "安心感" } };

    const markdown = buildReadingOutlineMd(
      doc,
      {
        readingNavEnabled: true,
        readingIndex: 0,
        readingMode: "islands+cards",
        reviewedOnly: false,
        safeMode: true,
      },
      { appendKaFields: true, context: "share" },
    );

    expect(markdown).toContain("[SAFE MODE: KA fields hidden]");
    expect(markdown).not.toContain("しんどい");
  });
});
