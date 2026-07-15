import type { Card, DocumentV1, HoldState } from "./types";

export type HoldStateSelection = HoldState | "active";

export function updateCardHoldState(
  cards: readonly Card[],
  cardId: string,
  selection: HoldStateSelection,
): Card[] {
  const nextHoldState = selection === "active" ? undefined : selection;

  return cards.map((card) => {
    if (card.id !== cardId || card.holdState === nextHoldState) {
      return card;
    }

    const { holdState: _currentHoldState, ...cardWithoutHoldState } = card;
    return nextHoldState
      ? { ...cardWithoutHoldState, holdState: nextHoldState }
      : cardWithoutHoldState;
  });
}

export function updateCardHoldStateAndShelf(
  document: DocumentV1,
  cardId: string,
  selection: HoldStateSelection,
  shelvedAt: string,
): DocumentV1 {
  const cards = updateCardHoldState(document.cards, cardId, selection);
  const cardsChanged = cards.some((card, index) => card !== document.cards[index]);
  const currentShelf = document.shelf ?? [];
  const existingEntry = currentShelf.find((entry) => entry.cardId === cardId);
  const shelf = selection === "shelved"
    ? existingEntry
      ? currentShelf
      : [...currentShelf, { cardId, shelvedAt }]
    : currentShelf.filter((entry) => entry.cardId !== cardId);

  if (!cardsChanged && shelf === currentShelf) {
    return document;
  }

  return {
    ...document,
    cards: cardsChanged ? cards : document.cards,
    ...(shelf.length > 0 ? { shelf } : { shelf: undefined }),
  };
}
