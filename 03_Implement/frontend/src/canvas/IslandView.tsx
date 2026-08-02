import { memo, useContext } from "react";
import type { CSSProperties, MouseEvent } from "react";

import { getIslandPolygonPoints } from "../domain/geometry/island_geometry";
import { isSelfIntersectingPolygon } from "../domain/geometry/polygon_self_intersection";
import { isPointInPolygon } from "../domain/geometry/point_in_polygon";
import { shouldLoadLegacyIslandImage } from "../domain/legacy_island_image";
import {
  buildIslandSummaryLabelId,
  buildIslandTitleLabelId,
  buildIslandUnreviewedLabelId,
} from "../domain/view/label_culling";
import type { Card, Island, Point } from "../domain/types";
import { t } from "../i18n/translate";
import { LabelVisibilityContext } from "./LabelVisibilityContext";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const ISLAND_PADDING = 24;
const ISLAND_HEADER_HEIGHT = 24;
const ISLAND_HEADER_HEIGHT_WITH_SUMMARY = 70;
export const ISLAND_TITLE_MARGIN_LEFT = 10;
export const ISLAND_TITLE_MARGIN_TOP = 6;

type IslandViewProps = {
  island: Island;
  displayTitle?: string;
  cards: Card[];
  isSelected: boolean;
  isPeeking?: boolean;
  summaryView?: boolean;
  abstractMapView?: boolean;
  showSummary?: boolean;
  safeMode?: boolean;
  isCollapsedForView?: boolean;
  onSelect: (islandId: string, isShiftPressed: boolean) => void;
  onToggleCollapsed?: (islandId: string, collapsed: boolean) => void;
  onTitleDoubleClick?: (islandId: string) => void;
  onFocusIsland?: (islandId: string) => void;
  isShapeStale?: boolean;
  onPeekStart?: (islandId: string) => void;
  onPeekEnd?: () => void;
  isPickingEdgeTarget?: boolean;
  zIndex?: number;
  /** UX-VISUAL-02: deterministic "protection" mark for a small island. */
  isProtected?: boolean;
};

type EdgeHitbox = {
  key: string;
  style: CSSProperties;
};

export function resolveIslandRepresentativeTitle(
  island: Island,
  cards: Card[],
  fallbackTitle = t("canvas.island.default_title"),
): string {
  const placardText = island.placardCardId
    ? cards.find((card) => card.id === island.placardCardId)?.text?.trim() ?? ""
    : "";

  return placardText || island.title?.trim() || fallbackTitle;
}

const EDGE_HITBOXES: EdgeHitbox[] = [
  {
    key: "top",
    style: {
      left: 0,
      top: 0,
      width: "100%",
      height: 8,
    },
  },
  {
    key: "right",
    style: {
      right: 0,
      top: 0,
      width: 8,
      height: "100%",
    },
  },
  {
    key: "bottom",
    style: {
      left: 0,
      bottom: 0,
      width: "100%",
      height: 8,
    },
  },
  {
    key: "left",
    style: {
      left: 0,
      top: 0,
      width: 8,
      height: "100%",
    },
  },
];

