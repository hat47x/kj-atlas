import { describe, expect, it } from "vitest";

import { collectMergeCandidates } from "./merge_candidates";
import { appendMergeSuggestionDecision, restoreMergeSuggestionDecisionsBySnapshot } from "./merge_suggestion_decisions";
import { STREAM_B_CONTRACTS } from "./stream_b_contract";
import type { DocumentV1 } from "./types";

type ValidationLog = {
  contractId: string;
  responsibility: "A2-Mock" | "A3-Implementation";
  input: Record<string, unknown>;
  expected: Record<string, unknown>;
  result: Record<string, unknown>;
};

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-stream-b",
    createdAt: "2026-03-01T00:00:00.000Z",
    updatedAt: "2026-03-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Risk mitigation", x: 0, y: 0 },
      { id: "c2", text: "risk mitigation", x: 10, y: 0 },
      { id: "c3", text: "Timeline", x: 20, y: 0 },
    ],
    edges: [],
    islands: [],
    mergeSuggestionDecisions: [],
  };
}

describe("Stream B A2 mock validation", () => {
  it("validates CTR-2B-01-CANDIDATE-GROUP-V1 with deterministic fixture", () => {
    const document = createDocument();
    const groups = collectMergeCandidates(document);
    const first = groups[0];

    const log: ValidationLog = {
      contractId: "CTR-2B-01-CANDIDATE-GROUP-V1",
      responsibility: "A2-Mock",
      input: { cardCount: document.cards.length },
      expected: {
        snapshotVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        reasonCodes: ["heuristic:normalized-text"],
      },
      result: {
        snapshotVersion: first?.snapshotVersion,
        reasonCodes: first?.reasonCodes,
      },
    };

    expect(first?.targetCardId).toBe("c1");
    expect(first?.candidateCardIds).toEqual(["c2"]);
    expect(first?.snapshotVersion).toBe(log.expected.snapshotVersion);
    expect(first?.reasonCodes).toEqual(log.expected.reasonCodes);
  });

  it("validates CTR-2B-02-DECISION-LOG-V1 append and restore flow with stub fixtures", () => {
    const orderedActions = ["accept", "partial", "reject", "defer"] as const;
    const decidedAtByAction: Record<(typeof orderedActions)[number], string> = {
      accept: "2026-03-01T10:00:00.000Z",
      partial: "2026-03-01T10:01:00.000Z",
      reject: "2026-03-01T10:02:00.000Z",
      defer: "2026-03-01T10:03:00.000Z",
    };

    const next = orderedActions.reduce((current, action) => {
      return appendMergeSuggestionDecision(
        current,
        {
          groupId: "g1",
          mergeMethod: "near_duplicate",
          decision: action,
          cardIds: ["c2", "c1"],
          mergedTextDraft: "risk mitigation",
          editedText: `risk mitigation (${action})`,
        },
        { idFactory: () => `decision-${action}`, now: decidedAtByAction[action] }
      );
    }, createDocument());

    const restored = restoreMergeSuggestionDecisionsBySnapshot(next.mergeSuggestionDecisions, STREAM_B_CONTRACTS.decisionLog.contractId);

    const log: ValidationLog = {
      contractId: "CTR-2B-02-DECISION-LOG-V1",
      responsibility: "A2-Mock",
      input: { appendOrder: orderedActions, snapshotVersion: STREAM_B_CONTRACTS.decisionLog.contractId },
      expected: {
        restoredActionsInOrder: orderedActions,
        restoredCount: orderedActions.length,
        noAutoRepresentativeCommit: true,
      },
      result: {
        restoredActionsInOrder: restored.map((entry) => entry.action),
        restoredCount: restored.length,
        noAutoRepresentativeCommit: restored.every((entry) => entry.decidedBy === "human"),
      },
    };

    expect(restored.map((entry) => entry.action)).toEqual(log.expected.restoredActionsInOrder);
    expect(restored.length).toBe(log.expected.restoredCount);
    expect(restored.every((entry) => entry.selectedCardIds?.join(",") === "c1,c2")).toBe(true);
    expect(restored.every((entry) => entry.decidedBy === "human")).toBe(log.expected.noAutoRepresentativeCommit);
  });

  it("restores only human-confirmed decisions after reload", () => {
    const decisions = [
      {
        id: "d1",
        decisionId: "d1",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-03-01T10:00:00.000Z",
        decidedBy: "human",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "risk mitigation",
        editedText: "risk mitigation",
        note: "risk mitigation",
        snapshotVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
      },
      {
        id: "d2",
        decisionId: "d2",
        groupId: "g1",
        decision: "accept",
        action: "accept",
        decidedAt: "2026-03-01T10:01:00.000Z",
        decidedBy: "system",
        cardIds: ["c1", "c2"],
        selectedCardIds: ["c1", "c2"],
        mergedTextDraft: "risk mitigation",
        editedText: "risk mitigation",
        note: "risk mitigation",
        snapshotVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
      },
    ] as DocumentV1["mergeSuggestionDecisions"];

    const restored = restoreMergeSuggestionDecisionsBySnapshot(decisions, STREAM_B_CONTRACTS.decisionLog.contractId);

    expect(restored).toHaveLength(1);
    expect(restored[0]?.id).toBe("d1");
  });

});
