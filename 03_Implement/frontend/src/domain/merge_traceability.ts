import type { Card, DocumentV1 } from "./types";

export type RepresentativeOriginTrace = {
  representativeCardId: string;
  sourceCardIds: string[];
  missingSourceCardIds: string[];
  representativeResolvedBy: "repOf" | "mergedIntoCardId" | "fallback" | "unresolved";
};

function sortIds(ids: Iterable<string>): string[] {
  return [...new Set(ids)].sort((left, right) => left.localeCompare(right));
}

function resolveRepresentativeCard(
  document: DocumentV1,
  cardIds: string[]
): { card?: Card; resolvedBy: RepresentativeOriginTrace["representativeResolvedBy"] } {
  const decisionCardIdSet = new Set(cardIds);
  const normalizedDecisionCardIds = sortIds(cardIds);

  const representativeByRepOf = document.cards
    .filter((card) => Array.isArray(card.repOf) && card.repOf.length > 0)
    .map((card) => ({
      card,
      overlapCount: card.repOf?.filter((sourceCardId) => decisionCardIdSet.has(sourceCardId)).length ?? 0,
    }))
    .filter((candidate) => candidate.overlapCount > 0)
    .sort((left, right) => {
      if (left.overlapCount !== right.overlapCount) {
        return right.overlapCount - left.overlapCount;
      }
      return left.card.id.localeCompare(right.card.id);
    })[0]?.card;
  if (representativeByRepOf) {
    return {
      card: representativeByRepOf,
      resolvedBy: "repOf",
    };
  }

  const representativeByMergedInto = document.cards
    .filter((card) => decisionCardIdSet.has(card.id) && typeof card.mergedIntoCardId === "string")
    .map((card) => card.mergedIntoCardId as string)
    .sort((left, right) => left.localeCompare(right))[0];
  if (representativeByMergedInto) {
    return {
      card: document.cards.find((card) => card.id === representativeByMergedInto) ?? {
        id: representativeByMergedInto,
        text: "",
        x: 0,
        y: 0,
      },
      resolvedBy: "mergedIntoCardId",
    };
  }

  const representativeFallbackId = normalizedDecisionCardIds[0];
  if (!representativeFallbackId) {
    return { resolvedBy: "unresolved" };
  }

  return {
    card: document.cards.find((card) => card.id === representativeFallbackId) ?? {
      id: representativeFallbackId,
      text: "",
      x: 0,
      y: 0,
    },
    resolvedBy: "fallback",
  };
}

export function resolveRepresentativeOriginTrace(document: DocumentV1, representativeCardId: string): RepresentativeOriginTrace {
  const representative = document.cards.find((card) => card.id === representativeCardId);
  const cardsById = new Map(document.cards.map((card) => [card.id, card]));

  const sourceIds = new Set<string>();
  if (representative?.repOf && representative.repOf.length > 0) {
    for (const sourceId of representative.repOf) {
      sourceIds.add(sourceId);
    }
  }

  for (const card of document.cards) {
    if (card.mergedIntoCardId === representativeCardId) {
      sourceIds.add(card.id);
    }
  }

  if (representative && sourceIds.size === 0 && Array.isArray(representative.sources)) {
    for (const sourceId of representative.sources) {
      sourceIds.add(sourceId);
    }
  }

  const sortedSourceIds = sortIds(sourceIds);
  const sourceCardIds: string[] = [];
  const missingSourceCardIds: string[] = [];
  for (const sourceId of sortedSourceIds) {
    if (cardsById.has(sourceId)) {
      sourceCardIds.push(sourceId);
    } else {
      missingSourceCardIds.push(sourceId);
    }
  }

  return {
    representativeCardId,
    sourceCardIds,
    missingSourceCardIds,
    representativeResolvedBy: "repOf",
  };
}

export function resolveDecisionOriginTrace(document: DocumentV1, cardIds: string[]): RepresentativeOriginTrace {
  const sortedCardIds = sortIds(cardIds);
  const representative = resolveRepresentativeCard(document, sortedCardIds);
  const representativeCardId = representative.card?.id ?? "";
  if (!representativeCardId) {
    return {
      representativeCardId: "",
      sourceCardIds: [],
      missingSourceCardIds: [],
      representativeResolvedBy: "unresolved",
    };
  }

  const representativeTrace = resolveRepresentativeOriginTrace(document, representativeCardId);
  if (representativeTrace.sourceCardIds.length > 0 || representativeTrace.missingSourceCardIds.length > 0) {
    return {
      ...representativeTrace,
      representativeResolvedBy: representative.resolvedBy,
    };
  }

  return {
    representativeCardId,
    sourceCardIds: sortIds(sortedCardIds.filter((cardId) => cardId !== representativeCardId)),
    missingSourceCardIds: [],
    representativeResolvedBy: representative.resolvedBy,
  };
}
