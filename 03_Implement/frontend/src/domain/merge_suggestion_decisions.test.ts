import { describe, expect, it } from "vitest";

import { appendMergeSuggestionDecision, getLatestMergeSuggestionDecisionByGroup } from "./merge_suggestion_decisions";
import type { DocumentV2 } from "./types";

function createBaseDocument(): DocumentV2 {
  return {
    version: 2,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "alpha", x: 0, y: 0 },
      { id: "c2", text: "Alpha", x: 100, y: 0 },
    ],
    edges: [],
    islands: [],
  };
}

describe("merge_suggestion_decisions", () => {
  it("appends decision entries with deterministic card id ordering", () => {
    const result = appendMergeSuggestionDecision(
      createBaseDocument(),
      {
        groupId: "g1",
        decision: "accept",
        cardIds: ["c2", "c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha canonical",
      },
      { idFactory: () => "d1", now: "2026-01-02T00:00:00.000Z" }
    );

    expect(result.mergeSuggestionDecisions).toEqual([
      {
        id: "d1",
        decisionId: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-01-02T00:00:00.000Z",
        decidedBy: "human",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha canonical",
        note: "alpha canonical",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
        rationale: undefined,
      },
    ]);
  });

  it("returns latest decision per group", () => {
    const decisions: DocumentV2["mergeSuggestionDecisions"] = [
      {
        id: "d1",
        groupId: "g1",
        decision: "defer",
        decidedAt: "2026-01-02T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha",
      },
      {
        id: "d2",
        groupId: "g1",
        decision: "partial",
        decidedAt: "2026-01-03T00:00:00.000Z",
        cardIds: ["c1", "c2"],
        mergedTextDraft: "alpha",
        editedText: "alpha partial",
      },
      {
        id: "d3",
        groupId: "g2",
        decision: "reject",
        decidedAt: "2026-01-01T00:00:00.000Z",
        cardIds: ["c3", "c4"],
        mergedTextDraft: "beta",
        editedText: "beta",
      },
    ];

    const latest = getLatestMergeSuggestionDecisionByGroup(decisions);

    expect(latest.get("g1")?.id).toBe("d2");
    expect(latest.get("g2")?.id).toBe("d3");
  });
});
