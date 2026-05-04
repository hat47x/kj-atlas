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
    expect(enHtml).toContain("Draft suggestion");
    expect(enHtml).toContain("CE-2 guardrail: proposal-only flow. Auto-apply is disabled.");
    expect(enHtml).not.toContain("Apply suggestion");
    expect(enHtml).toContain("CE2 proposal-only blockers: auto_apply_blocked");
    expect(enHtml).toContain("Patch proposals");
    expect(enHtml).toContain("review state: 1 unreviewed / 1 human reviewed");
    expect(enHtml).toContain("selected: <strong>Proposal 2</strong> (held, human_reviewed)");
    expect(enHtml).toContain("Proposal 2 (held, human_reviewed)");
    expect(enHtml).toContain("Reversible synthesis keeps proposals isolated until explicit human approval.");
  });

  it("disables edit actions in read-only mode", () => {
    setActiveLocale("en");
    const html = renderToStaticMarkup(React.createElement(SuggestionPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain("Suggest layout");
    expect(html).toContain("disabled");
  });
});
