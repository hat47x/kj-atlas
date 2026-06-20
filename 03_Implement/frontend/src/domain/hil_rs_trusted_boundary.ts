export type MergeDecisionTrustBoundaryInput = {
  isReadOnly: boolean;
  isTrustedEvent: boolean;
};

export type MergeDecisionTrustBoundaryResult = {
  allowDecision: boolean;
  rejectionReason: "read_only" | "untrusted_event" | null;
};

export function evaluateMergeDecisionTrustBoundary({
  isReadOnly,
  isTrustedEvent,
}: MergeDecisionTrustBoundaryInput): MergeDecisionTrustBoundaryResult {
  if (isReadOnly) {
    return {
      allowDecision: false,
      rejectionReason: "read_only",
    };
  }

  if (!isTrustedEvent) {
    return {
      allowDecision: false,
      rejectionReason: "untrusted_event",
    };
  }

  return {
    allowDecision: true,
    rejectionReason: null,
  };
}
