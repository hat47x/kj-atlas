import type { Card, HoldState } from "./types";

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
