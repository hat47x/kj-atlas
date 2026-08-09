import type { DocumentV1, MergeSuggestionDecisionEntry } from "./types";
import { resolveDecisionOriginTrace } from "./merge_traceability";

export type MergeDecisionAuditEntry = {
  decisionId: string;
  groupId: string;
  decisionType: MergeSuggestionDecisionEntry["decision"];
  actorType: "human";
  decidedAt: string;
  representativeCardId: string;
  representativeResolvedBy: "repOf" | "mergedIntoCardId" | "fallback" | "unresolved";
  sourceCardIds: string[];
  missingSourceCardIds: string[];
  cardIds: string[];
  rationale?: string;
};

function sortCardIds(cardIds: string[]): string[] {
  return [...new Set(cardIds)].sort((left, right) => left.localeCompare(right));
}

export function buildMergeDecisionAuditEntries(document: DocumentV1): MergeDecisionAuditEntry[] {
  const decisions = [...(document.mergeSuggestionDecisions ?? [])].sort((left, right) => {
    const byTime = left.decidedAt.localeCompare(right.decidedAt);
    if (byTime !== 0) {
      return byTime;
    }
    return left.id.localeCompare(right.id);
  });

  return decisions.map((decision) => {
    const cardIds = sortCardIds(decision.cardIds);
    // R3-tier-1 (F-9 fix): prefer the decision-time snapshot when present so the audit
    // entry stays stable across later merges of the same cards. Entries recorded before
    // this field existed have no snapshot — fall back to live re-resolution for those,
    // same as before.
    const originTrace = decision.representativeCardId !== undefined
      ? {
          representativeCardId: decision.representativeCardId,
          representativeResolvedBy: decision.representativeResolvedBy ?? "unresolved",
          sourceCardIds: decision.sourceCardIds ?? [],
          missingSourceCardIds: decision.missingSourceCardIds ?? [],
        }
      : resolveDecisionOriginTrace(document, cardIds);

    return {
      decisionId: decision.id,
      groupId: decision.groupId,
      decisionType: decision.decision,
      actorType: "human",
      decidedAt: decision.decidedAt,
      representativeCardId: originTrace.representativeCardId,
      representativeResolvedBy: originTrace.representativeResolvedBy,
      sourceCardIds: originTrace.sourceCardIds,
      missingSourceCardIds: originTrace.missingSourceCardIds,
      cardIds,
      rationale: decision.rationale,
    };
  });
}

