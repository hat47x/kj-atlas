export type MergeDecisionTrustBoundaryInput = {
  isReadOnly: boolean;
  isTrustedEvent: boolean;
};

export type MergeDecisionTrustBoundaryResult = {
  allowDecision: boolean;
  errorMessage: string | null;
};

const TRUSTED_DECISION_ERROR = "Merge decision must be triggered by a trusted human interaction.";

export function evaluateMergeDecisionTrustBoundary({
  isReadOnly,
  isTrustedEvent,
}: MergeDecisionTrustBoundaryInput): MergeDecisionTrustBoundaryResult {
  if (isReadOnly) {
    return {
      allowDecision: false,
      errorMessage: null,
    };
  }

  if (!isTrustedEvent) {
    return {
      allowDecision: false,
      errorMessage: TRUSTED_DECISION_ERROR,
    };
  }

  return {
    allowDecision: true,
    errorMessage: null,
  };
}

export const MERGE_DECISION_TRUSTED_ERROR_MESSAGE = TRUSTED_DECISION_ERROR;
