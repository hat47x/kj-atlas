import { memo, useMemo } from "react";
import type { MouseEvent } from "react";

import { getIslandPolygonPoints } from "../domain/geometry/island_geometry";
import { polygonCentroid } from "../domain/geometry/polygon_centroid";
import { isSelfIntersectingPolygon } from "../domain/geometry/polygon_self_intersection";
import { rayPolygonBoundaryIntersection } from "../domain/geometry/ray_polygon_intersect";
import type { RenderEdge } from "../domain/edge_aggregate";
import type { Card, Island } from "../domain/types";
import { resolveKnownEdgeType } from "../domain/types";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const ISLAND_PADDING = 24;
const WORLD_HALF_SIZE = 100000;
const WORLD_SIZE = WORLD_HALF_SIZE * 2;
// DOMAIN-KJ-01: arrowhead size in WORLD units (scales with zoom, unlike the
// non-scaling line stroke). At far LOD only derived edges remain visible and
// those render type-suppressed (no arrowheads), so the shrink is acceptable.
const ARROW_HEAD_SIZE = 14;
const ARROW_HEAD_SPREAD = Math.PI / 7;

function buildArrowHeadPoints(tip: CenterPoint, angle: number): string {
  const left = {
    x: tip.x - ARROW_HEAD_SIZE * Math.cos(angle - ARROW_HEAD_SPREAD),
    y: tip.y - ARROW_HEAD_SIZE * Math.sin(angle - ARROW_HEAD_SPREAD),
  };
  const right = {
    x: tip.x - ARROW_HEAD_SIZE * Math.cos(angle + ARROW_HEAD_SPREAD),
    y: tip.y - ARROW_HEAD_SIZE * Math.sin(angle + ARROW_HEAD_SPREAD),
  };
  return `${tip.x},${tip.y} ${left.x},${left.y} ${right.x},${right.y}`;
}

// Card anchors are card CENTERS (the line end is covered by the card box, so
// an arrowhead drawn there would be invisible). Walk from the center toward
// the opposite endpoint until the card's rectangle boundary is reached and
// put the arrow tip there. Island anchors are already boundary points.
function rectBoundaryTowards(center: CenterPoint, halfWidth: number, halfHeight: number, toward: CenterPoint): CenterPoint {
  const dx = toward.x - center.x;
  const dy = toward.y - center.y;
  if (dx === 0 && dy === 0) {
    return center;
  }

  const tx = dx !== 0 ? halfWidth / Math.abs(dx) : Number.POSITIVE_INFINITY;
  const ty = dy !== 0 ? halfHeight / Math.abs(dy) : Number.POSITIVE_INFINITY;
  const t = Math.min(tx, ty, 1);
  return { x: center.x + dx * t, y: center.y + dy * t };
}

type EdgeLayerProps = {
  cards: Card[];
  islands: Island[];
  edges: RenderEdge[];
  hiddenCardIds: Set<string>;
  selectedEdgeId?: string | null;
  highlightedEdgeIds?: string[];
  onEdgeSelect?: (edgeId: string, edge: RenderEdge) => void;
};

type CenterPoint = {
  x: number;
  y: number;
};

function getCardCenter(card: Card): CenterPoint {
  return {
    x: card.x + CARD_WIDTH / 2,
    y: card.y + CARD_MIN_HEIGHT / 2,
  };
}

export function getRenderableIslandPolygonPoints(island: Island) {
  const polygonPoints = getIslandPolygonPoints(island);
  if (polygonPoints.length < 3 || isSelfIntersectingPolygon(polygonPoints)) {
    return [];
  }

  return polygonPoints;
}

function getIslandCenter(island: Island, cardsById: Map<string, Card>): CenterPoint | null {
  const polygonPoints = getRenderableIslandPolygonPoints(island);
  if (polygonPoints.length >= 3) {
    return polygonCentroid(polygonPoints);
  }

  const islandCards = island.cardIds
    .map((cardId) => cardsById.get(cardId))
    .filter((card): card is Card => card !== undefined);

  if (islandCards.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const card of islandCards) {
    minX = Math.min(minX, card.x);
    minY = Math.min(minY, card.y);
    maxX = Math.max(maxX, card.x + CARD_WIDTH);
    maxY = Math.max(maxY, card.y + CARD_MIN_HEIGHT);
  }

  const left = minX - ISLAND_PADDING;
  const top = minY - ISLAND_PADDING;
  const width = maxX - minX + ISLAND_PADDING * 2;
  const height = maxY - minY + ISLAND_PADDING * 2;

  return {
    x: left + width / 2,
    y: top + height / 2,
  };
}

