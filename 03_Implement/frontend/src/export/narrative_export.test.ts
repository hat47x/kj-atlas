import { describe, expect, it } from "vitest";

import { buildNarrativeHtml, buildNarrativeMarkdown } from "./narrative_export";

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
      }
    );

    expect(output).toContain("DRAFT (UNREVIEWED) — Please verify against the diagram.");
    expect(output).toContain("Status: Unreviewed draft");
    expect(output).toContain("1. card_1: first card");
    expect(output).toContain("2. island_2");
    expect(output).toContain("CreatedAt: N/A");
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
      }
    );

    expect(output).toContain("Reviewed by human");
    expect(output).toContain("CreatedAt: 2026-01-01T00:00:00Z");
    expect(output).toContain("Reviewed &lt;Title&gt;");
    expect(output).toContain("Alpha &lt;beta&gt;");
    expect(output).toContain("Snippet &lt;safe&gt;");
    expect(output).toContain("<ol>");
  });
});
