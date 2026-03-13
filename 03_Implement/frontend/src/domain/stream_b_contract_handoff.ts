import { collectMergeCandidates } from "./merge_candidates";
import { appendMergeSuggestionDecision, type MergeSuggestionDecision } from "./merge_suggestion_decisions";
import type { DocumentV2 } from "./types";

export type StreamBValidationOwner = "A1" | "A2" | "A3";

export type StreamBValidationLog = {
  contractVersion: "CTR-2B-01-CANDIDATE-GROUP-V1" | "CTR-2B-02-DECISION-LOG-V1";
  mockCaseId: "M1" | "M2" | "M3" | "M4";
  validationResult: "pass" | "fail";
  ownerOfFix: StreamBValidationOwner;
  evidence: string;
};

export function validateCandidateGroupContract(document: DocumentV2): StreamBValidationLog {
  const first = collectMergeCandidates(document)[0];
  if (!first) {
    return {
      contractVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
      mockCaseId: "M4",
      validationResult: "fail",
      ownerOfFix: "A2",
      evidence: "candidate group not generated",
    };
  }

  const isValid = first.snapshotVersion === "CTR-2B-01-CANDIDATE-GROUP-V1" && first.reasonCodes.length > 0;
  return {
    contractVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
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
};

export function validateDecisionLogContract(
  document: DocumentV2,
  input: ValidateDecisionLogInput,
  options?: { idFactory?: () => string; now?: string },
): StreamBValidationLog {
  const next = appendMergeSuggestionDecision(document, input, options);
  const entry = next.mergeSuggestionDecisions?.at(-1);

  const isValid =
    entry?.snapshotVersion === "CTR-2B-02-DECISION-LOG-V1" &&
    entry.action === input.decision &&
    entry.decisionId !== undefined &&
    entry.decisionId.length > 0;

  return {
    contractVersion: "CTR-2B-02-DECISION-LOG-V1",
    mockCaseId: isValid ? "M2" : "M3",
    validationResult: isValid ? "pass" : "fail",
    ownerOfFix: isValid ? "A3" : "A2",
    evidence: isValid ? `decisionId=${entry?.decisionId}` : "decision append mismatch",
  };
}
