import { describe, expect, it } from "vitest";

import {
  evaluateStreamBA3GoNoGo,
  validateCandidateGroupContract,
  validateDecisionLogContract,
} from "./stream_b_contract_handoff";
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

  it("returns go when M1-M4 logs satisfy A2→A3 handoff constraints", () => {
    const logs = [
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M1",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "candidate group contract pass",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
        schemaVersion: STREAM_B_CONTRACTS.decisionLog.schemaVersion,
        mockCaseId: "M2",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "decision log contract pass",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M3",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "invalid snapshotVersion/reasonCodes",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M4",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "candidate group not generated",
      },
    ] as const;

    expect(evaluateStreamBA3GoNoGo([...logs])).toEqual({ go: true, reason: "go" });
  });

  it("returns NoGo when mock cases contain duplicates", () => {
    const duplicate = {
      contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
      schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
      mockCaseId: "M1",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "duplicate",
    } as const;

    expect(evaluateStreamBA3GoNoGo([duplicate, duplicate])).toEqual({
      go: false,
      reason: "duplicate mock case: M1",
    });
  });

  it("returns NoGo when fail cases are assigned to A3", () => {
    const logs = [
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M1",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "M1",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
        schemaVersion: STREAM_B_CONTRACTS.decisionLog.schemaVersion,
        mockCaseId: "M2",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "M2",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M3",
        validationResult: "fail",
        ownerOfFix: "A3",
        evidence: "M3",
      },
      {
        contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
        schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
        mockCaseId: "M4",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "M4",
      },
    ] as const;

    expect(evaluateStreamBA3GoNoGo([...logs])).toEqual({
      go: false,
      reason: "M3/M4 ownerOfFix must not be A3",
    });
  });
});
