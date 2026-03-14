import { describe, expect, it } from "vitest";

import { validateCandidateGroupContract, validateDecisionLogContract } from "./stream_b_contract_handoff";
import { STREAM_B_CONTRACTS } from "./stream_b_contract";
import type { DocumentV2 } from "./types";

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

describe("stream_b_contract_handoff", () => {
  it("builds A2 candidate-group handoff log", () => {
    const result = validateCandidateGroupContract(createDocument());
    expect(result).toEqual({
      contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
      schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
      mockCaseId: "M1",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "heuristic:normalized-text",
    });
  });

  it("builds A3 decision-log handoff log", () => {
    const result = validateDecisionLogContract(
      createDocument(),
      {
        groupId: "g1",
        decision: "partial",
        cardIds: ["c2", "c1"],
        mergedTextDraft: "risk mitigation",
        editedText: "risk mitigation (reviewed)",
      },
      { idFactory: () => "decision-1", now: "2026-03-01T10:00:00.000Z" },
    );

    expect(result).toEqual({
      contractVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
      schemaVersion: STREAM_B_CONTRACTS.decisionLog.schemaVersion,
      mockCaseId: "M2",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "decisionId=decision-1",
    });
  });
});
