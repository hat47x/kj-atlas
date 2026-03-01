import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { SuggestionPanel } from "./SuggestionPanel";

function buildProps() {
  return {
    instruction: "layout hints",
    onInstructionChange: vi.fn(),
    onSuggest: vi.fn(),
    onResuggest: vi.fn(),
    onApply: vi.fn(),
    onDiscard: vi.fn(),
    hasSuggestion: true,
    isPreviewEnabled: true,
    onPreviewToggle: vi.fn(),
    isAnnotateOverlayEnabled: false,
    onAnnotateOverlayToggle: vi.fn(),
    isSuggesting: false,
    errorMessage: null,
    notes: "draft note",
  };
}

describe("SuggestionPanel", () => {
  it("renders draft suggestion controls", () => {
    const html = renderToStaticMarkup(React.createElement(SuggestionPanel, buildProps()));

    expect(html).toContain("Draft suggestion");
    expect(html).toContain("Suggest layout");
    expect(html).toContain("Apply suggestion");
    expect(html).toContain("Discard");
  });

  it("disables edit actions in read-only mode", () => {
    const html = renderToStaticMarkup(React.createElement(SuggestionPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain("Suggest layout");
    expect(html).toContain("disabled");
  });
});
