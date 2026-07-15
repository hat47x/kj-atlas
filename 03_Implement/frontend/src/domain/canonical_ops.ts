import type { Card, DocumentV1, Island } from "./types";

export type ApplyCanonicalizationInput = {
  sourceCardIds: string[];
  mergedText: string;
  canonicalId?: string;
  canonicalIdFactory?: () => string;
};

export type ApplyCanonicalizationResult = {
  document: DocumentV1;
  canonicalId: string;
};

function uniqueIds(ids: string[]): string[] {
  const seen = new Set<string>();
  const unique: string[] = [];

  for (const id of ids) {
    if (!seen.has(id)) {
      seen.add(id);
      unique.push(id);
    }
  }

  return unique;
}

function computeAveragePosition(cards: Card[]): { x: number; y: number } {
  const sum = cards.reduce(
    (acc, card) => ({
      x: acc.x + card.x,
      y: acc.y + card.y,
    }),
    { x: 0, y: 0 }
  );

  return {
    x: sum.x / cards.length,
    y: sum.y / cards.length,
  };
}

function updateIslands(islands: Island[], sourceCardIdSet: Set<string>, canonicalId: string): Island[] {
  let didChange = false;

  const nextIslands = islands.map((island) => {
    const containsSourceCard = island.cardIds.some((cardId) => sourceCardIdSet.has(cardId));
    if (!containsSourceCard || island.cardIds.includes(canonicalId)) {
      return island;
    }

    didChange = true;
    return {
      ...island,
      cardIds: [...island.cardIds, canonicalId],
    };
  });

  return didChange ? nextIslands : islands;
}

function updateReadingOrder(
  readingOrder: string[] | undefined,
  sourceCardIdSet: Set<string>,
  canonicalId: string
): string[] | undefined {
  if (!readingOrder || readingOrder.length === 0) {
    return readingOrder;
  }

  const firstSourceIndex = readingOrder.findIndex((cardId) => sourceCardIdSet.has(cardId));
  if (firstSourceIndex === -1) {
    return readingOrder;
  }

  const filteredReadingOrder = readingOrder.filter((cardId) => !sourceCardIdSet.has(cardId));
  const insertionIndex = Math.min(firstSourceIndex, filteredReadingOrder.length);

  return [
    ...filteredReadingOrder.slice(0, insertionIndex),
    canonicalId,
    ...filteredReadingOrder.slice(insertionIndex),
  ];
}

export function applyCanonicalization(
  document: DocumentV1,
  input: ApplyCanonicalizationInput
): ApplyCanonicalizationResult {
  const sourceCardIds = uniqueIds(input.sourceCardIds);
  if (sourceCardIds.length < 2) {
    throw new Error("applyCanonicalization requires at least 2 source card ids");
  }

  const sourceCardIdSet = new Set(sourceCardIds);
  const sourceCards = document.cards.filter((card) => sourceCardIdSet.has(card.id));
  if (sourceCards.length !== sourceCardIds.length) {
    throw new Error("applyCanonicalization source cards must exist in document");
  }

  const canonicalId = input.canonicalId ?? input.canonicalIdFactory?.();
  if (!canonicalId) {
    throw new Error("applyCanonicalization requires canonicalId or canonicalIdFactory");
  }
  if (document.cards.some((card) => card.id === canonicalId)) {
    throw new Error("applyCanonicalization canonical id already exists");
  }

  const average = computeAveragePosition(sourceCards);
  const canonicalCard: Card = {
    id: canonicalId,
    text: input.mergedText,
    x: average.x,
    y: average.y,
    sources: sourceCardIds,
    textReviewed: false,
  };

  const nextCards = [
    ...document.cards.map((card) =>
      sourceCardIdSet.has(card.id)
        ? {
            ...card,
            canonicalId,
          }
        : card
    ),
    canonicalCard,
  ];

  return {
    canonicalId,
    document: {
      ...document,
      cards: nextCards,
      islands: updateIslands(document.islands, sourceCardIdSet, canonicalId),
      readingOrder: updateReadingOrder(document.readingOrder, sourceCardIdSet, canonicalId),
    },
  };
}
