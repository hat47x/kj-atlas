import { useEffect, useRef, useState } from "react";
import type { PointerEvent, ReactNode, WheelEvent } from "react";

import type { DocumentV2, Transform } from "../domain/types";
import { applyPan, applyZoomAtScreenPoint } from "./transform";
import { CardView } from "./CardView";
import { EdgeLayer } from "./EdgeLayer";
import { Marquee } from "./Marquee";

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 4;
const ZOOM_SENSITIVITY = 0.0015;

type DragState = {
  pointerId: number;
  lastClientX: number;
  lastClientY: number;
  startScreenX: number;
  startScreenY: number;
  didMove: boolean;
  mode: "pan" | "marquee";
};

type CanvasShellProps = {
  document: DocumentV2;
  onCardMove: (cardId: string, deltaWorldX: number, deltaWorldY: number) => void;
  selectedCardIds: string[];
  onCardSelect: (cardId: string, isShiftPressed: boolean) => void;
  onCanvasBackgroundClick: () => void;
  onMarqueeSelect: (cardIds: string[], isShiftPressed: boolean) => void;
  onTransformChange?: (transform: Transform) => void;
  children?: ReactNode;
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function canStartDrag(event: PointerEvent<HTMLDivElement>): boolean {
  if (event.pointerType === "mouse") {
    return event.button === 0;
  }

  return true;
}

export function CanvasShell({
  document,
  onCardMove,
  selectedCardIds,
  onCardSelect,
  onCanvasBackgroundClick,
  onMarqueeSelect,
  onTransformChange,
  children,
}: CanvasShellProps) {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<DragState | null>(null);

  const [transform, setTransform] = useState<Transform>(document.transform);
  const [dragMode, setDragMode] = useState<"none" | "pan" | "marquee">("none");
  const [isSpacePressed, setIsSpacePressed] = useState(false);
  const [marqueeRect, setMarqueeRect] = useState<{
    x: number;
    y: number;
    width: number;
    height: number;
  } | null>(null);

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.code === "Space") {
        event.preventDefault();
        setIsSpacePressed(true);
      }
    };

    const handleKeyUp = (event: KeyboardEvent) => {
      if (event.code === "Space") {
        setIsSpacePressed(false);
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    window.addEventListener("keyup", handleKeyUp);

    return () => {
      window.removeEventListener("keydown", handleKeyDown);
      window.removeEventListener("keyup", handleKeyUp);
    };
  }, []);

  useEffect(() => {
    if (!onTransformChange) {
      return;
    }

    onTransformChange(transform);
  }, [onTransformChange, transform]);

  const clearDragState = (event: PointerEvent<HTMLDivElement>) => {
    dragRef.current = null;
    setDragMode("none");
    setMarqueeRect(null);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  };

  const handlePointerDown = (event: PointerEvent<HTMLDivElement>) => {
    if (!canStartDrag(event)) {
      return;
    }

    const viewport = viewportRef.current;
    if (!viewport) {
      return;
    }

    const rect = viewport.getBoundingClientRect();
    const startScreenX = event.clientX - rect.left;
    const startScreenY = event.clientY - rect.top;

    // Mode rule: hold Space to pan. Otherwise, dragging on empty canvas starts marquee selection.
    const mode = isSpacePressed ? "pan" : "marquee";

    dragRef.current = {
      pointerId: event.pointerId,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      startScreenX,
      startScreenY,
      didMove: false,
      mode,
    };
    setDragMode(mode);

    event.currentTarget.setPointerCapture(event.pointerId);
  };

  const handlePointerMove = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    const deltaX = event.clientX - drag.lastClientX;
    const deltaY = event.clientY - drag.lastClientY;

    if (deltaX === 0 && deltaY === 0) {
      return;
    }

    dragRef.current = {
      ...drag,
      lastClientX: event.clientX,
      lastClientY: event.clientY,
      didMove: true,
    };

    if (drag.mode === "marquee") {
      const viewport = viewportRef.current;
      if (!viewport) {
        return;
      }

      const rect = viewport.getBoundingClientRect();
      const currentScreenX = event.clientX - rect.left;
      const currentScreenY = event.clientY - rect.top;
      const left = Math.min(drag.startScreenX, currentScreenX);
      const top = Math.min(drag.startScreenY, currentScreenY);
      const width = Math.abs(currentScreenX - drag.startScreenX);
      const height = Math.abs(currentScreenY - drag.startScreenY);

      setMarqueeRect({
        x: left,
        y: top,
        width,
        height,
      });
      return;
    }

    setTransform((prev) => applyPan(prev, deltaX, deltaY));
  };

  const handlePointerUp = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    if (!drag.didMove) {
      onCanvasBackgroundClick();
    } else if (drag.mode === "marquee") {
      const viewport = viewportRef.current;
      if (!viewport) {
        clearDragState(event);
        return;
      }

      const viewportRect = viewport.getBoundingClientRect();
      const endScreenX = event.clientX - viewportRect.left;
      const endScreenY = event.clientY - viewportRect.top;
      const selectionRect = {
        x: Math.min(drag.startScreenX, endScreenX),
        y: Math.min(drag.startScreenY, endScreenY),
        width: Math.abs(endScreenX - drag.startScreenX),
        height: Math.abs(endScreenY - drag.startScreenY),
      };

      const worldRect = {
        x: (selectionRect.x - transform.panX) / transform.zoom,
        y: (selectionRect.y - transform.panY) / transform.zoom,
        width: selectionRect.width / transform.zoom,
        height: selectionRect.height / transform.zoom,
      };

      const intersects = (cardX: number, cardY: number) => {
        const cardWidth = 220;
        const cardHeight = 80;

        return (
          cardX < worldRect.x + worldRect.width &&
          cardX + cardWidth > worldRect.x &&
          cardY < worldRect.y + worldRect.height &&
          cardY + cardHeight > worldRect.y
        );
      };

      const selectedByMarquee = document.cards
        .filter((card) => intersects(card.x, card.y))
        .map((card) => card.id);

      onMarqueeSelect(selectedByMarquee, event.shiftKey);
    }

    clearDragState(event);
  };

  const handlePointerCancel = (event: PointerEvent<HTMLDivElement>) => {
    const drag = dragRef.current;
    if (!drag || drag.pointerId !== event.pointerId) {
      return;
    }

    clearDragState(event);
  };

  const handleWheel = (event: WheelEvent<HTMLDivElement>) => {
    event.preventDefault();

    const viewport = viewportRef.current;
    if (!viewport) {
      return;
    }

    const rect = viewport.getBoundingClientRect();
    const screenPoint = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top,
    };

    setTransform((prev) => {
      const factor = Math.exp(-event.deltaY * ZOOM_SENSITIVITY);
      const unclampedZoom = prev.zoom * factor;
      const nextZoom = clamp(unclampedZoom, MIN_ZOOM, MAX_ZOOM);
      const actualFactor = nextZoom / prev.zoom;

      if (actualFactor === 1) {
        return prev;
      }

      return applyZoomAtScreenPoint(prev, actualFactor, screenPoint);
    });
  };

  return (
    <div
      ref={viewportRef}
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerCancel}
      onWheel={handleWheel}
      style={{
        position: "relative",
        width: "100%",
        height: "100%",
        overflow: "hidden",
        touchAction: "none",
        backgroundColor: "#fbfbfb",
        backgroundImage:
          "linear-gradient(to right, rgba(30, 41, 59, 0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(30, 41, 59, 0.08) 1px, transparent 1px)",
        backgroundSize: "24px 24px",
        cursor: dragMode === "pan" ? "grabbing" : isSpacePressed ? "grab" : "default",
      }}
    >
      <div
        style={{
          position: "absolute",
          inset: 0,
          transform: `translate(${transform.panX}px, ${transform.panY}px) scale(${transform.zoom})`,
          transformOrigin: "0 0",
        }}
      >
        <EdgeLayer cards={document.cards} edges={document.edges} />
        {document.cards.map((card) => (
          <CardView
            key={card.id}
            card={card}
            zoom={transform.zoom}
            onMove={onCardMove}
            isSelected={selectedCardIds.includes(card.id)}
            onSelect={onCardSelect}
          />
        ))}
        {children}
      </div>
      {marqueeRect && dragMode === "marquee" ? <Marquee rect={marqueeRect} /> : null}
    </div>
  );
}
