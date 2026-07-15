import type { DocumentV1 } from "./types";

type MergeOptions = {
  rewireMembershipAndEdges?: boolean;
};

type MergeResult = {
  nextDocument: DocumentV1;
  representativeCardId: string;
  mergedCardCount: number;
};

export function createRepresentativeMerge(
  document: DocumentV1,
  selectedCardIds: string[],
  representativeText: string,
  options: MergeOptions = {}
): MergeResult | null {
  const uniqueSelectedCardIds = Array.from(new Set(selectedCardIds));
  if (uniqueSelectedCardIds.length < 2) {
    return null;
  }

  const selectedCardSet = new Set(uniqueSelectedCardIds);
  const selectedCards = document.cards.filter((card) => selectedCardSet.has(card.id));
  if (selectedCards.length < 2) {
    return null;
  }

  const normalizedRepresentativeText = representativeText.trim();
  if (normalizedRepresentativeText.length === 0) {
    return null;
  }

  const representativeCardId = crypto.randomUUID();
  const averageX = selectedCards.reduce((sum, card) => sum + card.x, 0) / selectedCards.length;
  const averageY = selectedCards.reduce((sum, card) => sum + card.y, 0) / selectedCards.length;

  const nextCards = document.cards.map((card) => {
    if (!selectedCardSet.has(card.id)) {
      return card;
    }

    return {
      ...card,
      mergedIntoCardId: representativeCardId,
    };
  });

  nextCards.push({
    id: representativeCardId,
    text: normalizedRepresentativeText,
    x: averageX,
    y: averageY,
    repOf: uniqueSelectedCardIds,
  });

  const rewire = options.rewireMembershipAndEdges === true;

  const nextIslands = rewire
    ? document.islands.map((island) => {
        const hasMergedMember = island.cardIds.some((cardId) => selectedCardSet.has(cardId));
        if (!hasMergedMember) {
          return island;
        }

        const filteredCardIds = island.cardIds.filter((cardId) => !selectedCardSet.has(cardId));
        return {
          ...island,
          cardIds: filteredCardIds.includes(representativeCardId)
            ? filteredCardIds
            : [...filteredCardIds, representativeCardId],
        };
      })
    : document.islands;

  const nextEdges = rewire
    ? document.edges.map((edge) => {
        const fromKind = edge.fromKind ?? "card";
        const toKind = edge.toKind ?? "card";

        const nextFromId = fromKind === "card" && selectedCardSet.has(edge.fromId) ? representativeCardId : edge.fromId;
        const nextToId = toKind === "card" && selectedCardSet.has(edge.toId) ? representativeCardId : edge.toId;

        if (nextFromId === edge.fromId && nextToId === edge.toId) {
          return edge;
        }

        return {
          ...edge,
          fromId: nextFromId,
          toId: nextToId,
        };
      })
    : document.edges;

  return {
    nextDocument: {
      ...document,
      cards: nextCards,
      islands: nextIslands,
      edges: nextEdges,
    },
    representativeCardId,
    mergedCardCount: selectedCards.length,
  };
}