function getBoundsFromPoints(points: Point[]) {
  if (points.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  for (const point of points) {
    minX = Math.min(minX, point.x);
    minY = Math.min(minY, point.y);
    maxX = Math.max(maxX, point.x);
    maxY = Math.max(maxY, point.y);
  }

  return {
    left: minX,
    top: minY,
    width: maxX - minX,
    height: maxY - minY,
  };
}

export function getIslandBounds(island: Island, cards: Card[]) {
  const polygonPoints = getIslandPolygonPoints(island);
  if (polygonPoints.length >= 3 && !isSelfIntersectingPolygon(polygonPoints)) {
    return getBoundsFromPoints(polygonPoints);
  }

  const islandCards = cards.filter((card) => island.cardIds.includes(card.id));
  if (islandCards.length === 0) {
    return null;
  }

  let minX = Infinity;
  let minY = Infinity;
  let maxX = -Infinity;
  let maxY = -Infinity;

  islandCards.forEach((card) => {
    minX = Math.min(minX, card.x);
    minY = Math.min(minY, card.y);
    maxX = Math.max(maxX, card.x + CARD_WIDTH);
    maxY = Math.max(maxY, card.y + CARD_MIN_HEIGHT);
  });

  return {
    left: minX - ISLAND_PADDING,
    top: minY - ISLAND_PADDING,
    width: maxX - minX + ISLAND_PADDING * 2,
    height: maxY - minY + ISLAND_PADDING * 2,
  };
}

function IslandViewComponent({
  island,
  displayTitle,
  cards,
  isSelected,
  isPeeking = false,
  summaryView = false,
  abstractMapView = false,
  showSummary = true,
  safeMode = false,
  isCollapsedForView,
  onSelect,
  onToggleCollapsed,
  onTitleDoubleClick,
  onFocusIsland,
  isShapeStale = false,
  onPeekStart,
  onPeekEnd,
  isPickingEdgeTarget = false,
  zIndex = 0,
  isProtected = false,
}: IslandViewProps) {
  const bounds = getIslandBounds(island, cards);
  const { acceptedLabelIds } = useContext(LabelVisibilityContext);
  const hasCritique = typeof island.critique === "string" && island.critique.trim().length > 0;
  const placardCard = island.placardCardId ? cards.find((card) => card.id === island.placardCardId) : undefined;
  const placardText = placardCard?.text?.trim() ?? "";
  const resolvedDisplayTitle = displayTitle?.trim() || island.title?.trim() || t("canvas.island.default_title");
  const representativeTitle = resolveIslandRepresentativeTitle(island, cards, resolvedDisplayTitle);
  const hasSummary = typeof island.summaryText === "string" && island.summaryText.trim().length > 0;
  const hideUnreviewedSummary = safeMode && island.summaryReviewed === false && hasSummary;
  const isCollapsed = isCollapsedForView ?? island.collapsed === true;
  const headerHeight = hasSummary || abstractMapView ? ISLAND_HEADER_HEIGHT_WITH_SUMMARY : ISLAND_HEADER_HEIGHT;
  const islandBackgroundImage = shouldLoadLegacyIslandImage(safeMode, island.imageUrl)
    ? `url("${encodeURI(island.imageUrl!)}")`
    : null;
  const polygonPoints = getIslandPolygonPoints(island);
  const hasPolygon = polygonPoints.length >= 3 && !isSelfIntersectingPolygon(polygonPoints);
  // UX-SCALE-01 (c): (vertexCount - 4) / 2 = count of reflex ("concave")
  // corners — 0 for a plain rectangle. A structural count, not a score/rank
  // (ADR-0048 D3 anti-scoring); shown only when non-zero (CB-1: no badge
  // for the common default-shape case).
  const outlineComplexity = hasPolygon ? Math.max(0, Math.round((polygonPoints.length - 4) / 2)) : 0;
  const showTitleLabel = acceptedLabelIds ? acceptedLabelIds.has(buildIslandTitleLabelId(island.id)) : true;
  const showSummaryLabel = acceptedLabelIds ? acceptedLabelIds.has(buildIslandSummaryLabelId(island.id)) : true;
  const showUnreviewedLabel = acceptedLabelIds ? acceptedLabelIds.has(buildIslandUnreviewedLabelId(island.id)) : true;
  const showStandaloneUnreviewed =
    island.summaryReviewed === false &&
    hasSummary &&
    showUnreviewedLabel &&
    (!showSummary || !showSummaryLabel);

  if (!bounds) {
    return null;
  }

  const polygonPath = hasPolygon
    ? polygonPoints.map((point) => `${point.x - bounds.left},${point.y - bounds.top}`).join(" ")
    : null;
  const collapsedActionLabel = isCollapsed ? t("canvas.island.expand_action") : t("canvas.island.collapse_action");

  const handleIslandPointerSelect = (event: MouseEvent<HTMLElement | SVGSVGElement>) => {
    event.stopPropagation();
    if (isPickingEdgeTarget) {
      return;
    }

    if (hasPolygon && event.detail !== 0) {
      const targetRect = event.currentTarget.getBoundingClientRect();
      if (targetRect.width <= 0 || targetRect.height <= 0) {
        return;
      }

      const localX = event.clientX - targetRect.left;
      const localY = event.clientY - targetRect.top;
      const clickPoint = {
        x: bounds.left + localX * (bounds.width / targetRect.width),
        y: bounds.top + localY * (bounds.height / targetRect.height),
      };

      if (!isPointInPolygon(clickPoint, polygonPoints)) {
        return;
      }
    }

    onSelect(island.id, event.shiftKey);
  };

  return (
    <div
      style={{
        pointerEvents: "none",
        position: "absolute",
        left: bounds.left,
        top: bounds.top,
        width: bounds.width,
        height: bounds.height,
        borderRadius: 12,
        boxSizing: "border-box",
        overflow: "hidden",
        zIndex,
        isolation: "isolate",
      }}
    >
      {hasPolygon && polygonPath ? (
        <button
          type="button"
          aria-label={t("canvas.island.select_label", { id: island.id })}
          onClick={handleIslandPointerSelect}
          style={{
            position: "absolute",
            inset: 0,
            border: "none",
            backgroundColor: "transparent",
            padding: 0,
            pointerEvents: isPickingEdgeTarget ? "none" : "auto",
            zIndex: 2,
            cursor: isPickingEdgeTarget ? "default" : "pointer",
          }}
        >
          <svg
            aria-hidden="true"
            focusable="false"
            style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
            viewBox={`0 0 ${Math.max(bounds.width, 1)} ${Math.max(bounds.height, 1)}`}
          >
            <polygon points={polygonPath} fill="rgba(0, 0, 0, 0.001)" stroke="transparent" />
          </svg>
        </button>
      ) : (
        <>
          <button
            type="button"
            onClick={handleIslandPointerSelect}
            style={{
              pointerEvents: isPickingEdgeTarget ? "none" : "auto",
              position: "absolute",
              inset: 0,
              border: "none",
              backgroundColor: "transparent",
              padding: 0,
              cursor: isPickingEdgeTarget ? "default" : "pointer",
              zIndex: 1,
            }}
            aria-label={t("canvas.island.select_label", { id: island.id })}
          />
          {EDGE_HITBOXES.map((edgeHitbox) => (
            <div
              key={edgeHitbox.key}
              onClick={handleIslandPointerSelect}
              aria-hidden="true"
              style={{
                pointerEvents: isPickingEdgeTarget ? "none" : "auto",
                position: "absolute",
                ...edgeHitbox.style,
                cursor: isPickingEdgeTarget ? "default" : "pointer",
                zIndex: 2,
              }}
            />
          ))}
        </>
      )}
      {islandBackgroundImage ? (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            backgroundImage: islandBackgroundImage,
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
            opacity: 0.15,
            zIndex: 0,
          }}
        />
      ) : null}
      {hasPolygon && polygonPath ? (
        <svg
          aria-hidden="true"
          style={{ position: "absolute", inset: 0, zIndex: 1, pointerEvents: "none" }}
          viewBox={`0 0 ${Math.max(bounds.width, 1)} ${Math.max(bounds.height, 1)}`}
        >
          <polygon
            points={polygonPath}
            fill={isSelected ? "rgba(14, 165, 233, 0.12)" : "rgba(14, 165, 233, 0.05)"}
            stroke={isSelected ? "#0284c7" : "#0ea5e9"}
            strokeWidth={2}
            strokeLinejoin="round"
          />
        </svg>
      ) : (
        <div
          aria-hidden="true"
          style={{
            position: "absolute",
            inset: 0,
            border: isSelected ? "2px solid #0284c7" : "2px solid #0ea5e9",
            borderRadius: 12,
            backgroundColor: isSelected ? "rgba(14, 165, 233, 0.12)" : "rgba(14, 165, 233, 0.05)",
            boxSizing: "border-box",
            zIndex: 1,
          }}
        />
      )}
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: "100%",
          height: headerHeight,
          borderBottom: "1px solid #bae6fd",
          backgroundColor: "rgba(240, 249, 255, 0.9)",
          zIndex: 1,
        }}
      />
      <div
        onClick={(event) => {
          event.stopPropagation();
          if (!isPickingEdgeTarget) onSelect(island.id, event.shiftKey);
        }}
        onDoubleClick={(event) => {
          event.stopPropagation();
          if (isPickingEdgeTarget) {
            return;
          }

          if (abstractMapView) {
            onTitleDoubleClick?.(island.id);
            return;
          }

          onToggleCollapsed?.(island.id, !isCollapsed);
        }}
        style={{
          pointerEvents: isPickingEdgeTarget ? "none" : "auto",
          position: "absolute",
          left: ISLAND_TITLE_MARGIN_LEFT,
          top: ISLAND_TITLE_MARGIN_TOP,
          fontSize: abstractMapView ? 14 : 12,
          fontWeight: abstractMapView ? 800 : 700,
          color: "#0c4a6e",
          backgroundColor: "#f0f9ff",
          padding: "2px 6px",
          borderRadius: 6,
          border: "1px solid #bae6fd",
          zIndex: 3,
          cursor: isPickingEdgeTarget ? "default" : "pointer",
          display: "flex",
          alignItems: "center",
          gap: 6,
        }}
      >
        {showTitleLabel ? (isCollapsed ? representativeTitle : resolvedDisplayTitle) : null}
        <span
          style={{
            fontSize: 10,
            fontWeight: 700,
            color: "#0c4a6e",
            backgroundColor: "#e0f2fe",
            border: "1px solid #bae6fd",
            borderRadius: 999,
            padding: "1px 6px",
          }}
          title={t("canvas.island.card_count_title", { count: island.cardIds.length })}
        >
          #{island.cardIds.length}
        </span>
        {outlineComplexity > 0 ? (
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#7c2d12",
              backgroundColor: "#fef3e2",
              border: "1px solid #fed7aa",
              borderRadius: 999,
              padding: "1px 6px",
            }}
            title={t("canvas.island.outline_complexity_title", { count: outlineComplexity })}
          >
            {t("canvas.island.outline_complexity_badge", { count: outlineComplexity })}
          </span>
        ) : null}
        {isProtected ? (
          // UX-VISUAL-02 (ADR-0048 D3): protection mark for a small island.
          // Mirrors CardView's protection chip exactly (dashed border, square dot,
          // borderRadius 4 not the 999 pill shape used by the neighboring count/
          // placard badges) so the "protection" form signature is one channel,
          // consistent across cards, islands, and the legend swatch.
          <span
            aria-label={t("canvas.island.protected")}
            title={t("canvas.island.protected_title")}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 3,
              fontSize: 10,
              fontWeight: 600,
              color: "#334155",
              backgroundColor: "#f8fafc",
              border: "1px dashed #94a3b8",
              borderRadius: 4,
              padding: "1px 6px",
            }}
          >
            <span aria-hidden="true" style={{ width: 6, height: 6, borderRadius: 2, backgroundColor: "#94a3b8" }} />
            {t("canvas.island.protected")}
          </span>
        ) : null}
        {placardText && !isCollapsed ? (
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#1d4ed8",
              backgroundColor: "#dbeafe",
              border: "1px solid #93c5fd",
              borderRadius: 999,
              padding: "1px 6px",
              maxWidth: 150,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={placardText}
          >
            {placardText}
          </span>
        ) : null}
        {isCollapsed ? (
          <span
            style={{
              fontSize: 10,
              fontWeight: 700,
              color: "#1d4ed8",
              backgroundColor: "#dbeafe",
              border: "1px solid #93c5fd",
              borderRadius: 999,
              padding: "1px 6px",
              maxWidth: 180,
              overflow: "hidden",
              textOverflow: "ellipsis",
              whiteSpace: "nowrap",
            }}
            title={representativeTitle}
          >
            {t("canvas.island.representative_title", { title: representativeTitle })}
          </span>
        ) : null}
        {isCollapsed ? <span style={{ fontWeight: 500 }}>{t("canvas.island.collapsed_badge")}</span> : null}
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onFocusIsland?.(island.id);
          }}
          onDoubleClick={(event) => {
            event.stopPropagation();
          }}
          style={{
            pointerEvents: isPickingEdgeTarget ? "none" : "auto",
            border: "1px solid #7dd3fc",
            borderRadius: 4,
            backgroundColor: "#e0f2fe",
            color: "#075985",
            fontSize: 10,
            lineHeight: 1,
            padding: "3px 6px",
            cursor: isPickingEdgeTarget ? "default" : "pointer",
          }}
          aria-label={t("canvas.island.focus_label", { id: island.id })}
          title={t("canvas.island.focus_title")}
        >
          ⤢
        </button>
        <button
          type="button"
          onClick={(event) => {
            event.stopPropagation();
            onToggleCollapsed?.(island.id, !isCollapsed);
          }}
          onDoubleClick={(event) => {
            event.stopPropagation();
          }}
          style={{
            pointerEvents: isPickingEdgeTarget ? "none" : "auto",
            border: "1px solid #7dd3fc",
            borderRadius: 4,
            backgroundColor: "#e0f2fe",
            color: "#075985",
            fontSize: 10,
            lineHeight: 1,
            padding: "3px 6px",
            cursor: isPickingEdgeTarget ? "default" : "pointer",
          }}
          aria-label={t("canvas.island.toggle_collapsed_label", { action: collapsedActionLabel, id: island.id })}
        >
          {collapsedActionLabel}
        </button>
        {isShapeStale ? (
          <span style={{ fontWeight: 600, color: "#b45309" }}>{t("canvas.island.stale_badge")}</span>
        ) : null}
        {isCollapsed ? (
          <button
            type="button"
            onPointerDown={(event) => {
              event.stopPropagation();
              onPeekStart?.(island.id);

              window.addEventListener(
                "mouseup",
                () => {
                  onPeekEnd?.();
                },
                { once: true }
              );
            }}
            onDoubleClick={(event) => {
              event.stopPropagation();
            }}
            style={{
              pointerEvents: isPickingEdgeTarget ? "none" : "auto",
              border: "1px solid #7dd3fc",
              borderRadius: 4,
              backgroundColor: isPeeking ? "#0ea5e9" : "#e0f2fe",
              color: isPeeking ? "#f8fafc" : "#075985",
              fontSize: 10,
              lineHeight: 1,
              padding: "3px 6px",
              cursor: isPickingEdgeTarget ? "default" : "pointer",
            }}
            aria-label={t("canvas.island.peek_label", { id: island.id })}
            title={t("canvas.island.peek_title")}
          >
            {t("canvas.island.peek_action")}
          </button>
        ) : null}
        {hasCritique ? (
          <span
            aria-label={t("canvas.island.critique_note_indicator")}
            title={t("canvas.island.critique_note_indicator")}
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              backgroundColor: "#f59e0b",
            }}
          />
        ) : null}
      </div>

      {((hasSummary && showSummary) || abstractMapView) && showSummaryLabel ? (
        <div
          style={{
            position: "absolute",
            left: ISLAND_TITLE_MARGIN_LEFT,
            top: ISLAND_TITLE_MARGIN_TOP + 28,
            right: ISLAND_TITLE_MARGIN_LEFT,
            fontSize: abstractMapView ? 13 : summaryView ? 12 : 11,
            fontWeight: abstractMapView ? 700 : summaryView ? 600 : 500,
            lineHeight: 1.35,
            color: "#0c4a6e",
            zIndex: 3,
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
          title={hideUnreviewedSummary ? t("canvas.island.unreviewed_hidden") : hasSummary ? island.summaryText : t("canvas.island.no_summary")}
        >
          {hideUnreviewedSummary ? (
            <span style={{ color: "#92400e", fontWeight: 700 }}>{t("canvas.island.unreviewed_hidden")}</span>
          ) : hasSummary ? (
            island.summaryText
          ) : (
            <span style={{ color: "#64748b" }}>{t("canvas.island.no_summary")}</span>
          )}
          {island.summaryReviewed === false && hasSummary && showUnreviewedLabel ? (
            <span
              style={{
                marginLeft: 8,
                display: "inline-block",
                fontSize: 10,
                fontWeight: 800,
                color: "#92400e",
                backgroundColor: "#fef3c7",
                border: "1px solid #fde68a",
                borderRadius: 999,
                padding: "1px 6px",
              }}
            >
              {t("canvas.island.unreviewed_badge")}
            </span>
          ) : null}
        </div>
      ) : null}
      {showStandaloneUnreviewed ? (
        <div
          style={{
            position: "absolute",
            right: ISLAND_TITLE_MARGIN_LEFT,
            top: ISLAND_TITLE_MARGIN_TOP,
            fontSize: 10,
            fontWeight: 800,
            color: "#92400e",
            backgroundColor: "#fef3c7",
            border: "1px solid #fde68a",
            borderRadius: 999,
            padding: "1px 6px",
            zIndex: 3,
          }}
          title={t("canvas.island.summary_unreviewed_title")}
        >
          {t("canvas.island.unreviewed_badge")}
        </div>
      ) : null}
    </div>
  );
}

export const IslandView = memo(IslandViewComponent);
