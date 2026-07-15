import { getIslandPolygonPoints } from "./island_geometry";
import { getPolygonBoundingBox } from "./polygon_bbox";
import { getEdgesToRender } from "../edge_aggregate";
import { getDerivedIslandEdges } from "../island_edge_aggregate";
import { isSourceCard, type Card, type DocumentV1, type Island } from "../types";

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
const ISLAND_PADDING = 24;

export type BoundsRect = {
  x: number;
  y: number;
  w: number;
  h: number;
};

export type VisibleBoundsViewState = {
  visibleIslandIds: Set<string>;
  hiddenCardIds: Set<string>;
  hideSourceCards: boolean;
  summaryView: boolean;
  abstractMapView: boolean;
};

function getCardCenter(card: Card): { x: number; y: number } {
  return {
    x: card.x + CARD_WIDTH / 2,
    y: card.y + CARD_HEIGHT / 2,
  };
}

export function getCardWorldBounds(card: Card): BoundsRect {
  return {
    x: card.x,
    y: card.y,
    w: CARD_WIDTH,
    h: CARD_HEIGHT,
  };
}

export function getIslandWorldBounds(island: Island, cardsById: Map<string, Card>): BoundsRect | null {
  const polygonBounds = getPolygonBoundingBox(getIslandPolygonPoints(island));
  if (polygonBounds) {
    return polygonBounds;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const cardId of island.cardIds) {
    const card = cardsById.get(cardId);
    if (!card) {
      continue;
    }

    minX = Math.min(minX, card.x);
    minY = Math.min(minY, card.y);
    const bounds = getCardWorldBounds(card);
    maxX = Math.max(maxX, bounds.x + bounds.w);
    maxY = Math.max(maxY, bounds.y + bounds.h);
  }

  if (!Number.isFinite(minX)) {
    return null;
  }

  return {
    x: minX - ISLAND_PADDING,
    y: minY - ISLAND_PADDING,
    w: Math.max(1, maxX - minX + ISLAND_PADDING * 2),
    h: Math.max(1, maxY - minY + ISLAND_PADDING * 2),
  };
}


export function islandBounds(island: Island, cardsById: Map<string, Card>): BoundsRect | null {
  return getIslandWorldBounds(island, cardsById);
}

export function getIslandCenter(island: Island, cardsById: Map<string, Card>): { x: number; y: number } | null {
  const bounds = getIslandWorldBounds(island, cardsById);
  if (!bounds) {
    return null;
  }

  return {
    x: bounds.x + bounds.w / 2,
    y: bounds.y + bounds.h / 2,
  };
}

export function computeVisibleBounds(doc: DocumentV1, viewState: VisibleBoundsViewState): BoundsRect | null {
  const cardsById = new Map(doc.cards.map((card) => [card.id, card]));
  const islandById = new Map(doc.islands.map((island) => [island.id, island]));
  const visibleCards = doc.cards.filter((card) => {
    if (viewState.hiddenCardIds.has(card.id)) {
      return false;
    }
    if (viewState.hideSourceCards && isSourceCard(card)) {
      return false;
    }
    return true;
  });
  const visibleCardIdSet = new Set(visibleCards.map((card) => card.id));

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  const includeRect = (rect: BoundsRect) => {
    minX = Math.min(minX, rect.x);
    minY = Math.min(minY, rect.y);
    maxX = Math.max(maxX, rect.x + rect.w);
    maxY = Math.max(maxY, rect.y + rect.h);
  };

  const includePoint = (point: { x: number; y: number }) => {
    minX = Math.min(minX, point.x);
    minY = Math.min(minY, point.y);
    maxX = Math.max(maxX, point.x);
    maxY = Math.max(maxY, point.y);
  };

  for (const island of doc.islands) {
    if (!viewState.visibleIslandIds.has(island.id)) {
      continue;
    }

    const bounds = getIslandWorldBounds(island, cardsById);
    if (bounds) {
      includeRect(bounds);
    }
  }

  for (const card of visibleCards) {
    includeRect(getCardWorldBounds(card));
  }

  let edges = getEdgesToRender(doc, viewState.hideSourceCards).filter((edge) => {
    const isFromVisible = edge.fromKind === "island" ? viewState.visibleIslandIds.has(edge.fromId) : visibleCardIdSet.has(edge.fromId);
    const isToVisible = edge.toKind === "island" ? viewState.visibleIslandIds.has(edge.toId) : visibleCardIdSet.has(edge.toId);
    return isFromVisible && isToVisible;
  });

  if (viewState.summaryView || viewState.abstractMapView) {
    edges = [
      ...edges,
      ...getDerivedIslandEdges(doc).filter((edge) => {
        if (!viewState.visibleIslandIds.has(edge.fromId)) {
          return false;
        }
        return edge.toKind === "island" ? viewState.visibleIslandIds.has(edge.toId) : visibleCardIdSet.has(edge.toId);
      }),
    ];
  }

  for (const edge of edges) {
    const from = edge.fromKind === "card" ? cardsById.get(edge.fromId) : islandById.get(edge.fromId);
    const to = edge.toKind === "card" ? cardsById.get(edge.toId) : islandById.get(edge.toId);
    const fromPoint = edge.fromKind === "card" ? (from ? getCardCenter(from as Card) : null) : (from ? getIslandCenter(from as Island, cardsById) : null);
    const toPoint = edge.toKind === "card" ? (to ? getCardCenter(to as Card) : null) : (to ? getIslandCenter(to as Island, cardsById) : null);

    if (fromPoint) {
      includePoint(fromPoint);
    }
    if (toPoint) {
      includePoint(toPoint);
    }
  }

  if (!Number.isFinite(minX) || !Number.isFinite(minY) || !Number.isFinite(maxX) || !Number.isFinite(maxY)) {
    return null;
  }

  return {
    x: minX,
    y: minY,
    w: Math.max(1, maxX - minX),
    h: Math.max(1, maxY - minY),
  };
}
