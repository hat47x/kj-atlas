import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";

import { SuggestionPanel } from "./SuggestionPanel";
import { setActiveLocale } from "../i18n/translate";

function buildProps() {
  return {
    instruction: "layout hints",
    onInstructionChange: vi.fn(),
    onSuggest: vi.fn(),
    onResuggest: vi.fn(),
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
  it("renders localized draft suggestion controls", () => {
    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(React.createElement(SuggestionPanel, buildProps()));

    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(React.createElement(SuggestionPanel, buildProps()));

    expect(jaHtml).toContain("ドラフト提案");
    expect(enHtml).toContain("Draft suggestion");
    expect(enHtml).toContain("CE-2 guardrail: proposal-only flow. Auto-apply is disabled.");
    expect(enHtml).not.toContain("Apply suggestion");
  });

  it("disables edit actions in read-only mode", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SuggestionPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain("Suggest layout");
    expect(html).toContain("disabled");
  });
});
