import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { renderToStaticMarkup } from "react-dom/server";
import { MergeSuggestionsPanel } from "./MergeSuggestionsPanel";
import { setActiveLocale, t } from "../i18n/translate";

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
        targetCardId: "a",
        candidateCardIds: ["b"],
        scoreSummary: { min: 1, max: 1, avg: 1 },
        reasonCodes: ["heuristic:normalized-text"],
        snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
        cardIds: ["a", "b"],
        mergedTextDraft: "Risk mitigation",
        editedText: "Risk mitigation",
        isEdited: false,
        rationale: "heuristic:normalized-text",
        latestDecision: "defer" as const,
        latestDecidedAt: "2026-02-28T10:00:00.000Z",
        representativeCardId: "a",
        representativeResolvedBy: "fallback" as const,
        representativeSourceCount: 1,
      },
    ],
    cardsById: new Map([
      ["a", { id: "a", text: "Risk mitigation", x: 0, y: 0 }],
      ["b", { id: "b", text: "risk mitigation", x: 10, y: 0 }],
    ]),
    onMergedTextChange: vi.fn(),
    onDecide: vi.fn(),
    onApplyAccepted: vi.fn(),
    latestAuditEventByGroup: new Map([[
      "heuristic-risk-a-b",
      {
        eventId: "evt-1",
        groupId: "heuristic-risk-a-b",
        decision: "defer" as const,
        decidedAt: "2026-02-28T10:00:00.000Z",
        decidedBy: "human" as const,
        cardIds: ["a", "b"],
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      },
    ]]),
    auditEvents: [
      {
        eventId: "evt-1",
        groupId: "heuristic-risk-a-b",
        decision: "defer" as const,
        decidedAt: "2026-02-28T10:00:00.000Z",
        decidedBy: "human" as const,
        cardIds: ["a", "b"],
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      },
    ],
    onExportAuditEvents: vi.fn(),
  };
}

describe("MergeSuggestionsPanel", () => {
  afterEach(() => setActiveLocale("ja"));

  it("formats decision timestamps using the active app locale, not the browser default", () => {
    const timestamp = "2026-02-28T10:00:00.000Z";

    setActiveLocale("en");
    const htmlEn = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, buildProps()));
    expect(htmlEn).toContain(new Date(timestamp).toLocaleString("en-US"));
    expect(htmlEn).not.toContain(new Date(timestamp).toLocaleString("ja-JP"));

    setActiveLocale("ja");
    const htmlJa = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, buildProps()));
    expect(htmlJa).toContain(new Date(timestamp).toLocaleString("ja-JP"));
    expect(htmlJa).not.toContain(new Date(timestamp).toLocaleString("en-US"));
  });

  it("shows deterministic-heuristic guidance, decision status, and four decision actions", () => {
    const html = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, buildProps()));

    expect(html).toContain(t("merge_suggestions.title"));
    expect(html).toContain(t("merge_suggestions.deterministic_hint"));
    expect(html).toContain(t("merge_suggestions.cards_in_group"));
    expect(html).toContain(t("merge_suggestions.decision_label", { decision: t("merge_suggestions.decision.deferred") }));
    expect(html).toContain("a: Risk mitigation");
    expect(html).toContain("b: risk mitigation");
    expect(html).toContain(
      `${t("merge_suggestions.representative")}: a [${t("merge_suggestions.representative_resolution.fallback")}]${t("merge_suggestions.source_count_suffix", { count: 1 })}`
    );
    expect(html).toContain(`${t("merge_suggestions.rationale")}: heuristic:normalized-text`);
    expect(html).toContain(`判断=${t("merge_suggestions.decision.deferred")}`);
    expect(html).not.toContain("[fallback]");
    expect(html).not.toContain("判断=defer");
    expect(html).toContain(t("merge_suggestions.export_audit"));
    expect(html).toContain(t("merge_suggestions.events_count", { count: 1 }));
    expect(html).toContain(`${t("merge_suggestions.draft_diff_preview")}:`);
    expect(html).toContain(t("merge_suggestions.decision_reason"));
    expect(html).toContain(t("merge_suggestions.decision_reason_placeholder"));
    expect(html).toContain(t("merge_suggestions.decision_unlock_hint"));
    expect(html).toContain(t("merge_suggestions.action.accept"));
    expect(html).toContain(t("merge_suggestions.action.partial"));
    expect(html).toContain(t("merge_suggestions.partial_selection.title"));
    expect(html).toContain(t("merge_suggestions.partial_selection.hint"));
    expect(html).toContain(t("merge_suggestions.action.reject"));
    expect(html).toContain(t("merge_suggestions.action.defer"));
    expect(html).toContain(t("merge_suggestions.human_in_loop_hint"));
  });

  it("shows the explicit apply action for accepted and partially accepted suggestions", () => {
    const base = buildProps();
    const pendingHtml = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, {
        ...base,
        suggestions: [
          {
            ...base.suggestions[0],
            latestDecision: "accept" as const,
            representativeResolvedBy: "fallback" as const,
          },
        ],
      }),
    );
    expect(pendingHtml).toContain(t("merge_suggestions.action.apply"));
    expect(pendingHtml).not.toContain(t("merge_suggestions.action.applied"));

    const partialHtml = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, {
        ...base,
        suggestions: [{ ...base.suggestions[0], latestDecision: "partial" as const, representativeResolvedBy: "fallback" as const }],
      }),
    );
    expect(partialHtml).toContain(t("merge_suggestions.action.apply"));

    const appliedHtml = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, {
        ...base,
        suggestions: [
          {
            ...base.suggestions[0],
            latestDecision: "accept" as const,
            representativeResolvedBy: "repOf" as const,
          },
        ],
      }),
    );
    expect(appliedHtml).toContain(t("merge_suggestions.action.applied"));
  });

  it("disables merge-decision editing controls in read-only mode", () => {
    const html = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain(t("merge_suggestions.collect_candidates"));
    expect(html).toContain("disabled");
  });

  it("renders no-audit-events helper text when audit list is empty", () => {
    const html = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, {
        ...buildProps(),
        auditEvents: [],
      })
    );

    expect(html).toContain(t("merge_suggestions.no_audit_events"));
  });

  it("provides localized trust-boundary recovery messages", () => {
    expect(t("merge_suggestions.trust_boundary.read_only", undefined, "ja")).toContain("確認用");
    expect(t("merge_suggestions.trust_boundary.untrusted_event", undefined, "ja")).toContain("判断ボタン");
  });
});
