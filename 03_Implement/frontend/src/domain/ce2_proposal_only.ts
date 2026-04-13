export type Ce2ProposalOnlyInput = {
  safeModeEnabled: boolean;
  previewEnabled: boolean;
  hasSuggestion: boolean;
};

export type Ce2ProposalOnlyState = {
  canRequestProposal: boolean;
  canPreviewProposal: boolean;
  canAutoApply: false;
  blockers: string[];
};

export function buildCe2ProposalOnlyState(input: Ce2ProposalOnlyInput): Ce2ProposalOnlyState {
  const blockers: string[] = ["auto_apply_blocked"];

  if (!input.safeModeEnabled) {
    blockers.push("safe_mode_required");
  }

  if (!input.hasSuggestion) {
    blockers.push("suggestion_required");
  }

  if (!input.previewEnabled) {
    blockers.push("preview_opt_in_required");
  }

  return {
    canRequestProposal: input.safeModeEnabled,
    canPreviewProposal: input.hasSuggestion,
    canAutoApply: false,
    blockers,
  };
}
