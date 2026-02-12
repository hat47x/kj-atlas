import type { Card } from "./types";

export type AlignDirection = "left" | "right" | "top" | "bottom";

export type DistributeDirection = "horizontal" | "vertical";

export type AlignOptions = {
  cardWidth?: number;
  cardHeight?: number;
};

export type DistributeOptions = {
  cardWidth?: number;
  cardHeight?: number;
};

export type SnapOptions = {
  gridSize: number;
};

const DEFAULT_CARD_WIDTH = 220;
const DEFAULT_CARD_HEIGHT = 80;

function toSelectedIdSet(selectedIds: string[]): Set<string> {
  return new Set(selectedIds);
}

function updateCardsById(cards: Card[], nextPositionById: Map<string, { x: number; y: number }>): Card[] {
  let didChange = false;

  const nextCards = cards.map((card) => {
    const nextPosition = nextPositionById.get(card.id);
    if (!nextPosition) {
      return card;
    }

    if (card.x === nextPosition.x && card.y === nextPosition.y) {
      return card;
    }

    didChange = true;
    return {
      ...card,
      x: nextPosition.x,
      y: nextPosition.y,
    };
  });

  return didChange ? nextCards : cards;
}

export function alignSelectedCards(
  cards: Card[],
  selectedIds: string[],
  direction: AlignDirection,
  options: AlignOptions = {}
): Card[] {
  const selectedIdSet = toSelectedIdSet(selectedIds);
  const selectedCards = cards.filter((card) => selectedIdSet.has(card.id));

  if (selectedCards.length < 2) {
    return cards;
  }

  const cardWidth = options.cardWidth ?? DEFAULT_CARD_WIDTH;
  const cardHeight = options.cardHeight ?? DEFAULT_CARD_HEIGHT;

  const anchor =
    direction === "left"
      ? Math.min(...selectedCards.map((card) => card.x))
      : direction === "right"
        ? Math.max(...selectedCards.map((card) => card.x + cardWidth))
        : direction === "top"
          ? Math.min(...selectedCards.map((card) => card.y))
          : Math.max(...selectedCards.map((card) => card.y + cardHeight));

  const nextPositionById = new Map<string, { x: number; y: number }>();
  for (const card of selectedCards) {
    nextPositionById.set(card.id, {
      x: direction === "left" ? anchor : direction === "right" ? anchor - cardWidth : card.x,
      y: direction === "top" ? anchor : direction === "bottom" ? anchor - cardHeight : card.y,
    });
  }

  return updateCardsById(cards, nextPositionById);
}

export function distributeSelectedCards(
  cards: Card[],
  selectedIds: string[],
  direction: DistributeDirection,
  _options: DistributeOptions = {}
): Card[] {
  const selectedIdSet = toSelectedIdSet(selectedIds);
  const selectedCards = cards.filter((card) => selectedIdSet.has(card.id));

  if (selectedCards.length < 3) {
    return cards;
  }

  const isHorizontal = direction === "horizontal";
  const sortedCards = [...selectedCards].sort((a, b) => (isHorizontal ? a.x - b.x : a.y - b.y));

  const first = sortedCards[0];
  const last = sortedCards[sortedCards.length - 1];
  const span = isHorizontal ? last.x - first.x : last.y - first.y;
  const step = span / (sortedCards.length - 1);

  const nextPositionById = new Map<string, { x: number; y: number }>();
  sortedCards.forEach((card, index) => {
    nextPositionById.set(card.id, {
      x: isHorizontal ? first.x + step * index : card.x,
      y: isHorizontal ? card.y : first.y + step * index,
    });
  });

  return updateCardsById(cards, nextPositionById);
}

export function snapValueToGrid(value: number, options: SnapOptions): number {
  if (options.gridSize <= 0) {
    return value;
  }

  return Math.round(value / options.gridSize) * options.gridSize;
}
