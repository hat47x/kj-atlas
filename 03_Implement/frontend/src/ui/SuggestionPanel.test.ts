import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { SuggestionPanel } from "./SuggestionPanel";
import { setActiveLocale } from "../i18n/translate";
import type { Ce2SuggestionCandidate } from "./suggestion_panel_adapter";

const mockCandidates: Ce2SuggestionCandidate[] = [{
  id: "p1", label: "Proposal 1", status: "proposed", reviewState: "unreviewed",
  cardCount: 3, summary: "Draft proposal alpha", sourceBundleHash: "abc123",
}, {
  id: "p2", label: "Proposal 2", status: "held", reviewState: "human_reviewed",
  cardCount: 2, summary: "Draft proposal beta", sourceBundleHash: "def456",
}];

beforeEach(() => { setActiveLocale("ja"); });

describe("SuggestionPanel", () => {
  it("renders localized draft suggestion controls", () => {
    setActiveLocale("ja");
    const jaHtml = renderToStaticMarkup(createElement(SuggestionPanel, {
      onSuggest: vi.fn(), onResuggest: vi.fn(), onDiscard: vi.fn(),
      onAnnotateCritiques: vi.fn(), suggestionId: null, hasSuggestion: false,
      isSuggesting: false, layoutHints: "", onLayoutHintsChange: vi.fn(),
      onStopAnnotating: vi.fn(), notes: "", proposalCandidates: [],
      isPreviewEnabled: false, onPreviewToggle: vi.fn(),
    }));
    expect(jaHtml).toContain("ドラフト提案");
    
    setActiveLocale("en");
    const enHtml = renderToStaticMarkup(createElement(SuggestionPanel, {
      onSuggest: vi.fn(), onResuggest: vi.fn(), onDiscard: vi.fn(),
      onAnnotateCritiques: vi.fn(), suggestionId: "s1", hasSuggestion: true,
      isSuggesting: false, layoutHints: "layout hints", onLayoutHintsChange: vi.fn(),
      onStopAnnotating: vi.fn(), notes: "draft note",
      proposalCandidates: mockCandidates, selectedProposalId: "p2",
      onSelectProposalCandidate: vi.fn(), isPreviewEnabled: false, onPreviewToggle: vi.fn(),
    }));
    expect(enHtml).toContain("Draft suggestion");
    expect(enHtml).toContain("This is an unreviewed suggestion proposal.");
    expect(enHtml).not.toContain("Apply suggestion");
    expect(enHtml).toContain("Safety conditions");
    expect(enHtml).toContain("Patch proposals");
    expect(enHtml).toContain("review state: 1 unreviewed / 1 human reviewed");
    expect(enHtml).toContain("Suggest layout");
    expect(enHtml).toContain("CE-2 guardrail: proposal-only flow");
    expect(enHtml).not.toContain("auto_apply_blocked");
    expect(jaHtml).toContain("提案パッチ");
    expect(jaHtml).toContain("安全条件");
    expect(jaHtml).toContain("配置を提案");
  });

  it("explains each proposal prerequisite without exposing internal reason codes", () => {
    setActiveLocale("ja");
    const html = renderToStaticMarkup(createElement(SuggestionPanel, {
      onSuggest: vi.fn(), onResuggest: vi.fn(), onDiscard: vi.fn(),
      onAnnotateCritiques: vi.fn(), suggestionId: null, hasSuggestion: false,
      isSuggesting: false, layoutHints: "", onLayoutHintsChange: vi.fn(),
      onStopAnnotating: vi.fn(), notes: "", proposalCandidates: [],
      isPreviewEnabled: false, onPreviewToggle: vi.fn(),
    }));
    expect(html).toContain("配置を提案");
    expect(html).not.toContain("suggestion_required");
    expect(html).not.toContain("preview_opt_in_required");
  });
});
