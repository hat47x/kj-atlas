import React from "react";
import { afterEach, describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { DiffPanel } from "./DiffPanel";
import type { DiffResult } from "../domain/diff/doc_diff";
import { setActiveLocale, t } from "../i18n/translate";

const diffResult: DiffResult = {
  cards: {
    added: [],
    removed: [],
    changedText: [{ id: "c1", aText: "SECRET_TEXT_DO_NOT_LEAK", bText: "changed" }],
  },
  islands: {
    added: [],
    removed: [],
    membershipChanged: [],
    summaryChanged: [{ id: "i1", aSummary: "SECRET_TEXT_DO_NOT_LEAK", bSummary: "new", aReviewed: false, bReviewed: true }],
  },
  relationSummaries: {
    added: [],
    removed: [],
    changedText: [],
    changedReviewed: [{ id: "r1", aReviewed: false, bReviewed: true }],
    warningsChanged: [],
  },
  readingOrder: { changed: true, firstDifferingIndex: 1, aOrder: ["i1"], bOrder: ["i1", "c1"] },
};

afterEach(() => {
  setActiveLocale("ja");
});

describe("DiffPanel safe mode", () => {
  it("redacts card and summary text changes", () => {
    const html = renderToStaticMarkup(React.createElement(DiffPanel, {
      comparisonFileName: null,
      comparisonDocument: null,
      diffResult,
      currentCardIdSet: new Set(["c1"]),
      currentIslandIdSet: new Set(["i1"]),
      onLoadComparisonDocument: () => {},
      onJumpToItem: () => {},
      safeMode: true,
    }));

    expect(html).not.toContain("SECRET_TEXT_DO_NOT_LEAK");
    expect(html).toContain("[REDACTED]");
  });

  it("uses user-facing Japanese terminology instead of raw English and boolean values", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(React.createElement(DiffPanel, {
      comparisonFileName: "comparison.json",
      comparisonDocument: null,
      diffResult,
      currentCardIdSet: new Set(["c1"]),
      currentIslandIdSet: new Set(["i1"]),
      onLoadComparisonDocument: () => {},
      onJumpToItem: () => {},
      safeMode: true,
    }));

    expect(html).toContain(t("diff.panel.section.cards"));
    expect(html).toContain(t("diff.panel.section.reading_order"));
    expect(html).toContain(t("diff.panel.reviewed"));
    expect(html).toContain(t("diff.panel.unreviewed"));
    expect(html).toContain(t("diff.panel.label.a_strong"));
    expect(html).toContain(t("diff.panel.label.b_strong"));
    expect(html).not.toContain("Cards");
    expect(html).not.toContain("Reading order");
    expect(html).not.toContain("reviewed changed");
    expect(html).not.toContain("[true]");
    expect(html).not.toContain("[false]");
    expect(html).not.toContain("インデックス");
  });
});
