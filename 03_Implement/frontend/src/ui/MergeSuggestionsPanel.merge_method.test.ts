import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { setActiveLocale } from "../i18n/translate";
import { MergeSuggestionsPanel } from "./MergeSuggestionsPanel";

function buildProps(mergeMethod: "near_duplicate" | "kernel_fusion") {
  return {
    instruction: "",
    onInstructionChange: vi.fn(),
    onSuggest: vi.fn(),
    isSuggesting: false,
    errorMessage: null,
    suggestions: [
      {
        groupId: "g1",
        cardIds: ["a", "b"],
        mergedTextDraft: "Risk mitigation",
        mergeMethod,
        editedText: "Risk mitigation",
        isEdited: false,
      },
    ],
    cardsById: new Map([
      ["a", { id: "a", text: "Risk mitigation", x: 0, y: 0 }],
      ["b", { id: "b", text: "risk mitigation", x: 10, y: 0 }],
    ]),
    onMergedTextChange: vi.fn(),
    onDecide: vi.fn(),
    onApplyAccepted: vi.fn(),
    latestAuditEventByGroup: new Map(),
    auditEvents: [],
    onExportAuditEvents: vi.fn(),
  };
}

describe("MergeSuggestionsPanel merge method", () => {
  afterEach(() => setActiveLocale("ja"));

  it("shows the near-duplicate method separately from rationale in Japanese", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, buildProps("near_duplicate")),
    );

    expect(html).toContain("統合方式: 類似カードの整理（04ステップ型）");
  });

  it("shows the kernel-fusion method separately in English", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, buildProps("kernel_fusion")),
    );

    expect(html).toContain("Merge method: Meaning-kernel integration (KJ nuclear-fusion style)");
  });
});
