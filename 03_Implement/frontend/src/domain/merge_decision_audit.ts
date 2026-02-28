import type { DocumentV2, MergeSuggestionDecisionEntry } from "./types";

export type MergeDecisionAuditEntry = {
  decisionId: string;
  groupId: string;
  decisionType: MergeSuggestionDecisionEntry["decision"];
  actorType: "human";
  decidedAt: string;
  representativeCardId: string;
  sourceCardIds: string[];
  cardIds: string[];
  rationale?: string;
};

function sortCardIds(cardIds: string[]): string[] {
  return [...new Set(cardIds)].sort((left, right) => left.localeCompare(right));
}

function resolveRepresentativeCardId(document: DocumentV2, decisionCardIds: string[]): string {
  const decisionSet = new Set(decisionCardIds);
  const representativeFromRepOf = document.cards.find((card) => {
    if (!card.repOf || card.repOf.length === 0) {
      return false;
    }
    return card.repOf.some((sourceId) => decisionSet.has(sourceId));
  });
  if (representativeFromRepOf) {
    return representativeFromRepOf.id;
  }

  return decisionCardIds[0] ?? "";
}

function resolveSourceCardIds(document: DocumentV2, representativeCardId: string, decisionCardIds: string[]): string[] {
  const representative = document.cards.find((card) => card.id === representativeCardId);
  if (representative?.repOf && representative.repOf.length > 0) {
    return sortCardIds(representative.repOf);
  }
  return sortCardIds(decisionCardIds.filter((cardId) => cardId !== representativeCardId));
}

export function buildMergeDecisionAuditEntries(document: DocumentV2): MergeDecisionAuditEntry[] {
  const decisions = [...(document.mergeSuggestionDecisions ?? [])].sort((left, right) => {
    const byTime = left.decidedAt.localeCompare(right.decidedAt);
    if (byTime !== 0) {
      return byTime;
    }
    return left.id.localeCompare(right.id);
  });

  return decisions.map((decision) => {
    const cardIds = sortCardIds(decision.cardIds);
    const representativeCardId = resolveRepresentativeCardId(document, cardIds);

    return {
      decisionId: decision.id,
      groupId: decision.groupId,
      decisionType: decision.decision,
      actorType: "human",
      decidedAt: decision.decidedAt,
      representativeCardId,
      sourceCardIds: resolveSourceCardIds(document, representativeCardId, cardIds),
      cardIds,
      rationale: decision.rationale,
    };
  });
}

