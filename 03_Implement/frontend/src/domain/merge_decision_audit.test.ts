import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "./types";
import { buildMergeDecisionAuditEntries } from "./merge_decision_audit";

function createDocument(overrides: Partial<DocumentV1> = {}): DocumentV1 {
  return {
    version: 1,
    id: "doc-audit",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    ...overrides,
  };
}

describe("merge_decision_audit", () => {
  it("builds deterministic audit entries with representative/source mapping", () => {
    const doc = createDocument({
      cards: [
        { id: "c-rep", text: "canonical", x: 0, y: 0, repOf: ["c-a", "c-b"] },
        { id: "c-a", text: "source a", x: 100, y: 0, mergedIntoCardId: "c-rep" },
        { id: "c-b", text: "source b", x: 200, y: 0, mergedIntoCardId: "c-rep" },
      ],
      mergeSuggestionDecisions: [
        {
          id: "d-late",
          groupId: "group-1",
          decision: "accept",
          decidedAt: "2026-01-03T00:00:00.000Z",
          cardIds: ["c-b", "c-a"],
          mergedTextDraft: "merged",
          editedText: "merged edited",
          rationale: "same meaning",
        },
        {
          id: "d-early",
          groupId: "group-2",
          decision: "defer",
          decidedAt: "2026-01-02T00:00:00.000Z",
          cardIds: ["c-z", "c-y"],
          mergedTextDraft: "draft",
          editedText: "draft",
        },
      ],
    });

    expect(buildMergeDecisionAuditEntries(doc)).toEqual([
      {
        actorType: "human",
        cardIds: ["c-y", "c-z"],
        decisionId: "d-early",
        decisionType: "defer",
        decidedAt: "2026-01-02T00:00:00.000Z",
        groupId: "group-2",
        representativeCardId: "c-y",
        representativeResolvedBy: "fallback",
        sourceCardIds: ["c-z"],
        missingSourceCardIds: [],
      },
      {
        actorType: "human",
        cardIds: ["c-a", "c-b"],
        decisionId: "d-late",
        decisionType: "accept",
        decidedAt: "2026-01-03T00:00:00.000Z",
        groupId: "group-1",
        rationale: "same meaning",
        representativeCardId: "c-rep",
        representativeResolvedBy: "repOf",
        sourceCardIds: ["c-a", "c-b"],
        missingSourceCardIds: [],
      },
    ]);
  });

  it("keeps missing source ids in audit entries when representative source was deleted", () => {
    const doc = createDocument({
      cards: [
        { id: "c-rep", text: "canonical", x: 0, y: 0, repOf: ["c-live", "c-deleted"] },
        { id: "c-live", text: "source live", x: 100, y: 0, mergedIntoCardId: "c-rep" },
      ],
      mergeSuggestionDecisions: [
        {
          id: "d-1",
          groupId: "group-1",
          decision: "accept",
          decidedAt: "2026-01-03T00:00:00.000Z",
          cardIds: ["c-live"],
          mergedTextDraft: "merged",
          editedText: "merged",
        },
      ],
    });

    expect(buildMergeDecisionAuditEntries(doc)).toEqual([
      {
        actorType: "human",
        cardIds: ["c-live"],
        decisionId: "d-1",
        decisionType: "accept",
        decidedAt: "2026-01-03T00:00:00.000Z",
        groupId: "group-1",
        representativeCardId: "c-rep",
        representativeResolvedBy: "repOf",
        sourceCardIds: ["c-live"],
        missingSourceCardIds: ["c-deleted"],
      },
    ]);
  });


  it("returns empty entries when no decisions are recorded", () => {
    expect(buildMergeDecisionAuditEntries(createDocument())).toEqual([]);
  });
});

