import { describe, expect, it } from "vitest";

import { collectMergeCandidates } from "./merge_candidates";
import { appendMergeSuggestionDecision } from "./merge_suggestion_decisions";
import type { DocumentV2 } from "./types";

type ValidationLog = {
  contractId: string;
  responsibility: "A2-Mock" | "A3-Implementation";
  input: Record<string, unknown>;
  expected: Record<string, unknown>;
  result: Record<string, unknown>;
};

function createDocument(): DocumentV2 {
  return {
    version: 2,
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
        snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
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

  it("validates CTR-2B-02-DECISION-LOG-V1 append contract with stub", () => {
    const next = appendMergeSuggestionDecision(
      createDocument(),
      {
        groupId: "g1",
        decision: "partial",
        cardIds: ["c2", "c1"],
        mergedTextDraft: "risk mitigation",
        editedText: "risk mitigation (reviewed)",
      },
      { idFactory: () => "decision-1", now: "2026-03-01T10:00:00.000Z" }
    );

    const entry = next.mergeSuggestionDecisions?.[0];
    const log: ValidationLog = {
      contractId: "CTR-2B-02-DECISION-LOG-V1",
      responsibility: "A3-Implementation",
      input: { action: "partial", cardIds: ["c2", "c1"] },
      expected: {
        action: "partial",
        decisionId: "decision-1",
        snapshotVersion: "CTR-2B-02-DECISION-LOG-V1",
      },
      result: {
        action: entry?.action,
        decisionId: entry?.decisionId,
        snapshotVersion: entry?.snapshotVersion,
      },
    };

    expect(entry?.action).toBe(log.expected.action);
    expect(entry?.decisionId).toBe(log.expected.decisionId);
    expect(entry?.selectedCardIds).toEqual(["c1", "c2"]);
    expect(entry?.snapshotVersion).toBe(log.expected.snapshotVersion);
    expect(entry?.decidedBy).toBe("human");
  });
});
