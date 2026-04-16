export type Ce2ProposalStatus = "proposed" | "accepted" | "rejected" | "held";
export type Ce2ProposalReviewState = "unreviewed" | "human_reviewed";

export type Ce2SuggestionCandidate = {
  proposalId: string;
  label: string;
  status: Ce2ProposalStatus;
  reviewState: Ce2ProposalReviewState;
};

type BuildSuggestionCandidatesInput = {
  hasSuggestion: boolean;
  suggestionId?: string | null;
  candidates?: Ce2SuggestionCandidate[];
};

export function buildCe2SuggestionCandidates(input: BuildSuggestionCandidatesInput): Ce2SuggestionCandidate[] {
  const explicitCandidates = input.candidates ?? [];
  if (explicitCandidates.length > 0) {
    return [...explicitCandidates];
  }

  if (!input.hasSuggestion) {
    return [];
  }

  return [
    {
      proposalId: input.suggestionId?.trim() || "proposal-current",
      label: "Current proposal",
      status: "proposed",
      reviewState: "unreviewed",
    },
  ];
}

export function summarizeCe2ReviewStates(candidates: Ce2SuggestionCandidate[]): {
  reviewed: number;
  unreviewed: number;
} {
  return candidates.reduce(
    (acc, candidate) => {
      if (candidate.reviewState === "human_reviewed") {
        acc.reviewed += 1;
      } else {
        acc.unreviewed += 1;
      }
      return acc;
    },
    { reviewed: 0, unreviewed: 0 },
  );
}
