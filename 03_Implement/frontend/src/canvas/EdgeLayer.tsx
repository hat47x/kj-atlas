import { memo, useMemo } from "react";
import type { MouseEvent } from "react";

import type { RenderEdge } from "../domain/edge_aggregate";
import type { Card, Island } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const ISLAND_PADDING = 24;

const WORLD_HALF_SIZE = 100000;
const WORLD_SIZE = WORLD_HALF_SIZE * 2;

type EdgeLayerProps = {
  cards: Card[];
  islands: Island[];
  edges: RenderEdge[];
  hiddenCardIds: Set<string>;
  selectedEdgeId?: string | null;
  onEdgeSelect?: (edgeId: string) => void;
};

type CenterPoint = {
  x: number;
  y: number;
};

function getCardCenter(card: Card): CenterPoint {
  return {
    x: card.x + CARD_WIDTH / 2,
    y: card.y + CARD_MIN_HEIGHT / 2,
  };
}

function getIslandCenter(island: Island, cardsById: Map<string, Card>): CenterPoint | null {
  const islandCards = island.cardIds
    .map((cardId) => cardsById.get(cardId))
    .filter((card): card is Card => card !== undefined);

  if (islandCards.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const card of islandCards) {
    minX = Math.min(minX, card.x);
    minY = Math.min(minY, card.y);
    maxX = Math.max(maxX, card.x + CARD_WIDTH);
    maxY = Math.max(maxY, card.y + CARD_MIN_HEIGHT);
  }

  const left = minX - ISLAND_PADDING;
  const top = minY - ISLAND_PADDING;
  const width = maxX - minX + ISLAND_PADDING * 2;
  const height = maxY - minY + ISLAND_PADDING * 2;

  return {
    x: left + width / 2,
    y: top + height / 2,
  };
}

function getDashArray(edge: RenderEdge): string | undefined {
  if (edge.isDerived) {
    return "4 4";
  }

  if (edge.type === "negate") {
    return "6 4";
  }

  return undefined;
}

function EdgeLayerComponent({
  cards,
  islands,
  edges,
  hiddenCardIds,
  selectedEdgeId,
  onEdgeSelect,
}: EdgeLayerProps) {
  const cardCenterById = useMemo(() => {
    const nextCardCenterById = new Map<string, CenterPoint>();

    for (const card of cards) {
      nextCardCenterById.set(card.id, getCardCenter(card));
    }

    return nextCardCenterById;
  }, [cards]);

  const islandCenterById = useMemo(() => {
    const cardsById = new Map(cards.map((card) => [card.id, card]));
    const nextIslandCenterById = new Map<string, CenterPoint>();

    for (const island of islands) {
      const center = getIslandCenter(island, cardsById);
      if (center) {
        nextIslandCenterById.set(island.id, center);
      }
    }

    return nextIslandCenterById;
  }, [cards, islands]);

  const drawableEdges = useMemo(() => {
    return edges.filter((edge) => {
      if (edge.fromKind === "card" && hiddenCardIds?.has(edge.fromId)) {
        return false;
      }

      if (edge.toKind === "card" && hiddenCardIds?.has(edge.toId)) {
        return false;
      }

      const fromCenter = edge.fromKind === "card" ? cardCenterById.get(edge.fromId) : islandCenterById.get(edge.fromId);
      const toCenter = edge.toKind === "card" ? cardCenterById.get(edge.toId) : islandCenterById.get(edge.toId);

      return fromCenter !== undefined && toCenter !== undefined;
    });
  }, [cardCenterById, edges, hiddenCardIds, islandCenterById]);

  return (
    <svg
      x={-WORLD_HALF_SIZE}
      y={-WORLD_HALF_SIZE}
      width={WORLD_SIZE}
      height={WORLD_SIZE}
      viewBox={`${-WORLD_HALF_SIZE} ${-WORLD_HALF_SIZE} ${WORLD_SIZE} ${WORLD_SIZE}`}
      preserveAspectRatio="none"
      shapeRendering="geometricPrecision"
      style={{
        position: "absolute",
        inset: 0,
        pointerEvents: "auto",
      }}
    >
      {drawableEdges.map((edge) => {
        const fromCenter = edge.fromKind === "card" ? cardCenterById.get(edge.fromId) : islandCenterById.get(edge.fromId);
        const toCenter = edge.toKind === "card" ? cardCenterById.get(edge.toId) : islandCenterById.get(edge.toId);

        if (!fromCenter || !toCenter) {
          return null;
        }

const isSelected = selectedEdgeId === edge.id;

const handleEdgeClick = (event: MouseEvent<SVGLineElement>) => {
  event.stopPropagation();
  onEdgeSelect?.(edge.id);
};

const midX = (fromCenter.x + toCenter.x) / 2;
const midY = (fromCenter.y + toCenter.y) / 2;

// ベースの線色（main準拠）
const baseStroke = edge.isDerived ? "#0f766e" : "#64748b";
const selectedStroke = "#2563eb";

return (
  <g key={edge.id}>
    {/* 見た目の線 */}
    <line
      x1={fromCenter.x}
      y1={fromCenter.y}
      x2={toCenter.x}
      y2={toCenter.y}
      stroke={isSelected ? selectedStroke : baseStroke}
      strokeWidth={isSelected ? 3 : edge.isDerived ? 2.5 : 2}
      vectorEffect="non-scaling-stroke"
      strokeLinecap="round"
      strokeDasharray={getDashArray(edge)}
      pointerEvents="none"
    />

    {/* クリック/選択用のヒット領域（透明・太め） */}
    <line
      x1={fromCenter.x}
      y1={fromCenter.y}
      x2={toCenter.x}
      y2={toCenter.y}
      stroke="transparent"
      strokeWidth={10}
      vectorEffect="non-scaling-stroke"
      strokeLinecap="round"
      pointerEvents="stroke"
      onPointerDown={(event) => {
        event.stopPropagation();
      }}
      onClick={handleEdgeClick}
    />

    {edge.isDerived && (edge.aggregateCount ?? 0) > 1 ? (
      <text
        x={midX}
        y={midY - 4}
        fontSize={11}
        fill="#115e59"
        textAnchor="middle"
        vectorEffect="non-scaling-stroke"
      >
        ×{edge.aggregateCount}
      </text>
    ) : null}
  </g>
);

export const EdgeLayer = memo(EdgeLayerComponent);
