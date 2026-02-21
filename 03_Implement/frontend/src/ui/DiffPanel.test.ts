import React from "react";
import { describe, expect, it } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { DiffPanel } from "./DiffPanel";
import type { DiffResult } from "../domain/diff/doc_diff";

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
  relationSummaries: { added: [], removed: [], changedText: [], changedReviewed: [], warningsChanged: [] },
  readingOrder: { changed: false, firstDifferingIndex: -1, aOrder: [], bOrder: [] },
};

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
});
