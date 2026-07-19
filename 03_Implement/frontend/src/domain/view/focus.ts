import type { Transform } from "../types";
import type { BoundsRect } from "../geometry/bounds";
import type { LODThresholds } from "./lod";

const DEFAULT_PADDING = 48;
const FOCUS_HISTORY_LIMIT = 20;
export const FOCUS_LOD_EPSILON = 0.01;

export type FocusSnapshot = {
  camera: Transform;
  viewState?: {
    focusIslandId?: string;
    maxDepth?: number | "all";
  };
};

export type ViewportSize = {
  width: number;
  height: number;
};

export type FocusEntityRef = {
  kind: "island" | "card";
  idOrSignature: string;
};

export function pickPrimaryFocusRef(refs: FocusEntityRef[]): FocusEntityRef | null {
  const islandRef = refs.find((ref) => ref.kind === "island");
  if (islandRef) {
    return islandRef;
  }

  const cardRef = refs.find((ref) => ref.kind === "card");
  return cardRef ?? null;
}

export function zoomTo(camera: Transform, zoom: number): Transform {
  return {
    ...camera,
    zoom,
  };
}

export function fitToBounds(
  bounds: BoundsRect,
  viewportSize: ViewportSize,
  padding = DEFAULT_PADDING,
  zoomLimit: { min: number; max: number } = { min: 0.2, max: 4 }
): Transform {
  const safeWidth = Math.max(1, bounds.w);
  const safeHeight = Math.max(1, bounds.h);
  const availableWidth = Math.max(1, viewportSize.width - padding * 2);
  const availableHeight = Math.max(1, viewportSize.height - padding * 2);
  const fitZoom = Math.min(availableWidth / safeWidth, availableHeight / safeHeight);
  const zoom = Math.min(zoomLimit.max, Math.max(zoomLimit.min, fitZoom));
  const centerX = bounds.x + safeWidth / 2;
  const centerY = bounds.y + safeHeight / 2;

  return {
    panX: viewportSize.width / 2 - centerX * zoom,
    panY: viewportSize.height / 2 - centerY * zoom,
    zoom,
  };
}

export function applyIslandLodZoom(
  camera: Transform,
  lodEnabled: boolean,
  lodThresholds: LODThresholds,
  maxZoom: number
): Transform {
  if (!lodEnabled) {
    return camera;
  }

  const targetZoom = Math.min(maxZoom, Math.max(camera.zoom, lodThresholds.close + FOCUS_LOD_EPSILON));
  if (targetZoom === camera.zoom) {
    return camera;
  }

  return zoomTo(camera, targetZoom);
}

export function enforceMinZoomForBounds(
  bounds: BoundsRect,
  viewportSize: ViewportSize,
  desiredMinZoom: number,
  padding = DEFAULT_PADDING,
  zoomLimit: { min: number; max: number } = { min: 0.2, max: 4 }
): Transform {
  const minZoom = Math.min(zoomLimit.max, Math.max(zoomLimit.min, desiredMinZoom));
  return fitToBounds(bounds, viewportSize, padding, {
    min: minZoom,
    max: zoomLimit.max,
  });
}

export function pushFocusHistory(history: FocusSnapshot[], snapshot: FocusSnapshot): FocusSnapshot[] {
  const next = [...history, snapshot];
  if (next.length <= FOCUS_HISTORY_LIMIT) {
    return next;
  }

  return next.slice(next.length - FOCUS_HISTORY_LIMIT);
}

export function popFocusHistory(history: FocusSnapshot[]): { nextHistory: FocusSnapshot[]; snapshot: FocusSnapshot | null } {
  if (history.length === 0) {
    return {
      nextHistory: history,
      snapshot: null,
    };
  }

  const snapshot = history[history.length - 1];
  return {
    nextHistory: history.slice(0, -1),
    snapshot,
  };
}
