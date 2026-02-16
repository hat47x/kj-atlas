import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent, ReactNode, WheelEvent } from "react";

import { getEdgesToRender } from "../domain/edge_aggregate";
import { getDerivedIslandEdges } from "../domain/island_edge_aggregate";
import {
  isCanonicalCard,
  isSourceCard,
  type DocumentV2,
  type EdgeType,
  type Point,
  type Transform,
} from "../domain/types";
import { applyPan, applyZoomAtScreenPoint } from "./transform";
import { CardView } from "./CardView";
import { EdgeLayer } from "./EdgeLayer";
import { Marquee } from "./Marquee";
import { ReadingOrderLayer } from "./ReadingOrderLayer";
import { PolygonEditLayer } from "./PolygonEditLayer";
import { SuggestionDiffLayer } from "./SuggestionDiffLayer";
import type { SuggestionMoveDiff } from "./SuggestionDiffLayer";
import type { ReadingOrderDropPosition } from "../domain/reading_order_ops";
import { findNearestPolygonSegmentIndex } from "../domain/geometry/segment_pick";

const MIN_ZOOM = 0.2;
const MAX_ZOOM = 4;
const ZOOM_SENSITIVITY = 0.0015;
const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;

export type FocusReference = {
  id: string;
  kind: "card" | "island";
};

export function getFocusWorldPointForReference(document: DocumentV2, reference: FocusReference): { x: number; y: number } | null {
  if (reference.kind === "card") {
    const card = document.cards.find((item) => item.id === reference.id);
    if (!card) {
      return null;
    }
    return {
      x: card.x + CARD_WIDTH / 2,
      y: card.y + CARD_HEIGHT / 2,
    };
  }

  const island = document.islands.find((item) => item.id === reference.id);
  if (!island) {
    return null;
  }

  const focusedCards = document.cards.filter((card) => island.cardIds.includes(card.id));
  if (focusedCards.length === 0) {
    return null;
  }

  return {
    x: (Math.min(...focusedCards.map((card) => card.x)) + Math.max(...focusedCards.map((card) => card.x + CARD_WIDTH))) / 2,
    y: (Math.min(...focusedCards.map((card) => card.y)) + Math.max(...focusedCards.map((card) => card.y + CARD_HEIGHT))) / 2,
  };
}

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

export type CanvasViewState = {
  hideSourceCards: boolean;
  showCanonicalOnlyEdges: boolean;
  showReadingOrder: boolean;
};

export type CanvasCamera = {
  panX: number;
  panY: number;
  zoom: number;
  viewportWidth: number;
  viewportHeight: number;
};

export type CameraTransformRequest = {
  panX: number;
  panY: number;
  zoom: number;
  requestSeq: number;
};

type CanvasShellProps = {
  document: DocumentV2;
  onCardMove: (cardId: string, deltaWorldX: number, deltaWorldY: number) => void;
  selectedCardIds: string[];
  onCardSelect: (cardId: string, isShiftPressed: boolean) => void;
  onCanvasBackgroundClick: () => void;
  onMarqueeSelect: (cardIds: string[], isShiftPressed: boolean) => void;
  onTransformChange?: (transform: Transform) => void;
  onCameraChange?: (camera: CanvasCamera) => void;
  cameraTransformRequest?: CameraTransformRequest | null;
  hiddenCardIds?: Set<string>;
  deemphasizedCardIds?: Set<string>;
  hideSourceCards?: boolean;
  viewState?: CanvasViewState;
  /** @deprecated Use revealCardIds. */
  peekCardIds?: Set<string>;
  revealCardIds?: Set<string>;
  showCanonicalOnlyEdges?: boolean;
  summaryView?: boolean;
  abstractMapView?: boolean;
  searchQuery?: string;
  matchedCardIds?: Set<string>;
  activeMatchedCardId?: string | null;
  focusCardId?: string | null;
  focusWorldPoint?: { x: number; y: number } | null;
  focusRequestSeq?: number;
  flashReference?: FocusReference | null;
  flashRequestSeq?: number;
  isPickingEdgeTarget?: boolean;
  suggestionMoveDiffs?: SuggestionMoveDiff[];
  selectedEdgeId?: string | null;
  onEdgeSelect?: (edgeId: string) => void;
  onAggregatedEdgesChange?: (edges: AggregatedEdgeMeta[]) => void;
  showReadingOrder?: boolean;
  readingOrderEditMode?: boolean;
  onReadingOrderRemove?: (entryId: string) => void;
  onReadingOrderReorder?: (entryId: string, targetEntryId: string, position: ReadingOrderDropPosition) => void;
  visibleIslandIds?: Set<string>;
  polygonVertexEditIslandId?: string | null;
  onPolygonVertexMove?: (islandId: string, vertexIndex: number, point: Point) => void;
  onPolygonVertexAdd?: (islandId: string, segmentStartIndex: number, point: Point) => void;
  onPolygonVertexRemove?: (islandId: string, vertexIndex: number) => void;
  children?: ReactNode;
};

