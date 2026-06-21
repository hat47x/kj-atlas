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
    suggestionId: "proposal-ui-1",
    proposalCandidates: [
      {
        proposalId: "proposal-ui-1",
        label: "Proposal 1",
        status: "proposed" as const,
        reviewState: "unreviewed" as const,
      },
      {
        proposalId: "proposal-ui-2",
        label: "Proposal 2",
        status: "held" as const,
        reviewState: "human_reviewed" as const,
      },
    ],
    selectedProposalId: "proposal-ui-2",
    onSelectProposalCandidate: vi.fn(),
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
    expect(enHtml).toContain("Layout suggestion");
    expect(enHtml).toContain("Suggestions are never applied to the current document automatically.");
    expect(enHtml).not.toContain("Apply suggestion");
    expect(enHtml).toContain("Safety conditions: No automatic application");
    expect(enHtml).toContain("Layout suggestion candidates");
    expect(enHtml).toContain("review state: 1 unreviewed / 1 human reviewed");
    expect(jaHtml).toContain("提案パッチ");
    expect(jaHtml).toContain("安全上の条件: 自動適用なし");
    expect(jaHtml).not.toContain("CE2");
    expect(jaHtml).not.toContain("auto_apply_blocked");
    expect(enHtml).toContain("selected: <strong>Proposal 2</strong> (held, human reviewed)");
    expect(enHtml).toContain("Proposal 2 (held, human reviewed)");
    expect(enHtml).toContain("remains separate from the current document until you explicitly adopt it");
    expect(enHtml).not.toContain("CE-2");
    expect(enHtml).not.toContain("auto_apply_blocked");
  });

  it("disables edit actions in read-only mode", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SuggestionPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain("Suggest layout");
    expect(html).toContain("disabled");
  });

  it("explains each proposal prerequisite without exposing internal reason codes", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(
      React.createElement(SuggestionPanel, {
        ...buildProps(),
        hasSuggestion: false,
        isPreviewEnabled: false,
      }),
    );

    expect(html).toContain("提案をプレビュー");
    expect(html).toContain("内容を確認するにはプレビューを有効にする");
    expect(html).not.toContain("suggestion_required");
    expect(html).not.toContain("preview_opt_in_required");
  });
});
