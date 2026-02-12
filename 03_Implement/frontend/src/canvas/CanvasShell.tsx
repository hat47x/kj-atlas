import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent, ReactNode, WheelEvent } from "react";

import type { DocumentV2, Transform } from "../domain/types";
import { applyPan, applyZoomAtScreenPoint } from "./transform";
import { CardView } from "./CardView";
import { EdgeLayer } from "./EdgeLayer";
import { Marquee } from "./Marquee";
import { SuggestionDiffLayer } from "./SuggestionDiffLayer";
import type { SuggestionMoveDiff } from "./SuggestionDiffLayer";

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 4;
const ZOOM_SENSITIVITY = 0.0015;
const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;

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
  hiddenCardIds?: Set<string>;
  searchQuery?: string;
  matchedCardIds?: Set<string>;
  activeMatchedCardId?: string | null;
  focusCardId?: string | null;
  focusWorldPoint?: { x: number; y: number } | null;
  focusRequestSeq?: number;
  isPickingEdgeTarget?: boolean;
  suggestionMoveDiffs?: SuggestionMoveDiff[];
  children?: ReactNode;
};

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

export function focusTransformAtWorldPoint(
  currentTransform: Transform,
  worldPoint: { x: number; y: number },
  viewportWidth: number,
  viewportHeight: number
): Transform {
  return {
    ...currentTransform,
    panX: viewportWidth / 2 - worldPoint.x * currentTransform.zoom,
    panY: viewportHeight / 2 - worldPoint.y * currentTransform.zoom,
  };
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
  hiddenCardIds,
  searchQuery = "",
  matchedCardIds,
  activeMatchedCardId,
  focusCardId,
  focusWorldPoint,
  focusRequestSeq = 0,
  isPickingEdgeTarget = false,
  suggestionMoveDiffs,
  children,
}: CanvasShellProps) {
  const viewportRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<DragState | null>(null);

  const [transform, setTransform] = useState<Transform>(document.transform);
  const transformRef = useRef<Transform>(document.transform);
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
    setTransform(document.transform);
  }, [document.transform]);

  useEffect(() => {
    transformRef.current = transform;
  }, [transform]);

  useEffect(() => {
    if (!onTransformChange) {
      return;
    }

    onTransformChange(transform);
  }, [onTransformChange, transform]);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) {
      return;
    }

    if (focusWorldPoint) {
      setTransform((previousTransform) =>
        focusTransformAtWorldPoint(previousTransform, focusWorldPoint, viewport.clientWidth, viewport.clientHeight)
      );
      return;
    }

    if (!focusCardId) {
      return;
    }

    const targetCard = document.cards.find((card) => card.id === focusCardId);
    if (!targetCard) {
      return;
    }

    setTransform((previousTransform) =>
      focusTransformAtWorldPoint(
        previousTransform,
        {
          x: targetCard.x + CARD_WIDTH / 2,
          y: targetCard.y + CARD_HEIGHT / 2,
        },
        viewport.clientWidth,
        viewport.clientHeight
      )
    );
  }, [document.cards, focusCardId, focusRequestSeq, focusWorldPoint]);

  const selectedCardIdSet = useMemo(() => new Set(selectedCardIds), [selectedCardIds]);
  const hiddenCardIdSet = hiddenCardIds ?? new Set<string>();
  const visibleCards = useMemo(() => {
    if (hiddenCardIdSet.size === 0) {
      return document.cards;
    }

    return document.cards.filter((card) => !hiddenCardIdSet.has(card.id));
  }, [document.cards, hiddenCardIdSet]);
  const visibleEdges = useMemo(() => {
    if (hiddenCardIdSet.size === 0) {
      return document.edges;
    }

    return document.edges.filter((edge) => !hiddenCardIdSet.has(edge.fromId) && !hiddenCardIdSet.has(edge.toId));
  }, [document.edges, hiddenCardIdSet]);

  const visibleSuggestionMoveDiffs = useMemo(() => {
    const diffs = suggestionMoveDiffs ?? [];
    if (hiddenCardIdSet.size === 0) {
      return diffs;
    }

    return diffs.filter((diff) => !hiddenCardIdSet.has(diff.cardId));
  }, [hiddenCardIdSet, suggestionMoveDiffs]);

  const clearDragState = useCallback((event: PointerEvent<HTMLDivElement>) => {
    dragRef.current = null;
    setDragMode("none");
    setMarqueeRect(null);

    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId);
    }
  }, []);

  const handleCardMove = useCallback(
    (cardId: string, deltaScreenX: number, deltaScreenY: number) => {
      const currentZoom = transformRef.current.zoom;
      onCardMove(cardId, deltaScreenX / currentZoom, deltaScreenY / currentZoom);
    },
    [onCardMove]
  );

  const handleCardSelect = useCallback(
    (cardId: string, isShiftPressed: boolean) => {
      onCardSelect(cardId, isShiftPressed);
    },
    [onCardSelect]
  );

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
        return (
          cardX < worldRect.x + worldRect.width &&
          cardX + CARD_WIDTH > worldRect.x &&
          cardY < worldRect.y + worldRect.height &&
          cardY + CARD_HEIGHT > worldRect.y
        );
      };

      const selectedByMarquee = visibleCards
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
        <EdgeLayer cards={visibleCards} edges={visibleEdges} />
        <SuggestionDiffLayer diffs={visibleSuggestionMoveDiffs} cardWidth={CARD_WIDTH} cardHeight={CARD_HEIGHT} />
        {children}
        {visibleCards.map((card) => {
          return (
            <CardView
              key={card.id}
              card={card}
              onMove={handleCardMove}
              isSelected={selectedCardIdSet.has(card.id)}
              onSelect={handleCardSelect}
              searchQuery={searchQuery}
              isSearchMatch={matchedCardIds?.has(card.id) ?? false}
              isActiveSearchMatch={activeMatchedCardId === card.id}
              isPickingEdgeTarget={isPickingEdgeTarget}
            />
          );
        })}
      </div>
      {marqueeRect && dragMode === "marquee" ? <Marquee rect={marqueeRect} /> : null}
    </div>
  );
}
