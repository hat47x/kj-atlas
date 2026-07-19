import { useMemo, useRef, useState } from "react";

import type { PointerEvent } from "react";

import type { ReadingOrderDropPosition } from "../domain/reading_order_ops";

import type { Card, Island } from "../domain/types";
import { getIslandBounds, ISLAND_TITLE_MARGIN_LEFT, ISLAND_TITLE_MARGIN_TOP } from "./IslandView";

type ReadingOrderLayerProps = {
  cards: Card[];
  islands: Island[];
  readingOrder: string[];
  visibleCardIdSet: Set<string>;
  visibleIslandIdSet: Set<string>;
  onItemFocus: (entryId: string, kind: "card" | "island", worldPoint: { x: number; y: number }) => void;
  isEditMode?: boolean;
  onRemoveEntry?: (entryId: string) => void;
  onReorderEntry?: (entryId: string, targetEntryId: string, position: ReadingOrderDropPosition) => void;
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
const DRAG_ACTIVATION_DISTANCE = 4;
const DROP_NEAR_DISTANCE = 42;

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
  isEditMode = false,
  onRemoveEntry,
  onReorderEntry,
}: ReadingOrderLayerProps) {
  const [draggingEntryId, setDraggingEntryId] = useState<string | null>(null);
  const dragStartPointRef = useRef<{ x: number; y: number } | null>(null);
  const didDragRef = useRef(false);
  const suppressClickRef = useRef(false);

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
          data-reading-order-entry-id={marker.entryId}
          type="button"
          onPointerDown={(event) => {
            event.stopPropagation();
            if (!isEditMode) {
              return;
            }

            dragStartPointRef.current = { x: event.clientX, y: event.clientY };
            didDragRef.current = false;
            setDraggingEntryId(marker.entryId);
            event.currentTarget.setPointerCapture(event.pointerId);
          }}
          onPointerMove={(event: PointerEvent<HTMLButtonElement>) => {
            if (!isEditMode || draggingEntryId !== marker.entryId) {
              return;
            }

            const dragStart = dragStartPointRef.current;
            if (dragStart) {
              const dragDistance = Math.hypot(event.clientX - dragStart.x, event.clientY - dragStart.y);
              if (dragDistance >= DRAG_ACTIVATION_DISTANCE) {
                didDragRef.current = true;
              }
            }
            event.stopPropagation();
          }}
          onPointerUp={(event: PointerEvent<HTMLButtonElement>) => {
            if (!isEditMode || draggingEntryId !== marker.entryId) {
              return;
            }

            event.stopPropagation();

            if (event.currentTarget.hasPointerCapture(event.pointerId)) {
              event.currentTarget.releasePointerCapture(event.pointerId);
            }

            suppressClickRef.current = didDragRef.current;

            if (didDragRef.current) {
              const allBadgeElements = Array.from(
                document.querySelectorAll<HTMLElement>("[data-reading-order-entry-id]")
              ).filter((element) => element.dataset.readingOrderEntryId !== marker.entryId);

              let closestBadge: HTMLElement | null = null;
              let closestDistance = Number.POSITIVE_INFINITY;

              for (const candidate of allBadgeElements) {
                const rect = candidate.getBoundingClientRect();
                const centerX = rect.left + rect.width / 2;
                const centerY = rect.top + rect.height / 2;
                const distance = Math.hypot(event.clientX - centerX, event.clientY - centerY);

                if (distance < closestDistance) {
                  closestDistance = distance;
                  closestBadge = candidate;
                }
              }

              if (closestBadge && closestDistance <= DROP_NEAR_DISTANCE) {
                const targetEntryId = closestBadge.dataset.readingOrderEntryId;
                if (targetEntryId) {
                  const targetRect = closestBadge.getBoundingClientRect();
                  const position: ReadingOrderDropPosition =
                    event.clientX < targetRect.left + targetRect.width / 2 ? "before" : "after";
                  onReorderEntry?.(marker.entryId, targetEntryId, position);
                }
              }
            }

            dragStartPointRef.current = null;
            didDragRef.current = false;
            setDraggingEntryId(null);
          }}
          onPointerCancel={() => {
            dragStartPointRef.current = null;
            didDragRef.current = false;
            suppressClickRef.current = false;
            setDraggingEntryId(null);
          }}
          onClick={(event) => {
            event.stopPropagation();

            if (isEditMode && event.altKey) {
              suppressClickRef.current = false;
              onRemoveEntry?.(marker.entryId);
              return;
            }

            if (isEditMode && suppressClickRef.current) {
              suppressClickRef.current = false;
              return;
            }

            onItemFocus(marker.entryId, marker.kind, { x: marker.focusX, y: marker.focusY });
          }}
          onKeyDown={(event) => {
            if (isEditMode && (event.key === "Delete" || event.key === "Backspace")) {
              event.preventDefault();
              event.stopPropagation();
              onRemoveEntry?.(marker.entryId);
            }
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
            cursor: isEditMode ? "grab" : "pointer",
            boxShadow: "0 1px 2px rgba(15, 23, 42, 0.2)",
            opacity: draggingEntryId === marker.entryId ? 0.75 : 1,
          }}
          title={
            isEditMode
              ? `Drag to reorder. Alt+Click or Delete to remove item ${marker.index + 1}`
              : `Focus reading order item ${marker.index + 1}`
          }
          aria-label={
            isEditMode
              ? `Reading order item ${marker.index + 1}. Drag to reorder, or press Delete to remove`
              : `Focus reading order item ${marker.index + 1}`
          }
        >
          {marker.index + 1}
        </button>
      ))}
    </>
  );
}
