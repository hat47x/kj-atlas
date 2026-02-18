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
  compactMode?: boolean;
  markerMode?: boolean;
  showLabelText?: boolean;
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
  compactMode = false,
  markerMode = false,
  showLabelText = true,
}: CardViewProps) {
  const dragRef = useRef<CardDragState | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const hasCritique = typeof card.critique === "string" && card.critique.trim().length > 0;
  const representativeCount = card.repOf?.length ?? 0;
  const compactText = card.text.trim().split(/\n+/).join(" ").slice(0, 72);

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
        width: markerMode ? 10 : 220,
        minHeight: markerMode ? 10 : compactMode ? 52 : 80,
        padding: markerMode ? 0 : compactMode ? "8px 10px" : 12,
        border: markerMode ? "1px solid #64748b" : "1px solid #cbd5e1",
        outline: isActiveSearchMatch
          ? "3px solid #f59e0b"
          : isSelected
            ? "2px solid #2563eb"
            : isSearchMatch
              ? "2px solid #fcd34d"
              : "none",
        outlineOffset: 1,
        borderRadius: markerMode ? 999 : 8,
        backgroundColor: markerMode ? "rgba(100, 116, 139, 0.25)" : "#ffffff",
        opacity: markerMode ? 0.4 : isDeemphasized ? 0.55 : 1,
        boxShadow: isSelected
          ? "0 0 0 2px rgba(37, 99, 235, 0.2), 0 1px 2px rgba(15, 23, 42, 0.08)"
          : "0 1px 2px rgba(15, 23, 42, 0.08)",
        color: "#0f172a",
        lineHeight: compactMode ? 1.25 : 1.4,
        whiteSpace: compactMode ? "normal" : "pre-wrap",
        fontSize: compactMode ? 12 : 14,
        cursor: isPickingEdgeTarget ? "crosshair" : isDragging ? "grabbing" : "grab",
      }}
      title={compactMode ? card.text : undefined}
    >
      {!markerMode && representativeCount > 0 ? (
        <span
          style={{
            position: "absolute",
            top: 6,
            left: 6,
            borderRadius: 999,
            backgroundColor: "#dbeafe",
            color: "#1d4ed8",
            fontSize: 11,
            fontWeight: 700,
            padding: "2px 8px",
          }}
        >
          Rep ({representativeCount})
        </span>
      ) : null}
      {!markerMode && hasCritique ? (
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
      {!markerMode && showLabelText
        ? compactMode
          ? renderHighlightedText(compactText, searchQuery)
          : renderHighlightedText(card.text, searchQuery)
        : null}
    </div>
  );
}

export const CardView = memo(CardViewComponent);
