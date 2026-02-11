import { useRef, useState } from "react";
import type { PointerEvent } from "react";

import type { Card } from "../domain/types";

type CardDragState = {
  pointerId: number;
  lastClientX: number;
  lastClientY: number;
};

type CardViewProps = {
  card: Card;
  zoom: number;
  onMove: (cardId: string, deltaWorldX: number, deltaWorldY: number) => void;
};

function canStartDrag(event: PointerEvent<HTMLDivElement>): boolean {
  if (event.pointerType === "mouse") {
    return event.button === 0;
  }

  return true;
}

export function CardView({ card, zoom, onMove }: CardViewProps) {
  const dragRef = useRef<CardDragState | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (!canStartDrag(event)) {
      return;
    }

    event.stopPropagation();

    dragRef.current = {
      pointerId: event.pointerId,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
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
    };

    onMove(card.id, deltaScreenX / zoom, deltaScreenY / zoom);
  };

  const endDrag = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    event.stopPropagation();

    dragRef.current = null;
    setIsDragging(false);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  return (
    <div
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={endDrag}
      onPointerCancel={endDrag}
      style={{
        position: "absolute",
        left: card.x,
        top: card.y,
        width: 220,
        minHeight: 80,
        padding: 12,
        border: "1px solid #cbd5e1",
        borderRadius: 8,
        backgroundColor: "#ffffff",
        boxShadow: "0 1px 2px rgba(15, 23, 42, 0.08)",
        color: "#0f172a",
        lineHeight: 1.4,
        whiteSpace: "pre-wrap",
        cursor: isDragging ? "grabbing" : "grab",
      }}
    >
      {card.text}
    </div>
  );
}
