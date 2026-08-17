import { useEffect, useMemo, useRef, useState } from "react";
import type { PointerEvent as ReactPointerEvent } from "react";
import { t } from "../i18n/translate";
import type { Card, Island } from "../domain/types";
import type { CanvasCamera } from "../canvas/CanvasShell";
import { getCardWorldBounds, getIslandWorldBounds } from "../domain/geometry/bounds";
import { screenToWorld } from "../canvas/transform";
import { loadMinimapCollapsed, saveMinimapCollapsed } from "../storage/minimap_collapsed";
import type { TenantBrowserStorageScope } from "../storage/tenant_scope";

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
const MINIMAP_WIDTH = 160;
const MINIMAP_HEIGHT = 110;
const MINIMAP_PADDING_WORLD = 40;
const AUTO_COLLAPSE_WIDTH_PX = 640;

// Mirrors CardView.tsx's CLAIM_TYPE_STYLE.fg values (ADR-0048 D1: fixed tokens,
// no new colors). Duplicated as plain hex here since CardView's map is a local
// (i18n-labeled) const, not an exported module-level constant.
const CLAIM_TYPE_DOT_COLOR: Record<string, string> = {
  fact: "#166534",
  claim: "#1e40af",
  hypothesis: "#6b21a8",
  unknown: "#475569",
};

export type MinimapProps = {
  cards: Card[];
  islands: Island[];
  camera: CanvasCamera | null;
  storageScope?: TenantBrowserStorageScope;
  onPan: (panX: number, panY: number) => void;
};