function getDashArray(edge: RenderEdge): string | undefined {
  if (edge.isDerived) {
    return "4 4";
  }

  if (edge.type === "negate") {
    return "6 4";
  }

  return undefined;
}

function EdgeLayerComponent({
  cards,
  islands,
  edges,
  hiddenCardIds,
  selectedEdgeId,
  highlightedEdgeIds,
  onEdgeSelect,
}: EdgeLayerProps) {
  const cardCenterById = useMemo(() => {
    const nextCardCenterById = new Map<string, CenterPoint>();

    for (const card of cards) {
      nextCardCenterById.set(card.id, getCardCenter(card));
    }

    return nextCardCenterById;
  }, [cards]);

  const islandCenterById = useMemo(() => {
    const cardsById = new Map(cards.map((card) => [card.id, card]));
    const nextIslandCenterById = new Map<string, CenterPoint>();

    for (const island of islands) {
      const center = getIslandCenter(island, cardsById);
      if (center) {
        nextIslandCenterById.set(island.id, center);
      }
    }

    return nextIslandCenterById;
  }, [cards, islands]);

  const islandById = useMemo(() => new Map(islands.map((island) => [island.id, island])), [islands]);
  const highlightedEdgeIdSet = useMemo(() => new Set(highlightedEdgeIds ?? []), [highlightedEdgeIds]);

  const drawableEdges = useMemo(() => {
    return edges.filter((edge) => {
      if (edge.fromKind === "card" && hiddenCardIds?.has(edge.fromId)) {
        return false;
      }

      if (edge.toKind === "card" && hiddenCardIds?.has(edge.toId)) {
        return false;
      }

      const fromCenter = edge.fromKind === "card" ? cardCenterById.get(edge.fromId) : islandCenterById.get(edge.fromId);
      const toCenter = edge.toKind === "card" ? cardCenterById.get(edge.toId) : islandCenterById.get(edge.toId);

      return fromCenter !== undefined && toCenter !== undefined;
    });
  }, [cardCenterById, edges, hiddenCardIds, islandCenterById]);

  function getEdgeAnchor(endpointKind: "card" | "island", endpointId: string, oppositePoint: CenterPoint): CenterPoint | null {
    if (endpointKind === "card") {
      return cardCenterById.get(endpointId) ?? null;
    }

    const island = islandById.get(endpointId);
    const islandCenter = islandCenterById.get(endpointId);
    if (!island || !islandCenter) {
      return null;
    }

    const polygonPoints = getRenderableIslandPolygonPoints(island);
    if (polygonPoints.length < 3) {
      return islandCenter;
    }

    const centroid = polygonCentroid(polygonPoints);
    if (!centroid) {
      return islandCenter;
    }

    const intersection = rayPolygonBoundaryIntersection(centroid, oppositePoint, polygonPoints);
    return intersection ?? centroid;
  }

  return (
    // DOMAIN-KJ-01 fix of a long-standing rendering defect: the previous
    // markup relied on x/y ATTRIBUTES on this outer <svg>, which are ignored
    // for an HTML-embedded root svg — so the viewBox mapped world (0,0) to
    // +100000px inside the element box and every edge painted far off
    // screen (lines existed in the DOM but were never visible). The world
    // window must instead be positioned via CSS left/top so that world
    // (0,0) lands exactly on the transformed container's origin.
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
        pointerEvents: "auto",
      }}
    >
      {drawableEdges.map((edge) => {
        const fromCenter = edge.fromKind === "card" ? cardCenterById.get(edge.fromId) : islandCenterById.get(edge.fromId);
        const toCenter = edge.toKind === "card" ? cardCenterById.get(edge.toId) : islandCenterById.get(edge.toId);

        if (!fromCenter || !toCenter) {
          return null;
        }

        const fromAnchor = getEdgeAnchor(edge.fromKind, edge.fromId, toCenter);
        const toAnchor = getEdgeAnchor(edge.toKind, edge.toId, fromCenter);
        if (!fromAnchor || !toAnchor) {
          return null;
        }

        const isSelected = selectedEdgeId === edge.id;
        const isHighlighted = highlightedEdgeIdSet.has(edge.id);

        const handleEdgeClick = (event: MouseEvent<SVGLineElement>) => {
          event.stopPropagation();
          onEdgeSelect?.(edge.id, edge);
        };

        const midX = (fromAnchor.x + toAnchor.x) / 2;
        const midY = (fromAnchor.y + toAnchor.y) / 2;

        // ベースの線色（main準拠）
        const baseStroke = edge.isDerived ? "#0f766e" : "#64748b";
        const selectedStroke = "#2563eb";
        const highlightedStroke = "#f59e0b";
        const strokeColor = isSelected ? selectedStroke : isHighlighted ? highlightedStroke : baseStroke;

        // DOMAIN-KJ-01 (schemas.md §3.3.1): type symbols render only on
        // NON-derived edges — derived/aggregated edges stay type-suppressed
        // and generic (UX-SCALE-01 redline), and their endpoint order is
        // normalized, so an arrowhead there could point the wrong way.
        // Unknown preserved types resolve to "related" (no symbol).
        const resolvedType = edge.isDerived ? "related" : resolveKnownEdgeType(edge.type);
        const edgeAngle = Math.atan2(toAnchor.y - fromAnchor.y, toAnchor.x - fromAnchor.x);
        const toArrowTip =
          edge.toKind === "card"
            ? rectBoundaryTowards(toAnchor, CARD_WIDTH / 2, CARD_MIN_HEIGHT / 2, fromAnchor)
            : toAnchor;
        const fromArrowTip =
          edge.fromKind === "card"
            ? rectBoundaryTowards(fromAnchor, CARD_WIDTH / 2, CARD_MIN_HEIGHT / 2, toAnchor)
            : fromAnchor;

        return (
          <g key={edge.id}>
            {/* 見た目の線 */}
            <line
              x1={fromAnchor.x}
              y1={fromAnchor.y}
              x2={toAnchor.x}
              y2={toAnchor.y}
              stroke={isSelected ? selectedStroke : isHighlighted ? highlightedStroke : baseStroke}
              strokeWidth={isSelected ? 3 : isHighlighted ? 3.5 : edge.isDerived ? 2.5 : 2}
              vectorEffect="non-scaling-stroke"
              strokeLinecap="round"
              strokeDasharray={getDashArray(edge)}
              pointerEvents="none"
            />

            {/* クリック/選択用のヒット領域（透明・太め） */}
            <line
              x1={fromAnchor.x}
              y1={fromAnchor.y}
              x2={toAnchor.x}
              y2={toAnchor.y}
              stroke="transparent"
              strokeWidth={10}
              vectorEffect="non-scaling-stroke"
              strokeLinecap="round"
              pointerEvents="stroke"
              style={{ cursor: "pointer" }}
              role="button"
              tabIndex={0}
              onPointerDown={(event) => {
                event.stopPropagation();
              }}
              onClick={handleEdgeClick}
              onKeyDown={(event) => {
                if (event.key === "Enter" || event.key === " ") {
                  event.preventDefault();
                  event.stopPropagation();
                  onEdgeSelect?.(edge.id, edge);
                }
              }}
            />

            {resolvedType === "causal" || resolvedType === "mutual" ? (
              // 因果: fromId（原因）→ toId（結果）の意味方向を to 端の矢印で
              // 示す。相互は両端に矢印（⇄）。矢先はカード/島の境界に置く。
              <polygon
                data-edge-symbol="arrow-to"
                points={buildArrowHeadPoints(toArrowTip, edgeAngle)}
                fill={strokeColor}
                pointerEvents="none"
              />
            ) : null}
            {resolvedType === "mutual" ? (
              <polygon
                data-edge-symbol="arrow-from"
                points={buildArrowHeadPoints(fromArrowTip, edgeAngle + Math.PI)}
                fill={strokeColor}
                pointerEvents="none"
              />
            ) : null}
            {resolvedType === "equivalence" ? (
              // 同値: 中点に「=」記号（×N ラベルと同じ midpoint パターン）。
              <text
                data-edge-symbol="equivalence"
                x={midX}
                y={midY - 6}
                fontSize={16}
                fontWeight={700}
                fill={strokeColor}
                textAnchor="middle"
                pointerEvents="none"
              >
                =
              </text>
            ) : null}
            {edge.isDerived && (edge.aggregateCount ?? 0) > 1 ? (
              <text
                x={midX}
                y={midY - 4}
                fontSize={11}
                fill="#115e59"
                textAnchor="middle"
                vectorEffect="non-scaling-stroke"
              >
                ×{edge.aggregateCount}
              </text>
            ) : null}
          </g>
        );
      })}
    </svg>
  );
}

export const EdgeLayer = memo(EdgeLayerComponent);
