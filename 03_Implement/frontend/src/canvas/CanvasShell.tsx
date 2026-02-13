import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent, ReactNode, WheelEvent } from "react";

import { getEdgesToRender } from "../domain/edge_aggregate";
import { isCanonicalCard, isSourceCard, type DocumentV2, type EdgeType, type Transform } from "../domain/types";
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

type RenderEdge = {
  id: string;
  fromId: string;
  toId: string;
  type: EdgeType;
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
  hideSourceCards?: boolean;
  /** @deprecated Use revealCardIds. */
  peekCardIds?: Set<string>;
  revealCardIds?: Set<string>;
  showCanonicalOnlyEdges?: boolean;
  searchQuery?: string;
  matchedCardIds?: Set<string>;
  activeMatchedCardId?: string | null;
  focusCardId?: string | null;
  focusWorldPoint?: { x: number; y: number } | null;
  focusRequestSeq?: number;
  isPickingEdgeTarget?: boolean;
  suggestionMoveDiffs?: SuggestionMoveDiff[];
  selectedEdgeId?: string | null;
  onEdgeSelect?: (edgeId: string) => void;
  onAggregatedEdgesChange?: (edges: AggregatedEdgeMeta[]) => void;
  children?: ReactNode;
};

export type AggregatedEdgeSource = {
  sourceFromCardId: string;
  sourceToId: string;
  sourceToKind: "card" | "island";
};

export type AggregatedEdgeMeta = {
  id: string;
  fromId: string;
  toId: string;
  fromKind: "canonical" | "island";
  toKind: "canonical" | "island";
  type: EdgeType;
  sources: AggregatedEdgeSource[];
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
  hideSourceCards = true,
  peekCardIds,
  revealCardIds,
  showCanonicalOnlyEdges = false,
  searchQuery = "",
  matchedCardIds,
  activeMatchedCardId,
  focusCardId,
  focusWorldPoint,
  focusRequestSeq = 0,
  isPickingEdgeTarget = false,
  suggestionMoveDiffs,
  selectedEdgeId,
  onEdgeSelect,
  onAggregatedEdgesChange,
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
  const emptyIdSet = useMemo(() => new Set<string>(), []);

  const sourceCardIdSet = useMemo(() => {
    if (!hideSourceCards) {
      return emptyIdSet;
    }
    return new Set(
      document.cards
        .filter((card) => isSourceCard(card))
        .map((card) => card.id)
    );
  }, [document.cards, hideSourceCards, emptyIdSet]);
  const revealedCardIdSet = revealCardIds ?? peekCardIds ?? emptyIdSet;

  const hiddenCardIdSet = hiddenCardIds ?? emptyIdSet;
  const isCardHidden = useCallback(
    (cardId: string) => hiddenCardIdSet.has(cardId) || (sourceCardIdSet.has(cardId) && !revealedCardIdSet.has(cardId)),
    [hiddenCardIdSet, sourceCardIdSet, revealedCardIdSet]
  );

  const hiddenEndpointIdSet = useMemo(() => {
    const hiddenSourceCardIds = Array.from(sourceCardIdSet).filter((cardId) => !revealedCardIdSet.has(cardId));
    return new Set([...hiddenCardIdSet, ...hiddenSourceCardIds]);
  }, [hiddenCardIdSet, sourceCardIdSet, revealedCardIdSet]);

  const visibleCards = useMemo(() => {
    return document.cards.filter((card) => !isCardHidden(card.id));
  }, [document.cards, isCardHidden]);
  const visibleCardIdSet = useMemo(() => new Set(visibleCards.map((card) => card.id)), [visibleCards]);
  const canonicalCardIdSet = useMemo(
    () => new Set(document.cards.filter((card) => isCanonicalCard(card)).map((card) => card.id)),
    [document.cards]
  );

  const aggregatedEdges = useMemo(() => {
    const cardsById = new Map(document.cards.map((card) => [card.id, card]));
    const grouped = new Map<string, AggregatedEdgeMeta>();

    for (const edge of document.edges) {
      const edgeWithKinds = edge as typeof edge & { fromKind?: "card" | "island"; toKind?: "card" | "island" };
      const sourceFromKind = edgeWithKinds.fromKind ?? "card";
      const sourceToKind = edgeWithKinds.toKind ?? "card";

      const fromCard = sourceFromKind === "card" ? cardsById.get(edge.fromId) : undefined;
      const toCard = sourceToKind === "card" ? cardsById.get(edge.toId) : undefined;
      const resolvedFromId = sourceFromKind === "card" ? fromCard?.canonicalId ?? edge.fromId : edge.fromId;
      const resolvedToId = sourceToKind === "card" ? toCard?.canonicalId ?? edge.toId : edge.toId;
      const resolvedFromKind = sourceFromKind === "island" ? "island" : "canonical";
      const resolvedToKind = sourceToKind === "island" ? "island" : "canonical";

      if (resolvedFromId === resolvedToId && resolvedFromKind === resolvedToKind) {
        continue;
      }

      const key = `${resolvedFromKind}:${resolvedFromId}->${resolvedToKind}:${resolvedToId}:${edge.type}`;
      const current = grouped.get(key);
      const nextSource: AggregatedEdgeSource = {
        sourceFromCardId: edge.fromId,
        sourceToId: edge.toId,
        sourceToKind: sourceToKind,
      };

      if (current) {
        current.sources.push(nextSource);
        continue;
      }

      grouped.set(key, {
        id: key,
        fromId: resolvedFromId,
        toId: resolvedToId,
        fromKind: resolvedFromKind,
        toKind: resolvedToKind,
        type: edge.type,
        sources: [nextSource],
      });
    }

    return Array.from(grouped.values());
  }, [document.cards, document.edges]);

  const visibleEdges = useMemo(() => {
    let edges = getEdgesToRender(document, hideSourceCards === true).filter((edge) => {
      const isFromVisible = edge.fromKind === "island" || visibleCardIdSet.has(edge.fromId);
      const isToVisible = edge.toKind === "island" || visibleCardIdSet.has(edge.toId);
      return isFromVisible && isToVisible;
    });

    if (showCanonicalOnlyEdges) {
      edges = edges.filter((edge) => {
        return (
          edge.fromKind === "card" &&
          edge.toKind === "card" &&
          canonicalCardIdSet.has(edge.fromId) &&
          canonicalCardIdSet.has(edge.toId)
        );
      });
    }

    return edges;
  }, [canonicalCardIdSet, document, hideSourceCards, showCanonicalOnlyEdges, visibleCardIdSet]);

  useEffect(() => {
    onAggregatedEdgesChange?.(aggregatedEdges);
  }, [aggregatedEdges, onAggregatedEdgesChange]);
  const visibleSuggestionMoveDiffs = useMemo(() => {
    const diffs = suggestionMoveDiffs ?? [];
    return diffs.filter((diff) => !isCardHidden(diff.cardId));
  }, [isCardHidden, suggestionMoveDiffs]);
  
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
        <EdgeLayer
          cards={visibleCards}
          islands={document.islands}
          edges={visibleEdges}
          hiddenCardIds={hiddenEndpointIdSet}
        />
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