// UX-SCALE-01 (ADR-0048 D2, Round 5 redline): a small, corner, collapsible
// overview of the whole document — current-viewport frame is draggable to
// pan. Scoped to pointer interaction only (a supplementary navigation aid,
// not the sole path to any operation — panning/fit-to-view remain reachable
// via existing keyboard-accessible controls), consistent with ADR-0030's
// keyboard-reachability requirement applying to primary operations only.
export function Minimap({ cards, islands, camera, storageScope, onPan }: MinimapProps) {
  const [isCollapsed, setIsCollapsed] = useState(() => loadMinimapCollapsed(storageScope));
  const [isAutoHidden, setIsAutoHidden] = useState(false);
  const toggleButtonRef = useRef<HTMLButtonElement>(null);

  const setCollapsedAndRestoreFocus = (collapsed: boolean) => {
    setIsCollapsed(collapsed);
    saveMinimapCollapsed(collapsed, storageScope);
    window.requestAnimationFrame(() => {
      toggleButtonRef.current?.focus({ preventScroll: true });
    });
  };

  useEffect(() => {
    setIsCollapsed(loadMinimapCollapsed(storageScope));
  }, [storageScope?.deployment, storageScope?.principalId, storageScope?.tenantId]);

  useEffect(() => {
    const updateAutoHidden = () => {
      setIsAutoHidden(window.innerWidth < AUTO_COLLAPSE_WIDTH_PX);
    };
    updateAutoHidden();
    window.addEventListener("resize", updateAutoHidden);
    return () => window.removeEventListener("resize", updateAutoHidden);
  }, []);

  const cardsById = useMemo(() => new Map(cards.map((card) => [card.id, card])), [cards]);

  const worldBounds = useMemo(() => {
    let minX = Infinity;
    let minY = Infinity;
    let maxX = -Infinity;
    let maxY = -Infinity;
    const include = (x: number, y: number) => {
      minX = Math.min(minX, x);
      minY = Math.min(minY, y);
      maxX = Math.max(maxX, x);
      maxY = Math.max(maxY, y);
    };

    for (const card of cards) {
      const bounds = getCardWorldBounds(card);
      include(bounds.x, bounds.y);
      include(bounds.x + bounds.w, bounds.y + bounds.h);
    }
    for (const island of islands) {
      const bounds = getIslandWorldBounds(island, cardsById);
      if (bounds) {
        include(bounds.x, bounds.y);
        include(bounds.x + bounds.w, bounds.y + bounds.h);
      }
    }
    if (camera) {
      // Always include the current viewport so panning far from content
      // doesn't clip the view frame off the minimap entirely.
      const topLeft = screenToWorld({ x: 0, y: 0 }, camera);
      const bottomRight = screenToWorld({ x: camera.viewportWidth, y: camera.viewportHeight }, camera);
      include(topLeft.x, topLeft.y);
      include(bottomRight.x, bottomRight.y);
    }

    if (!Number.isFinite(minX)) {
      return null;
    }

    return {
      x: minX - MINIMAP_PADDING_WORLD,
      y: minY - MINIMAP_PADDING_WORLD,
      w: Math.max(1, maxX - minX + MINIMAP_PADDING_WORLD * 2),
      h: Math.max(1, maxY - minY + MINIMAP_PADDING_WORLD * 2),
    };
  }, [cards, islands, cardsById, camera]);

  const scale = worldBounds ? Math.min(MINIMAP_WIDTH / worldBounds.w, MINIMAP_HEIGHT / worldBounds.h) : 1;
  const offsetX = worldBounds ? (MINIMAP_WIDTH - worldBounds.w * scale) / 2 : 0;
  const offsetY = worldBounds ? (MINIMAP_HEIGHT - worldBounds.h * scale) / 2 : 0;

  const toMinimapPoint = (worldX: number, worldY: number) => {
    if (!worldBounds) {
      return { x: 0, y: 0 };
    }
    return {
      x: (worldX - worldBounds.x) * scale + offsetX,
      y: (worldY - worldBounds.y) * scale + offsetY,
    };
  };

  const viewportRect = useMemo(() => {
    if (!camera || !worldBounds) {
      return null;
    }
    // Defined inside useMemo so its closure over scale/offsetX/offsetY/worldBounds
    // is captured by the deps array rather than via an external function reference.
    const toPoint = (worldX: number, worldY: number) => {
      return {
        x: (worldX - worldBounds.x) * scale + offsetX,
        y: (worldY - worldBounds.y) * scale + offsetY,
      };
    };
    const topLeft = screenToWorld({ x: 0, y: 0 }, camera);
    const bottomRight = screenToWorld({ x: camera.viewportWidth, y: camera.viewportHeight }, camera);
    const p1 = toPoint(topLeft.x, topLeft.y);
    const p2 = toPoint(bottomRight.x, bottomRight.y);
    return { x: p1.x, y: p1.y, w: p2.x - p1.x, h: p2.y - p1.y };
  }, [camera, worldBounds, scale, offsetX, offsetY]);

  const panToMinimapPoint = (minimapX: number, minimapY: number) => {
    if (!camera || !worldBounds || scale <= 0) {
      return;
    }
    const targetWorldX = worldBounds.x + (minimapX - offsetX) / scale;
    const targetWorldY = worldBounds.y + (minimapY - offsetY) / scale;
    const nextPanX = camera.viewportWidth / 2 - targetWorldX * camera.zoom;
    const nextPanY = camera.viewportHeight / 2 - targetWorldY * camera.zoom;
    onPan(nextPanX, nextPanY);
  };

  const handlePointerDown = (event: ReactPointerEvent<SVGSVGElement>) => {
    event.currentTarget.setPointerCapture(event.pointerId);
    const rect = event.currentTarget.getBoundingClientRect();
    panToMinimapPoint(event.clientX - rect.left, event.clientY - rect.top);
  };
  const handlePointerMove = (event: ReactPointerEvent<SVGSVGElement>) => {
    if (event.buttons !== 1) {
      return;
    }
    const rect = event.currentTarget.getBoundingClientRect();
    panToMinimapPoint(event.clientX - rect.left, event.clientY - rect.top);
  };
  const handlePointerUp = (event: ReactPointerEvent<SVGSVGElement>) => {
    event.currentTarget.releasePointerCapture(event.pointerId);
  };

  if (cards.length === 0 && islands.length === 0) {
    return null;
  }

  if (isAutoHidden || isCollapsed) {
    return (
      <button
        ref={toggleButtonRef}
        type="button"
        data-ui-region="minimap-collapsed-trigger"
        onClick={() => setCollapsedAndRestoreFocus(false)}
        aria-label={t("minimap.expand")}
        title={t("minimap.expand")}
        style={{
          position: "absolute",
          right: 16,
          bottom: 16,
          width: 32,
          height: 32,
          borderRadius: 8,
          border: "1px solid #cbd5e1",
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          color: "#0f172a",
          cursor: "pointer",
          fontSize: 14,
          boxShadow: "0 2px 8px rgba(15, 23, 42, 0.15)",
        }}
      >
        ▤
      </button>
    );
  }

  return (
    <div
      data-ui-region="minimap"
      style={{
        position: "absolute",
        right: 16,
        bottom: 16,
        width: MINIMAP_WIDTH,
        height: MINIMAP_HEIGHT,
        borderRadius: 8,
        overflow: "hidden",
        backgroundColor: "rgba(248, 250, 252, 0.85)",
        border: "1px solid #cbd5e1",
        boxShadow: "0 2px 8px rgba(15, 23, 42, 0.15)",
      }}
    >
      <button
        ref={toggleButtonRef}
        type="button"
        onClick={() => setCollapsedAndRestoreFocus(true)}
        aria-label={t("minimap.collapse")}
        title={t("minimap.collapse")}
        style={{
          position: "absolute",
          top: 2,
          right: 2,
          zIndex: 1,
          width: 16,
          height: 16,
          lineHeight: "14px",
          fontSize: 10,
          border: "none",
          borderRadius: 4,
          backgroundColor: "rgba(255, 255, 255, 0.7)",
          color: "#64748b",
          cursor: "pointer",
          padding: 0,
        }}
      >
        ×
      </button>
      <svg
        role="img"
        aria-label={t("minimap.aria_label")}
        width={MINIMAP_WIDTH}
        height={MINIMAP_HEIGHT}
        tabIndex={-1}
        style={{ display: "block", cursor: "pointer" }}
        onPointerDown={handlePointerDown}
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
      >
        {islands.map((island) => {
          const bounds = getIslandWorldBounds(island, cardsById);
          if (!bounds) {
            return null;
          }
          const topLeft = toMinimapPoint(bounds.x, bounds.y);
          return (
            <rect
              key={island.id}
              x={topLeft.x}
              y={topLeft.y}
              width={bounds.w * scale}
              height={bounds.h * scale}
              rx={2}
              fill="none"
              stroke="#94a3b8"
              strokeOpacity={0.5}
              strokeWidth={1}
            />
          );
        })}
        {cards.map((card) => {
          const center = toMinimapPoint(card.x + CARD_WIDTH / 2, card.y + CARD_HEIGHT / 2);
          return (
            <circle
              key={card.id}
              cx={center.x}
              cy={center.y}
              r={2}
              fill={CLAIM_TYPE_DOT_COLOR[card.claimType ?? "unknown"] ?? CLAIM_TYPE_DOT_COLOR.unknown}
            />
          );
        })}
        {viewportRect ? (
          <rect
            data-testid="minimap-viewport-rect"
            x={viewportRect.x}
            y={viewportRect.y}
            width={Math.max(1, viewportRect.w)}
            height={Math.max(1, viewportRect.h)}
            fill="rgba(37, 99, 235, 0.08)"
            stroke="#2563eb"
            strokeWidth={2}
          />
        ) : null}
      </svg>
    </div>
  );
}