export type AggregatedEdgeSource = {
  sourceEdgeId?: string;
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
  fromLabel?: string;
  toLabel?: string;
  type: EdgeType;
  sources: AggregatedEdgeSource[];
  aggregateCount?: number;
  contributingEdgeIds?: string[];
  contributingCardIds?: string[];
  isDerivedIslandEdge?: boolean;
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
  onCameraChange,
  cameraTransformRequest = null,
  hiddenCardIds,
  deemphasizedCardIds,
  hideSourceCards = true,
  viewState,
  peekCardIds,
  revealCardIds,
  showCanonicalOnlyEdges = false,
  summaryView = false,
  abstractMapView = false,
  searchQuery = "",
  matchedCardIds,
  activeMatchedCardId,
  focusCardId,
  focusWorldPoint,
  focusRequestSeq = 0,
  flashReference = null,
  flashRequestSeq = 0,
  isPickingEdgeTarget = false,
  suggestionMoveDiffs,
  selectedEdgeId,
  onEdgeSelect,
  onAggregatedEdgesChange,
  showReadingOrder = false,
  readingOrderEditMode = false,
  onReadingOrderRemove,
  onReadingOrderReorder,
  visibleIslandIds,
  polygonVertexEditIslandId = null,
  onPolygonVertexMove,
  onPolygonVertexAdd,
  onPolygonVertexRemove,
  children,
}: CanvasShellProps) {
  const effectiveHideSourceCards = viewState?.hideSourceCards ?? hideSourceCards;
  const effectiveShowCanonicalOnlyEdges = viewState?.showCanonicalOnlyEdges ?? showCanonicalOnlyEdges;
  const effectiveShowReadingOrder = viewState?.showReadingOrder ?? showReadingOrder;

  const viewportRef = useRef<HTMLDivElement | null>(null);
  const dragRef = useRef<DragState | null>(null);

  const [transform, setTransform] = useState<Transform>(document.transform);
  const transformRef = useRef<Transform>(document.transform);
  const [dragMode, setDragMode] = useState<"none" | "pan" | "marquee">("none");
  const [viewportSize, setViewportSize] = useState({ width: 0, height: 0 });
  const [isSpacePressed, setIsSpacePressed] = useState(false);
  const [marqueeRect, setMarqueeRect] = useState<{
    x: number;
    y: number;
    width: number;
    height: number;
  } | null>(null);
  const [activeFlashReference, setActiveFlashReference] = useState<FocusReference | null>(null);

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
    if (!cameraTransformRequest) {
      return;
    }

    setTransform({
      panX: cameraTransformRequest.panX,
      panY: cameraTransformRequest.panY,
      zoom: cameraTransformRequest.zoom,
    });
  }, [cameraTransformRequest]);

  useEffect(() => {
    const viewport = viewportRef.current;
    if (!viewport) {
      return;
    }

    const updateViewportSize = () => {
      setViewportSize({
        width: viewport.clientWidth,
        height: viewport.clientHeight,
      });
    };

    updateViewportSize();
    const observer = new ResizeObserver(updateViewportSize);
    observer.observe(viewport);

    return () => {
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    if (!onCameraChange || viewportSize.width <= 0 || viewportSize.height <= 0) {
      return;
    }

    onCameraChange({
      panX: transform.panX,
      panY: transform.panY,
      zoom: transform.zoom,
      viewportWidth: viewportSize.width,
      viewportHeight: viewportSize.height,
    });
  }, [onCameraChange, transform.panX, transform.panY, transform.zoom, viewportSize.height, viewportSize.width]);

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

  useEffect(() => {
    if (!flashReference) {
      return;
    }

    setActiveFlashReference(flashReference);
    const timeoutId = window.setTimeout(() => {
      setActiveFlashReference((previousReference) => {
        if (
          previousReference?.kind === flashReference.kind &&
          previousReference.id === flashReference.id
        ) {
          return null;
        }
        return previousReference;
      });
    }, 1000);

    return () => {
      window.clearTimeout(timeoutId);
    };
  }, [flashReference, flashRequestSeq]);

  const selectedCardIdSet = useMemo(() => new Set(selectedCardIds), [selectedCardIds]);
  const emptyIdSet = useMemo(() => new Set<string>(), []);

  const sourceCardIdSet = useMemo(() => {
    if (!effectiveHideSourceCards) {
      return emptyIdSet;
    }
    return new Set(
      document.cards
        .filter((card) => isSourceCard(card))
        .map((card) => card.id)
    );
  }, [document.cards, effectiveHideSourceCards, emptyIdSet]);
  const revealedCardIdSet = revealCardIds ?? peekCardIds ?? emptyIdSet;

  const hiddenCardIdSet = hiddenCardIds ?? emptyIdSet;
  const deemphasizedCardIdSet = deemphasizedCardIds ?? emptyIdSet;
  const visibleIslandIdSet = visibleIslandIds ?? emptyIdSet;

  /*
   * Manual test steps (Abstract Map View):
   * 1) Turn on Abstract map view from View controls.
   * 2) Confirm non-lone-wolf cards hide, island summaries stay visible, and UNREVIEWED badges appear for draft summaries.
   * 3) Select an island and use temporary reveal/focus controls, then reload and confirm reveal state is not persisted.
   */
  const abstractMemberCardIdSet = useMemo(() => {
    if (!abstractMapView) {
      return emptyIdSet;
    }

    const memberCardIds = new Set<string>();
    for (const island of document.islands) {
      for (const cardId of island.cardIds) {
        memberCardIds.add(cardId);
      }
    }

    return memberCardIds;
  }, [abstractMapView, document.islands, emptyIdSet]);

  const isCardHidden = useCallback(
    (cardId: string) =>
      hiddenCardIdSet.has(cardId) ||
      (sourceCardIdSet.has(cardId) && !revealedCardIdSet.has(cardId)) ||
      (abstractMapView && abstractMemberCardIdSet.has(cardId) && !revealedCardIdSet.has(cardId)),
    [abstractMapView, abstractMemberCardIdSet, hiddenCardIdSet, sourceCardIdSet, revealedCardIdSet]
  );

  const hiddenEndpointIdSet = useMemo(() => {
    const hiddenSourceCardIds = Array.from(sourceCardIdSet).filter((cardId) => !revealedCardIdSet.has(cardId));
    const hiddenAbstractCardIds =
      abstractMapView
        ? Array.from(abstractMemberCardIdSet).filter((cardId) => !revealedCardIdSet.has(cardId))
        : [];
    return new Set([...hiddenCardIdSet, ...hiddenSourceCardIds, ...hiddenAbstractCardIds]);
  }, [abstractMapView, abstractMemberCardIdSet, hiddenCardIdSet, sourceCardIdSet, revealedCardIdSet]);

  const visibleCards = useMemo(() => {
    return document.cards.filter((card) => !isCardHidden(card.id));
  }, [document.cards, isCardHidden]);
  const visibleCardIdSet = useMemo(() => new Set(visibleCards.map((card) => card.id)), [visibleCards]);
  const highlightedCard = useMemo(() => {
    if (activeFlashReference?.kind !== "card") {
      return null;
    }

    return visibleCards.find((card) => card.id === activeFlashReference.id) ?? null;
  }, [activeFlashReference, visibleCards]);
  const highlightedIsland = useMemo(() => {
    if (activeFlashReference?.kind !== "island") {
      return null;
    }

    return document.islands.find((island) => island.id === activeFlashReference.id) ?? null;
  }, [activeFlashReference, document.islands]);
  const highlightedIslandBounds = useMemo(() => {
    if (!highlightedIsland) {
      return null;
    }

    const focusedCards = document.cards.filter((card) => highlightedIsland.cardIds.includes(card.id));
    if (focusedCards.length === 0) {
      return null;
    }

    const minX = Math.min(...focusedCards.map((card) => card.x)) - 24;
    const minY = Math.min(...focusedCards.map((card) => card.y)) - 24;
    const maxX = Math.max(...focusedCards.map((card) => card.x + CARD_WIDTH)) + 24;
    const maxY = Math.max(...focusedCards.map((card) => card.y + CARD_HEIGHT)) + 24;

    return {
      left: minX,
      top: minY,
      width: maxX - minX,
      height: maxY - minY,
    };
  }, [document.cards, highlightedIsland]);
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
        sourceEdgeId: edge.id,
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
        fromLabel: resolvedFromKind === "island"
          ? document.islands.find((island) => island.id === resolvedFromId)?.title?.trim() || resolvedFromId
          : cardsById.get(resolvedFromId)?.text || resolvedFromId,
        toLabel: resolvedToKind === "island"
          ? document.islands.find((island) => island.id === resolvedToId)?.title?.trim() || resolvedToId
          : cardsById.get(resolvedToId)?.text || resolvedToId,
        type: edge.type,
        sources: [nextSource],
      });
    }

    return Array.from(grouped.values());
  }, [document.cards, document.edges]);

  const derivedIslandEdges = useMemo(() => {
    if (!summaryView && !abstractMapView) {
      return [];
    }

    return getDerivedIslandEdges(document);
  }, [abstractMapView, document, summaryView]);

  const derivedIslandEdgeMeta = useMemo<AggregatedEdgeMeta[]>(() => {
    return derivedIslandEdges.map((edge) => ({
      id: edge.id,
      fromId: edge.fromId,
      toId: edge.toId,
      fromKind: "island",
      toKind: "island",
      fromLabel: document.islands.find((island) => island.id === edge.fromId)?.title?.trim() || edge.fromId,
      toLabel: document.islands.find((island) => island.id === edge.toId)?.title?.trim() || edge.toId,
      type: edge.type,
      sources: [],
      aggregateCount: edge.aggregateCount,
      contributingEdgeIds: edge.contributingEdgeIds,
      contributingCardIds: edge.contributingCardIds,
      isDerivedIslandEdge: true,
    }));
  }, [derivedIslandEdges]);

  const visibleEdges = useMemo(() => {
    let edges = getEdgesToRender(document, effectiveHideSourceCards === true).filter((edge) => {
      const isFromVisible = edge.fromKind === "island" ? visibleIslandIdSet.has(edge.fromId) : visibleCardIdSet.has(edge.fromId);
      const isToVisible = edge.toKind === "island" ? visibleIslandIdSet.has(edge.toId) : visibleCardIdSet.has(edge.toId);
      return isFromVisible && isToVisible;
    });

    if (effectiveShowCanonicalOnlyEdges) {
      edges = edges.filter((edge) => {
        return (
          edge.fromKind === "card" &&
          edge.toKind === "card" &&
          canonicalCardIdSet.has(edge.fromId) &&
          canonicalCardIdSet.has(edge.toId)
        );
      });
    }

    if (summaryView || abstractMapView) {
      edges = [
        ...edges,
        ...derivedIslandEdges.filter(
          (edge) => visibleIslandIdSet.has(edge.fromId) && visibleIslandIdSet.has(edge.toId)
        ),
      ];
    }

    return edges;
  }, [
    abstractMapView,
    canonicalCardIdSet,
    derivedIslandEdges,
    document,
    effectiveHideSourceCards,
    effectiveShowCanonicalOnlyEdges,
    summaryView,
    visibleCardIdSet,
    visibleIslandIdSet,
  ]);

  const visibleEdgeInspectorMeta = useMemo(() => {
    const visibleIds = new Set(visibleEdges.map((edge) => edge.id));
    const edgeMetaById = new Map<string, AggregatedEdgeMeta>();

    for (const edgeMeta of [...aggregatedEdges, ...derivedIslandEdgeMeta]) {
      if (visibleIds.has(edgeMeta.id)) {
        edgeMetaById.set(edgeMeta.id, edgeMeta);
      }
    }

    for (const edge of visibleEdges) {
      if (edgeMetaById.has(edge.id) || edge.fromKind !== "island" || edge.toKind !== "island") {
        continue;
      }

      edgeMetaById.set(edge.id, {
        id: edge.id,
        fromId: edge.fromId,
        toId: edge.toId,
        fromKind: "island",
        toKind: "island",
        fromLabel: document.islands.find((island) => island.id === edge.fromId)?.title?.trim() || edge.fromId,
        toLabel: document.islands.find((island) => island.id === edge.toId)?.title?.trim() || edge.toId,
        type: edge.type,
        sources: [
          {
            sourceEdgeId: edge.id,
            sourceFromCardId: edge.fromId,
            sourceToId: edge.toId,
            sourceToKind: "island",
          },
        ],
      });
    }

    return Array.from(edgeMetaById.values());
  }, [aggregatedEdges, derivedIslandEdgeMeta, document.islands, visibleEdges]);

  useEffect(() => {
    onAggregatedEdgesChange?.(visibleEdgeInspectorMeta);
  }, [onAggregatedEdgesChange, visibleEdgeInspectorMeta]);
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
    if (event.altKey && polygonVertexEditIslandId && polygonVertexEditShape && onPolygonVertexAdd) {
      const viewport = viewportRef.current;
      if (!viewport) {
        return;
      }

      const rect = viewport.getBoundingClientRect();
      const worldPoint = {
        x: (event.clientX - rect.left - transform.panX) / transform.zoom,
        y: (event.clientY - rect.top - transform.panY) / transform.zoom,
      };
      const segmentStartIndex = findNearestPolygonSegmentIndex(polygonVertexEditShape.points, worldPoint, 8 / transform.zoom);
      if (segmentStartIndex !== null) {
        event.preventDefault();
        event.stopPropagation();
        onPolygonVertexAdd(polygonVertexEditIslandId, segmentStartIndex, worldPoint);
        return;
      }
    }

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

  const polygonVertexEditShape = useMemo(() => {
    if (!polygonVertexEditIslandId) {
      return null;
    }

    const targetIsland = document.islands.find((island) => island.id === polygonVertexEditIslandId);
    if (!targetIsland || targetIsland.shape?.kind !== "polygon") {
      return null;
    }

    return targetIsland.shape;
  }, [document.islands, polygonVertexEditIslandId]);

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
          islands={document.islands.filter((island) => visibleIslandIdSet.has(island.id))}
          edges={visibleEdges}
          hiddenCardIds={hiddenEndpointIdSet}
          selectedEdgeId={selectedEdgeId}
          onEdgeSelect={onEdgeSelect}
        />
        <SuggestionDiffLayer diffs={visibleSuggestionMoveDiffs} cardWidth={CARD_WIDTH} cardHeight={CARD_HEIGHT} />
        {effectiveShowReadingOrder ? (
          <ReadingOrderLayer
            cards={document.cards}
            islands={document.islands.filter((island) => visibleIslandIdSet.has(island.id))}
            readingOrder={document.readingOrder ?? []}
            visibleCardIdSet={visibleCardIdSet}
            visibleIslandIdSet={visibleIslandIdSet}
            isEditMode={readingOrderEditMode}
            onRemoveEntry={onReadingOrderRemove}
            onReorderEntry={onReadingOrderReorder}
            onItemFocus={(_entryId, _kind, worldPoint) => {
              const viewport = viewportRef.current;
              if (!viewport) {
                return;
              }

              setTransform((previousTransform) =>
                focusTransformAtWorldPoint(previousTransform, worldPoint, viewport.clientWidth, viewport.clientHeight)
              );
            }}
          />
        ) : null}
        {children}
        {polygonVertexEditIslandId && polygonVertexEditShape && onPolygonVertexMove && onPolygonVertexRemove ? (
          <PolygonEditLayer
            points={polygonVertexEditShape.points}
            onVertexMove={(vertexIndex, screenPoint) => {
              const viewport = viewportRef.current;
              if (!viewport) {
                return;
              }

              const rect = viewport.getBoundingClientRect();
              const worldPoint = {
                x: (screenPoint.x - rect.left - transform.panX) / transform.zoom,
                y: (screenPoint.y - rect.top - transform.panY) / transform.zoom,
              };
              onPolygonVertexMove(polygonVertexEditIslandId, vertexIndex, worldPoint);
            }}
            onVertexRemove={(vertexIndex) => {
              onPolygonVertexRemove(polygonVertexEditIslandId, vertexIndex);
            }}
          />
        ) : null}
        {highlightedIslandBounds ? (
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              left: highlightedIslandBounds.left,
              top: highlightedIslandBounds.top,
              width: highlightedIslandBounds.width,
              height: highlightedIslandBounds.height,
              border: "3px solid #f59e0b",
              borderRadius: 14,
              boxShadow: "0 0 0 4px rgba(245, 158, 11, 0.2)",
              pointerEvents: "none",
            }}
          />
        ) : null}
        {highlightedCard ? (
          <div
            aria-hidden="true"
            style={{
              position: "absolute",
              left: highlightedCard.x - 4,
              top: highlightedCard.y - 4,
              width: CARD_WIDTH + 8,
              height: CARD_HEIGHT + 8,
              border: "3px solid #f59e0b",
              borderRadius: 10,
              boxShadow: "0 0 0 4px rgba(245, 158, 11, 0.2)",
              pointerEvents: "none",
              zIndex: 2,
            }}
          />
        ) : null}
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
              isDeemphasized={deemphasizedCardIdSet.has(card.id)}
            />
          );
        })}
      </div>
      {marqueeRect && dragMode === "marquee" ? <Marquee rect={marqueeRect} /> : null}
    </div>
  );
}
