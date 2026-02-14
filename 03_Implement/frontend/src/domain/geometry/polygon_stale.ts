import type { Card, Island } from "../types";

export function buildCardVersionToken(card: Card, cardWidth: number, cardHeight: number): string {
  return `${card.id}:${card.x},${card.y},${cardWidth},${cardHeight}`;
}

export function buildVersionTokenForCardIds(
  cards: Card[],
  cardIds: string[],
  cardWidth: number,
  cardHeight: number
): string {
  const cardsById = new Map(cards.map((card) => [card.id, card]));

  return cardIds
    .map((cardId) => {
      const card = cardsById.get(cardId);
      return card ? buildCardVersionToken(card, cardWidth, cardHeight) : `${cardId}:missing`;
    })
    .join("|");
}

export function isPolygonShapeStale(island: Island, cards: Card[], cardWidth: number, cardHeight: number): boolean {
  if (island.shape?.kind !== "polygon" || !island.shape.generatedFrom) {
    return false;
  }

  const { cardIds, versionToken } = island.shape.generatedFrom;
  if (cardIds.length === 0) {
    return false;
  }

  if (cardIds.length !== island.cardIds.length || cardIds.some((cardId, index) => cardId !== island.cardIds[index])) {
    return true;
  }

  const currentToken = buildVersionTokenForCardIds(cards, cardIds, cardWidth, cardHeight);
  return currentToken !== versionToken;
}
