import type { DocumentV2 } from "./types";

export const MERGE_SUGGESTION_DECISIONS = ["accept", "partial", "reject", "defer"] as const;
const DECISION_LOG_SNAPSHOT_VERSION = "CTR-2B-02-DECISION-LOG-V1";

export type MergeSuggestionDecision = (typeof MERGE_SUGGESTION_DECISIONS)[number];

export type MergeSuggestionDecisionEntry = {
  id: string;
  decisionId?: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  action?: MergeSuggestionDecision;
  decidedAt: string;
  decidedBy?: string;
  cardIds: string[];
  selectedCardIds?: string[];
  mergedTextDraft: string;
  editedText: string;
  note?: string;
  snapshotVersion?: string;
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

  const sortedCardIds = sortCardIds(input.cardIds);
  const decisionId = idFactory();
  const entry: MergeSuggestionDecisionEntry = {
    id: decisionId,
    decisionId,
    groupId: input.groupId,
    decision: input.decision,
    action: input.decision,
    decidedAt: now,
    decidedBy: "human",
    cardIds: sortedCardIds,
    selectedCardIds: sortedCardIds,
    mergedTextDraft: input.mergedTextDraft,
    editedText: input.editedText,
    note: input.editedText,
    snapshotVersion: DECISION_LOG_SNAPSHOT_VERSION,
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
