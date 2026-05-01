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

export type CoreGraphNode = Pick<Card, "id" | "x" | "y">;

export type CoreGraphContractAdapter = {
  toNode(card: Card): CoreGraphNode;
  applyPosition(card: Card, next: { x: number; y: number }): Card;
};

export type RepositionAnchorMode = "centroid" | "bounds-center";

export type CoreGraphRepositionOptions = {
  targetX: number;
  targetY: number;
  selectedIds: string[];
  anchorMode?: RepositionAnchorMode;
  snapToGridSize?: number;
  adapter?: CoreGraphContractAdapter;
};

export type CoreGraphRepositionResult = {
  cards: Card[];
  usedMockAdapter: boolean;
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

function snapIfNeeded(value: number, snapToGridSize?: number): number {
  if (!snapToGridSize || snapToGridSize <= 0) {
    return value;
  }
  return snapValueToGrid(value, { gridSize: snapToGridSize });
}

function mockCoreGraphAdapter(): CoreGraphContractAdapter {
  return {
    toNode: (card) => ({ id: card.id, x: card.x, y: card.y }),
    applyPosition: (card, next) => ({ ...card, x: next.x, y: next.y }),
  };
}

function computeAnchor(nodes: CoreGraphNode[], mode: RepositionAnchorMode): { x: number; y: number } {
  if (mode === "bounds-center") {
    const minX = Math.min(...nodes.map((node) => node.x));
    const maxX = Math.max(...nodes.map((node) => node.x));
    const minY = Math.min(...nodes.map((node) => node.y));
    const maxY = Math.max(...nodes.map((node) => node.y));
    return { x: (minX + maxX) / 2, y: (minY + maxY) / 2 };
  }

  const count = nodes.length;
  const sum = nodes.reduce(
    (acc, node) => ({ x: acc.x + node.x, y: acc.y + node.y }),
    { x: 0, y: 0 }
  );
  return { x: sum.x / count, y: sum.y / count };
}

export function repositionCoreGraph(cards: Card[], options: CoreGraphRepositionOptions): CoreGraphRepositionResult {
  const selectedIdSet = toSelectedIdSet(options.selectedIds);
  const selectedCards = cards.filter((card) => selectedIdSet.has(card.id));
  if (selectedCards.length === 0) {
    return { cards, usedMockAdapter: !options.adapter };
  }

  const adapter = options.adapter ?? mockCoreGraphAdapter();
  const nodes = selectedCards.map((card) => adapter.toNode(card));
  const anchor = computeAnchor(nodes, options.anchorMode ?? "centroid");

  const deltaX = options.targetX - anchor.x;
  const deltaY = options.targetY - anchor.y;

  let didChange = false;
  const selectedNodeMap = new Map(nodes.map((node) => [node.id, node]));
  const nextCards = cards.map((card) => {
    const node = selectedNodeMap.get(card.id);
    if (!node) {
      return card;
    }

    const nextX = snapIfNeeded(node.x + deltaX, options.snapToGridSize);
    const nextY = snapIfNeeded(node.y + deltaY, options.snapToGridSize);
    if (nextX === card.x && nextY === card.y) {
      return card;
    }

    didChange = true;
    return adapter.applyPosition(card, { x: nextX, y: nextY });
  });

  return {
    cards: didChange ? nextCards : cards,
    usedMockAdapter: !options.adapter,
  };
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
