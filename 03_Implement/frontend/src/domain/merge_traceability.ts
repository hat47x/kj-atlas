import type { Card, DocumentV2 } from "./types";

export type RepresentativeOriginTrace = {
  representativeCardId: string;
  sourceCardIds: string[];
  missingSourceCardIds: string[];
};

function sortIds(ids: Iterable<string>): string[] {
  return [...new Set(ids)].sort((left, right) => left.localeCompare(right));
}

function resolveRepresentativeCard(document: DocumentV2, cardIds: string[]): Card | undefined {
  const decisionCardIdSet = new Set(cardIds);

  const representativeByRepOf = document.cards.find((card) => {
    if (!Array.isArray(card.repOf) || card.repOf.length === 0) {
      return false;
    }
    return card.repOf.some((sourceCardId) => decisionCardIdSet.has(sourceCardId));
  });
  if (representativeByRepOf) {
    return representativeByRepOf;
  }

  const representativeByMergedInto = document.cards.find((card) => {
    if (!card.mergedIntoCardId) {
      return false;
    }
    return decisionCardIdSet.has(card.id);
  });
  if (representativeByMergedInto?.mergedIntoCardId) {
    return document.cards.find((card) => card.id === representativeByMergedInto.mergedIntoCardId);
  }

  const representativeFallbackId = cardIds[0];
  if (!representativeFallbackId) {
    return undefined;
  }

  return document.cards.find((card) => card.id === representativeFallbackId) ?? {
    id: representativeFallbackId,
    text: "",
    x: 0,
    y: 0,
  };
}

export function resolveRepresentativeOriginTrace(document: DocumentV2, representativeCardId: string): RepresentativeOriginTrace {
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
  };
}

export function resolveDecisionOriginTrace(document: DocumentV2, cardIds: string[]): RepresentativeOriginTrace {
  const sortedCardIds = sortIds(cardIds);
  const representative = resolveRepresentativeCard(document, sortedCardIds);
  const representativeCardId = representative?.id ?? "";
  if (!representativeCardId) {
    return {
      representativeCardId: "",
      sourceCardIds: [],
      missingSourceCardIds: [],
    };
  }

  const representativeTrace = resolveRepresentativeOriginTrace(document, representativeCardId);
  if (representativeTrace.sourceCardIds.length > 0 || representativeTrace.missingSourceCardIds.length > 0) {
    return representativeTrace;
  }

  return {
    representativeCardId,
    sourceCardIds: sortIds(sortedCardIds.filter((cardId) => cardId !== representativeCardId)),
    missingSourceCardIds: [],
  };
}

