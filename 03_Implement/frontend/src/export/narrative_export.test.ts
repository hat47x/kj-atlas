import { describe, expect, it } from "vitest";

import { buildNarrativeHtml, buildNarrativeMarkdown } from "./narrative_export";
import type { GroundingEntry } from "../domain/grounding";


const groundingEntries: GroundingEntry[] = [
  {
    anchor: "#1",
    sourceId: "island_2",
    kind: "island",
    islandTitle: "Island 2",
    islandSummaryText: "Summary text",
    islandSummaryReviewed: false,
    islandMembers: [{ id: "card_1", text: "Card one", kind: "canonical" }],
  },
];

describe("narrative_export", () => {
  it("renders unreviewed markdown with draft banner and ordered basedOnReadingOrder list", () => {
    const output = buildNarrativeMarkdown(
      {
        id: "n1",
        title: "Draft A",
        text: "Line 1",
        reviewed: false,
        basedOnReadingOrder: ["card_1", "island_2"],
      },
      {
        card_1: "first card",
      },
      groundingEntries
    );

    expect(output).toContain("DRAFT (UNREVIEWED) — Please verify against the diagram.");
    expect(output).toContain("Status: Unreviewed draft");
    expect(output).toContain("1. card_1: first card");
    expect(output).toContain("2. island_2");
    expect(output).toContain("CreatedAt: N/A");
    expect(output).toContain("## Grounding / Citations");
    expect(output).toContain("Summary (unreviewed): Summary text");
  });

  it("renders reviewed html with reviewed label and escaped content", () => {
    const output = buildNarrativeHtml(
      {
        id: "n2",
        title: "Reviewed <Title>",
        text: "Alpha <beta>",
        createdAt: "2026-01-01T00:00:00Z",
        reviewed: true,
        basedOnReadingOrder: ["card_1"],
      },
      {
        card_1: "Snippet <safe>",
      },
      groundingEntries
    );

    expect(output).toContain("Reviewed by human");
    expect(output).toContain("CreatedAt: 2026-01-01T00:00:00Z");
    expect(output).toContain("Reviewed &lt;Title&gt;");
    expect(output).toContain("Alpha &lt;beta&gt;");
    expect(output).toContain("Snippet &lt;safe&gt;");
    expect(output).toContain("<ol>");
    expect(output).toContain("Grounding / Citations");
    expect(output).toContain("Summary (unreviewed): Summary text");
  });

  it("keeps contradiction review state in markdown and html evidence links", () => {
    const item = {
      id: "n3",
      title: "Contradiction package",
      text: "Reviewed narrative",
      reviewed: true,
      basedOnReadingOrder: ["card_1"],
    };
    const evidenceLinks = [
      {
        id: "e-held",
        type: "contradicts" as const,
        fromCardId: "card_2",
        toCardId: "card_1",
        contradictionState: "held" as const,
      },
    ];

    const markdown = buildNarrativeMarkdown(item, {}, [], evidenceLinks);
    const html = buildNarrativeHtml(item, {}, [], evidenceLinks);

    expect(markdown).toContain("card_2 contradicts card_1 [held]");
    expect(html).toContain('<span class="contradiction-state">[held]</span>');
  });
});
