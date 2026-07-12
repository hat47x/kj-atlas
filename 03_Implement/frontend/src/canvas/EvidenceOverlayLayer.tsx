import { useMemo } from "react";

import type { Card, EvidenceLink } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const WORLD_HALF_SIZE = 100000;
const WORLD_SIZE = WORLD_HALF_SIZE * 2;

type EvidenceOverlayLayerProps = {
  cards: Card[];
  edges: EvidenceLink[];
};

function getCardCenter(card: Card): { x: number; y: number } {
  return {
    x: card.x + CARD_WIDTH / 2,
    y: card.y + CARD_MIN_HEIGHT / 2,
  };
}

export function EvidenceOverlayLayer({ cards, edges }: EvidenceOverlayLayerProps) {
  const cardCenterById = useMemo(() => {
    const map = new Map<string, { x: number; y: number }>();
    for (const card of cards) {
      map.set(card.id, getCardCenter(card));
    }
    return map;
  }, [cards]);

  const drawableEdges = useMemo(() => {
    return [...edges]
      .sort((left, right) => left.id.localeCompare(right.id))
      .filter((edge) => cardCenterById.has(edge.fromCardId) && cardCenterById.has(edge.toCardId));
  }, [cardCenterById, edges]);

  return (
    // Same world-window pattern as EdgeLayer: x/y ATTRIBUTES on an
    // HTML-embedded root <svg> are ignored, so with `inset: 0` the viewBox
    // mapped world coordinates into the container box and every evidence
    // line painted compressed/off screen (lines existed in the DOM but were
    // never visible -- found 2026-07-12 via the P32 teal/sky live check).
    // The world window must be positioned via CSS left/top instead.
    <svg
      width={WORLD_SIZE}
      height={WORLD_SIZE}
      viewBox={`${-WORLD_HALF_SIZE} ${-WORLD_HALF_SIZE} ${WORLD_SIZE} ${WORLD_SIZE}`}
      preserveAspectRatio="none"
      shapeRendering="geometricPrecision"
      style={{
        position: "absolute",
        left: -WORLD_HALF_SIZE,
        top: -WORLD_HALF_SIZE,
        width: WORLD_SIZE,
        height: WORLD_SIZE,
        pointerEvents: "none",
        zIndex: 3,
      }}
      aria-hidden="true"
    >
      {drawableEdges.map((edge) => {
        const from = cardCenterById.get(edge.fromCardId);
        const to = cardCenterById.get(edge.toCardId);
        if (!from || !to) {
          return null;
        }

        const isContradict = edge.type === "contradicts";

        return (
          <line
            key={edge.id}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={isContradict ? "#b91c1c" : "#0369a1"}
            strokeWidth={2}
            vectorEffect="non-scaling-stroke"
            strokeLinecap="round"
            strokeDasharray={isContradict ? "7 5" : undefined}
            opacity={0.9}
          />
        );
      })}
    </svg>
  );
}
