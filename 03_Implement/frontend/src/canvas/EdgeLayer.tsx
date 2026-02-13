import { memo, useMemo } from "react";

import type { Card, Edge } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;

const WORLD_HALF_SIZE = 100000;
const WORLD_SIZE = WORLD_HALF_SIZE * 2;

type EdgeLayerProps = {
  cards: Card[];
  edges: Edge[];
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

function EdgeLayerComponent({ cards, edges }: EdgeLayerProps) {
  const cardCenterById = useMemo(() => {
    const nextCardCenterById = new Map<string, CardCenter>();

    for (const card of cards) {
      nextCardCenterById.set(card.id, getCardCenter(card));
    }

    return nextCardCenterById;
  }, [cards]);

  const drawableEdges = useMemo(() => {
    return edges.filter((edge) => cardCenterById.has(edge.fromId) && cardCenterById.has(edge.toId));
  }, [cardCenterById, edges]);

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
        pointerEvents: "none",
      }}
    >
      {drawableEdges.map((edge) => {
        const fromCenter = cardCenterById.get(edge.fromId);
        const toCenter = cardCenterById.get(edge.toId);

        if (!fromCenter || !toCenter) {
          return null;
        }

        return (
          <line
            key={edge.id}
            x1={fromCenter.x}
            y1={fromCenter.y}
            x2={toCenter.x}
            y2={toCenter.y}
            stroke="#64748b"
            strokeWidth={2}
            vectorEffect="non-scaling-stroke"
            strokeLinecap="round"
            strokeDasharray={edge.type === "negate" ? "6 4" : undefined}
          />
        );
      })}
    </svg>
  );
}

export const EdgeLayer = memo(EdgeLayerComponent);
