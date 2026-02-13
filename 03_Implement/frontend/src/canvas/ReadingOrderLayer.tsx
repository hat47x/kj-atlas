import { useMemo } from "react";

import type { Card, Island } from "../domain/types";
import { getIslandBounds, ISLAND_TITLE_MARGIN_LEFT, ISLAND_TITLE_MARGIN_TOP } from "./IslandView";

type ReadingOrderLayerProps = {
  cards: Card[];
  islands: Island[];
  readingOrder: string[];
  visibleCardIdSet: Set<string>;
  visibleIslandIdSet: Set<string>;
  onItemFocus: (entryId: string, kind: "card" | "island", worldPoint: { x: number; y: number }) => void;
};

export type ReadingOrderMarker = {
  entryId: string;
  index: number;
  kind: "card" | "island";
  badgeX: number;
  badgeY: number;
  focusX: number;
  focusY: number;
};

const CARD_BADGE_OFFSET_X = 8;
const CARD_BADGE_OFFSET_Y = 8;
const BADGE_SIZE = 24;

export function buildReadingOrderMarkers(
  cards: Card[],
  islands: Island[],
  readingOrder: string[],
  visibleCardIdSet: Set<string>,
  visibleIslandIdSet: Set<string>
): ReadingOrderMarker[] {
  const cardsById = new Map(cards.map((card) => [card.id, card]));
  const islandsById = new Map(islands.map((island) => [island.id, island]));

  const items: ReadingOrderMarker[] = [];

  for (let i = 0; i < readingOrder.length; i += 1) {
    const entryId = readingOrder[i];
    const card = cardsById.get(entryId);

    if (card && visibleCardIdSet.has(entryId)) {
      items.push({
        entryId,
        index: i,
        kind: "card",
        badgeX: card.x + CARD_BADGE_OFFSET_X,
        badgeY: card.y + CARD_BADGE_OFFSET_Y,
        focusX: card.x + 110,
        focusY: card.y + 40,
      });
      continue;
    }

    const island = islandsById.get(entryId);
    if (!island || !visibleIslandIdSet.has(entryId)) {
      continue;
    }

    const islandBounds = getIslandBounds(island, cards);
    if (!islandBounds) {
      continue;
    }

    items.push({
      entryId,
      index: i,
      kind: "island",
      badgeX: islandBounds.left + ISLAND_TITLE_MARGIN_LEFT,
      badgeY: islandBounds.top + ISLAND_TITLE_MARGIN_TOP,
      focusX: islandBounds.left + islandBounds.width / 2,
      focusY: islandBounds.top + islandBounds.height / 2,
    });
  }

  return items;
}

export function ReadingOrderLayer({
  cards,
  islands,
  readingOrder,
  visibleCardIdSet,
  visibleIslandIdSet,
  onItemFocus,
}: ReadingOrderLayerProps) {
  const markers = useMemo(
    () => buildReadingOrderMarkers(cards, islands, readingOrder, visibleCardIdSet, visibleIslandIdSet),
    [cards, islands, readingOrder, visibleCardIdSet, visibleIslandIdSet]
  );

  if (markers.length === 0) {
    return null;
  }

  return (
    <>
      <svg
        width="100%"
        height="100%"
        style={{
          position: "absolute",
          inset: 0,
          pointerEvents: "none",
          overflow: "visible",
          zIndex: 30,
        }}
      >
        <defs>
          <marker id="reading-order-arrowhead" markerWidth="8" markerHeight="6" refX="7" refY="3" orient="auto">
            <path d="M 0 0 L 8 3 L 0 6 Z" fill="#6366f1" />
          </marker>
        </defs>
        {markers.slice(0, -1).map((marker, index) => {
          const next = markers[index + 1];
          return (
            <line
              key={`${marker.entryId}->${next.entryId}-${index}`}
              x1={marker.badgeX + BADGE_SIZE / 2}
              y1={marker.badgeY + BADGE_SIZE / 2}
              x2={next.badgeX + BADGE_SIZE / 2}
              y2={next.badgeY + BADGE_SIZE / 2}
              stroke="#6366f1"
              strokeWidth={1.5}
              markerEnd="url(#reading-order-arrowhead)"
              opacity={0.75}
            />
          );
        })}
      </svg>
      {markers.map((marker) => (
        <button
          key={`${marker.entryId}-${marker.index}`}
          type="button"
          onPointerDown={(event) => {
            event.stopPropagation();
          }}
          onClick={(event) => {
            event.stopPropagation();
            onItemFocus(marker.entryId, marker.kind, { x: marker.focusX, y: marker.focusY });
          }}
          style={{
            position: "absolute",
            left: marker.badgeX,
            top: marker.badgeY,
            width: BADGE_SIZE,
            height: BADGE_SIZE,
            borderRadius: "50%",
            border: "1px solid #4f46e5",
            backgroundColor: "#eef2ff",
            color: "#312e81",
            fontSize: 12,
            fontWeight: 700,
            lineHeight: 1,
            zIndex: 31,
            cursor: "pointer",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.2)",
          }}
          title={`Focus reading order item ${marker.index + 1}`}
          aria-label={`Focus reading order item ${marker.index + 1}`}
        >
          {marker.index + 1}
        </button>
      ))}
    </>
  );
}
