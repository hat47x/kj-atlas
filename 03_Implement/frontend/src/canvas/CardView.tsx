import { memo, useRef, useState } from "react";
import type { PointerEvent } from "react";

import type { Card } from "../domain/types";

type CardDragState = {
  pointerId: number;
  lastClientX: number;
  lastClientY: number;
  didMove: boolean;
};

type CardViewProps = {
  card: Card;
  isSelected: boolean;
  isDeemphasized?: boolean;
  searchQuery?: string;
  isSearchMatch?: boolean;
  isActiveSearchMatch?: boolean;
  onMove: (cardId: string, deltaScreenX: number, deltaScreenY: number) => void;
  onSelect: (cardId: string, isShiftPressed: boolean) => void;
  isPickingEdgeTarget?: boolean;
};

function canStartDrag(event: PointerEvent<HTMLDivElement>): boolean {
  if (event.pointerType === "mouse") {
    return event.button === 0;
  }

  return true;
}

function renderHighlightedText(text: string, searchQuery: string): JSX.Element {
  if (!searchQuery) {
    return <>{text}</>;
  }

  const query = searchQuery.toLowerCase();
  const lowerText = text.toLowerCase();
  const parts: JSX.Element[] = [];
  let cursor = 0;
  let key = 0;

  while (cursor < text.length) {
    const foundIndex = lowerText.indexOf(query, cursor);
    if (foundIndex < 0) {
      parts.push(<span key={key}>{text.slice(cursor)}</span>);
      break;
    }

    if (foundIndex > cursor) {
      parts.push(<span key={key}>{text.slice(cursor, foundIndex)}</span>);
      key += 1;
    }

    parts.push(
      <mark
        key={key}
        style={{
          backgroundColor: "#fde68a",
          color: "inherit",
          padding: 0,
        }}
      >
        {text.slice(foundIndex, foundIndex + searchQuery.length)}
      </mark>
    );
    key += 1;
    cursor = foundIndex + searchQuery.length;
  }

  return <>{parts}</>;
}

function CardViewComponent({
  card,
  isSelected,
  searchQuery = "",
  isSearchMatch = false,
  isActiveSearchMatch = false,
  onMove,
  onSelect,
  isPickingEdgeTarget = false,
  isDeemphasized = false,
}: CardViewProps) {
  const dragRef = useRef<CardDragState | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const hasCritique = typeof card.critique === "string" && card.critique.trim().length > 0;

  const clearDragState = (event: PointerEvent<HTMLDivElement>) => {
    dragRef.current = null;
    setIsDragging(false);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (isPickingEdgeTarget) {
      event.stopPropagation();
      onSelect(card.id, false);
      return;
    }

    if (!canStartDrag(event)) {
      return;
    }

    event.stopPropagation();

    dragRef.current = {
      pointerId: event.pointerId,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      didMove: false,
    };
    setIsDragging(true);

    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();

    const deltaScreenX = event.clientX - drag.lastClientX;
    const deltaScreenY = event.clientY - drag.lastClientY;

    if (deltaScreenX === 0 && deltaScreenY === 0) {
      return;
    }

    dragRef.current = {
      ...drag,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      didMove: true,
    };

    onMove(card.id, deltaScreenX, deltaScreenY);
  };

  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();

    if (!drag.didMove) {
      onSelect(card.id, event.shiftKey);
    }

    clearDragState(event);
  };

  const handlePointerCancel = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();
    clearDragState(event);
  };

  return (
    <div
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerCancel}
      style={{
        position: "absolute",
        left: card.x,
        top: card.y,
        width: 220,
        minHeight: 80,
        padding: 12,
        border: "1px solid #cbd5e1",
        outline: isActiveSearchMatch
          ? "3px solid #f59e0b"
          : isSelected
            ? "2px solid #2563eb"
            : isSearchMatch
              ? "2px solid #fcd34d"
              : "none",
        outlineOffset: 1,
        borderRadius: 8,
        backgroundColor: "#ffffff",
        opacity: isDeemphasized ? 0.55 : 1,
        boxShadow: isSelected
          ? "0 0 0 2px rgba(37, 99, 235, 0.2), 0 1px 2px rgba(15, 23, 42, 0.08)"
          : "0 1px 2px rgba(15, 23, 42, 0.08)",
        color: "#0f172a",
        lineHeight: 1.4,
        whiteSpace: "pre-wrap",
        cursor: isPickingEdgeTarget ? "crosshair" : isDragging ? "grabbing" : "grab",
      }}
    >
      {hasCritique ? (
        <span
          aria-label="Card has critique note"
          title="Card has critique note"
          style={{
            position: "absolute",
            top: 6,
            right: 6,
            width: 8,
            height: 8,
            borderRadius: "50%",
            backgroundColor: "#f59e0b",
          }}
        />
      ) : null}
      {renderHighlightedText(card.text, searchQuery)}
    </div>
  );
}

export const CardView = memo(CardViewComponent);
