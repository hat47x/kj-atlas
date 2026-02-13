import { memo, useMemo } from "react";
import type { MouseEvent } from "react";

import type { Card, EdgeType } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;

const WORLD_HALF_SIZE = 100000;
const WORLD_SIZE = WORLD_HALF_SIZE * 2;

type EdgeLayerProps = {
  cards: Card[];
  edges: Array<{
    id: string;
    fromId: string;
    toId: string;
    type: EdgeType;
  }>;
  hiddenCardIds?: Set<string>;
  selectedEdgeId?: string | null;
  onEdgeSelect?: (edgeId: string) => void;
};

type CardCenter = {
  x: number;
  y: number;
};

function getCardCenter(card: Card): CardCenter {
  return {
    x: card.x + CARD_WIDTH / 2,
    y: card.y + CARD_MIN_HEIGHT / 2,
  };
}

function EdgeLayerComponent({ cards, edges, hiddenCardIds, selectedEdgeId, onEdgeSelect }: EdgeLayerProps) {
  const cardCenterById = useMemo(() => {
    const nextCardCenterById = new Map<string, CardCenter>();

    for (const card of cards) {
      nextCardCenterById.set(card.id, getCardCenter(card));
    }

    return nextCardCenterById;
  }, [cards]);

  const drawableEdges = useMemo(() => {
    return edges.filter((edge) => {
      if (hiddenCardIds?.has(edge.fromId) || hiddenCardIds?.has(edge.toId)) {
        return false;
      }

      return cardCenterById.has(edge.fromId) && cardCenterById.has(edge.toId);
    });
  }, [cardCenterById, edges, hiddenCardIds]);

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
        const fromCenter = cardCenterById.get(edge.fromId);
        const toCenter = cardCenterById.get(edge.toId);

        if (!fromCenter || !toCenter) {
          return null;
        }

        const isSelected = selectedEdgeId === edge.id;

        const handleEdgeClick = (event: MouseEvent<SVGLineElement>) => {
          event.stopPropagation();
          onEdgeSelect?.(edge.id);
        };

        return (
          <line
            key={edge.id}
            x1={fromCenter.x}
            y1={fromCenter.y}
            x2={toCenter.x}
            y2={toCenter.y}
            stroke={isSelected ? "#2563eb" : "#64748b"}
            strokeWidth={isSelected ? 3 : 2}
            vectorEffect="non-scaling-stroke"
            strokeLinecap="round"
            strokeDasharray={edge.type === "negate" ? "6 4" : undefined}
            pointerEvents="stroke"
            onPointerDown={(event) => {
              event.stopPropagation();
            }}
            onClick={handleEdgeClick}
          />
        );
      })}
    </svg>
  );
}

export const EdgeLayer = memo(EdgeLayerComponent);
