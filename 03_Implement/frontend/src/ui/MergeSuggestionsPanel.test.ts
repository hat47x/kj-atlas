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
  it("shows deterministic-heuristic guidance, decision status, and four decision actions", () => {
    const html = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, buildProps()));

    expect(html).toContain("Similar card merge candidates");
    expect(html).toContain("Deterministic heuristic only (no AI decision)");
    expect(html).toContain("Cards in candidate group");
    expect(html).toContain("Decision: Deferred");
    expect(html).toContain("a: Risk mitigation");
    expect(html).toContain("b: risk mitigation");
    expect(html).toContain("Representative: a [fallback], source count: 1");
    expect(html).toContain("Rationale: heuristic:normalized-text");
    expect(html).toContain("Audit event recorded at");
    expect(html).toContain("decision=defer");
    expect(html).toContain("Export decision audit events (JSONL)");
    expect(html).toContain("1 event(s)");
    expect(html).toContain("Draft diff preview:");
    expect(html).toContain("Accept");
    expect(html).toContain("Partially accept");
    expect(html).toContain("Reject");
    expect(html).toContain("Defer");
    expect(html).toContain("no automatic canonical merge is executed");
  });

  it("disables merge-decision editing controls in read-only mode", () => {
    const html = renderToStaticMarkup(React.createElement(MergeSuggestionsPanel, { ...buildProps(), isReadOnly: true }));

    expect(html).toContain("Collect candidates");
    expect(html).toContain("disabled");
  });

  it("renders no-audit-events helper text when audit list is empty", () => {
    const html = renderToStaticMarkup(
      React.createElement(MergeSuggestionsPanel, {
        ...buildProps(),
        auditEvents: [],
      })
    );

    expect(html).toContain("No audit events yet");
  });
});
