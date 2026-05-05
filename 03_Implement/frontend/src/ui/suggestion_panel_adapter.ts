import { buildCe2ProposalOnlyState } from "../domain/ce2_proposal_only";
import {
  buildCe2SuggestionCandidates,
  summarizeCe2ReviewStates,
  type Ce2SuggestionCandidate,
} from "../domain/ce2_suggestion_candidates";

export type SuggestionPanelAdapter = {
  buildProposalOnlyState: typeof buildCe2ProposalOnlyState;
  buildCandidates: typeof buildCe2SuggestionCandidates;
  summarizeReviewStates: typeof summarizeCe2ReviewStates;
};

export const defaultSuggestionPanelAdapter: SuggestionPanelAdapter = {
  buildProposalOnlyState: buildCe2ProposalOnlyState,
  buildCandidates: buildCe2SuggestionCandidates,
  summarizeReviewStates: summarizeCe2ReviewStates,
};

export type { Ce2SuggestionCandidate };
