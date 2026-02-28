import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MergeSuggestionsPanel } from "./MergeSuggestionsPanel";

function buildProps() {
  return {
    instruction: "",
    onInstructionChange: vi.fn(),
    onSuggest: vi.fn(),
    isSuggesting: false,
    errorMessage: null,
    suggestions: [
      {
        groupId: "heuristic-risk-a-b",
        cardIds: ["a", "b"],
        mergedTextDraft: "Risk mitigation",
        editedText: "Risk mitigation",
        isEdited: false,
        rationale: "heuristic:normalized-text",
      },
    ],
    cardsById: new Map([
      ["a", { id: "a", text: "Risk mitigation", x: 0, y: 0 }],
      ["b", { id: "b", text: "risk mitigation", x: 10, y: 0 }],
    ]),
    onMergedTextChange: vi.fn(),
    onApply: vi.fn(),
    onDismiss: vi.fn(),
  };
}

describe("MergeSuggestionsPanel", () => {
  it("shows deterministic-heuristic guidance and candidate cards", () => {
    const html = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, buildProps()));

    expect(html).toContain("Similar card merge candidates");
    expect(html).toContain("Deterministic heuristic only (no AI decision)");
    expect(html).toContain("Cards in candidate group");
    expect(html).toContain("a: Risk mitigation");
    expect(html).toContain("b: risk mitigation");
    expect(html).toContain("Rationale: heuristic:normalized-text");
  });
});
