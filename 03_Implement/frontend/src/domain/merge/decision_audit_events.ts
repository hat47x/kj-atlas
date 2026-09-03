import type { MergeSuggestionDecision } from "../merge_suggestion_decisions";

export const MERGE_DECISION_AUDIT_EVENT_LIMIT = 50;

export type MergeDecisionAuditEvent = {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  decidedBy: "human";
  cardIds: string[];
  selectedCardIds?: string[];
  snapshotVersion: string;
  decisionReason?: string;
};

function sortCardIds(cardIds: string[]): string[] {
  return [...new Set(cardIds)].sort((left, right) => left.localeCompare(right));
}

export function createMergeDecisionAuditEvent(input: {
  eventId: string;
  groupId: string;
  decision: MergeSuggestionDecision;
  decidedAt: string;
  cardIds: string[];
  selectedCardIds?: string[];
  snapshotVersion: string;
  decisionReason?: string;
}): MergeDecisionAuditEvent {
  return {
    eventId: input.eventId,
    groupId: input.groupId,
    decision: input.decision,
    decidedAt: input.decidedAt,
    decidedBy: "human",
    cardIds: sortCardIds(input.cardIds),
    selectedCardIds: input.selectedCardIds ? sortCardIds(input.selectedCardIds) : undefined,
    snapshotVersion: input.snapshotVersion,
    decisionReason: input.decisionReason,
  };
}

export function appendMergeDecisionAuditEvent(
  current: readonly MergeDecisionAuditEvent[],
  event: MergeDecisionAuditEvent
): MergeDecisionAuditEvent[] {
  const next = [...current, event];
  return next.length <= MERGE_DECISION_AUDIT_EVENT_LIMIT
    ? next
    : next.slice(next.length - MERGE_DECISION_AUDIT_EVENT_LIMIT);
}
