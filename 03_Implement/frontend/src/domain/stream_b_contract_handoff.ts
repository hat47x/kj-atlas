import { collectMergeCandidates } from "./merge_candidates";
import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";
import type { DocumentV1 } from "./types";
import type { MergeMethod } from "./merge_method";
import { STREAM_B_CONTRACTS, type StreamBContractId, type StreamBSchemaVersion } from "./stream_b_contract";

export type StreamBValidationOwner = "A1" | "A2" | "A3";

export type StreamBValidationLog = {
  contractVersion: StreamBContractId | string;
  schemaVersion: StreamBSchemaVersion | string;
  mockCaseId: "M1" | "M2" | "M3" | "M4" | string;
  validationResult: "pass" | "fail";
  ownerOfFix: StreamBValidationOwner;
  evidence: string;
};

const REQUIRED_MOCK_CASE_IDS = ["M1", "M2", "M3", "M4"] as const;
const REQUIRED_MOCK_CASE_ID_SET = new Set<string>(REQUIRED_MOCK_CASE_IDS);

export function validateCandidateGroupContract(document: DocumentV1): StreamBValidationLog {
  const first = collectMergeCandidates(document)[0];
  if (!first) {
    return {
      contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
      schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
      mockCaseId: "M4",
      validationResult: "fail",
      ownerOfFix: "A2",
      evidence: "candidate group not generated",
    };
  }

  const isValid = first.snapshotVersion === STREAM_B_CONTRACTS.candidateGroup.contractId && first.reasonCodes.length > 0;
  return {
    contractVersion: STREAM_B_CONTRACTS.candidateGroup.contractId,
    schemaVersion: STREAM_B_CONTRACTS.candidateGroup.schemaVersion,
    mockCaseId: isValid ? "M1" : "M3",
    validationResult: isValid ? "pass" : "fail",
    ownerOfFix: isValid ? "A3" : "A2",
    evidence: isValid ? first.reasonCodes.join(",") : "snapshotVersion/reasonCodes mismatch",
  };
}

type ValidateDecisionLogInput = {
  groupId: string;
  decision: MergeSuggestionDecision;
  cardIds: string[];
  mergedTextDraft: string;
  editedText: string;
  mergeMethod: MergeMethod;
};

export function validateDecisionLogContract(
  document: DocumentV1,
  input: ValidateDecisionLogInput,
  options?: { idFactory?: () => string; now?: string },
): StreamBValidationLog {
  const next = appendMergeSuggestionDecision(document, input, options);
  const entry = next.mergeSuggestionDecisions?.at(-1);

  const isValid =
    entry?.snapshotVersion === STREAM_B_CONTRACTS.decisionLog.contractId &&
    entry.action === input.decision &&
    entry.mergeMethod === input.mergeMethod &&
    entry.decisionId !== undefined &&
    entry.decisionId.length > 0;

  return {
    contractVersion: STREAM_B_CONTRACTS.decisionLog.contractId,
    schemaVersion: STREAM_B_CONTRACTS.decisionLog.schemaVersion,
    mockCaseId: isValid ? "M2" : "M3",
    validationResult: isValid ? "pass" : "fail",
    ownerOfFix: isValid ? "A3" : "A2",
    evidence: isValid ? `decisionId=${entry?.decisionId}` : "decision append mismatch",
  };
}

export function evaluateStreamBA3GoNoGo(logs: StreamBValidationLog[]): { go: boolean; reason: string } {
  const ids = new Set<string>();

  for (const log of logs) {
    if (!REQUIRED_MOCK_CASE_ID_SET.has(log.mockCaseId)) {
      return { go: false, reason: `invalid mock case: ${log.mockCaseId}` };
    }

    if (log.evidence.trim().length === 0) {
      return { go: false, reason: `empty evidence: ${log.mockCaseId}` };
    }

    if (log.contractVersion !== STREAM_B_CONTRACTS.candidateGroup.contractId && log.contractVersion !== STREAM_B_CONTRACTS.decisionLog.contractId) {
      return { go: false, reason: `invalid contract version: ${log.contractVersion}` };
    }

    if (log.schemaVersion !== STREAM_B_CONTRACTS.candidateGroup.schemaVersion && log.schemaVersion !== STREAM_B_CONTRACTS.decisionLog.schemaVersion) {
      return { go: false, reason: `invalid schema version: ${log.schemaVersion}` };
    }

    if (ids.has(log.mockCaseId)) {
      return { go: false, reason: `duplicate mock case: ${log.mockCaseId}` };
    }
    ids.add(log.mockCaseId);
  }

  for (const caseId of REQUIRED_MOCK_CASE_IDS) {
    if (!ids.has(caseId)) {
      return { go: false, reason: `missing mock case: ${caseId}` };
    }
  }

  const findCase = (caseId: (typeof REQUIRED_MOCK_CASE_IDS)[number]): StreamBValidationLog =>
    logs.find((log) => log.mockCaseId === caseId)!;

  const m1 = findCase("M1");
  const m2 = findCase("M2");
  const m3 = findCase("M3");
  const m4 = findCase("M4");

  if (m1.validationResult !== "pass" || m2.validationResult !== "pass") {
    return { go: false, reason: "M1/M2 must be pass" };
  }

  if (m3.validationResult !== "fail" || m4.validationResult !== "fail") {
    return { go: false, reason: "M3/M4 must be fail" };
  }

  if (m1.ownerOfFix !== "A3" || m2.ownerOfFix !== "A3") {
    return { go: false, reason: "M1/M2 ownerOfFix must be A3" };
  }

  if (m3.ownerOfFix !== "A2" || m4.ownerOfFix !== "A2") {
    return { go: false, reason: "M3/M4 ownerOfFix must be A2" };
  }

  return { go: true, reason: "go" };
}
