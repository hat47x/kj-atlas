import type { DocumentV2 } from "./types";

export const MERGE_SUGGESTION_DECISIONS = ["accept", "partial", "reject", "defer"] as const;

export type MergeSuggestionDecision = (typeof MERGE_SUGGESTION_DECISIONS)[number];

export type MergeSuggestionDecisionEntry = {
  id: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  cardIds: string[];
  mergedTextDraft: string;
  editedText: string;
  rationale?: string;
};

type AppendMergeSuggestionDecisionInput = {
  groupId: string;
  decision: MergeSuggestionDecision;
  cardIds: string[];
  mergedTextDraft: string;
  editedText: string;
  rationale?: string;
};

function sortCardIds(cardIds: string[]): string[] {
  return [...new Set(cardIds)].sort((left, right) => left.localeCompare(right));
}

export function appendMergeSuggestionDecision(
  document: DocumentV2,
  input: AppendMergeSuggestionDecisionInput,
  options?: { idFactory?: () => string; now?: string }
): DocumentV2 {
  const idFactory = options?.idFactory ?? (() => crypto.randomUUID());
  const now = options?.now ?? new Date().toISOString();

  const entry: MergeSuggestionDecisionEntry = {
    id: idFactory(),
    groupId: input.groupId,
    decision: input.decision,
    decidedAt: now,
    cardIds: sortCardIds(input.cardIds),
    mergedTextDraft: input.mergedTextDraft,
    editedText: input.editedText,
    rationale: input.rationale,
  };

  return {
    ...document,
    mergeSuggestionDecisions: [...(document.mergeSuggestionDecisions ?? []), entry],
  };
}

export function getLatestMergeSuggestionDecisionByGroup(
  decisions: DocumentV2["mergeSuggestionDecisions"]
): Map<string, MergeSuggestionDecisionEntry> {
  const latest = new Map<string, MergeSuggestionDecisionEntry>();
  for (const decision of decisions ?? []) {
    const current = latest.get(decision.groupId);
    if (!current || current.decidedAt <= decision.decidedAt) {
      latest.set(decision.groupId, decision);
    }
  }
  return latest;
}
