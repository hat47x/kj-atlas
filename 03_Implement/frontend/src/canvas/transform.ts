import type { Transform } from "../domain/types";

export type Point = {
  x: number;
  y: number;
};

function requirePositiveZoom(zoom: number): void {
  if (zoom <= 0) {
    throw new RangeError("zoom must be greater than 0");
  }
}

export function worldToScreen(point: Point, transform: Transform): Point {
  return {
    x: point.x * transform.zoom + transform.panX,
    y: point.y * transform.zoom + transform.panY,
  };
}

export function screenToWorld(point: Point, transform: Transform): Point {
  requirePositiveZoom(transform.zoom);

  return {
    x: (point.x - transform.panX) / transform.zoom,
    y: (point.y - transform.panY) / transform.zoom,
  };
}

export function applyPan(
  transform: Transform,
  deltaScreenX: number,
  deltaScreenY: number
): Transform {
  return {
    ...transform,
    panX: transform.panX + deltaScreenX,
    panY: transform.panY + deltaScreenY,
  };
}

export function applyZoomAtScreenPoint(
  transform: Transform,
  zoomFactor: number,
  screenPoint: Point
): Transform {
  requirePositiveZoom(transform.zoom);
  requirePositiveZoom(zoomFactor);

  const nextZoom = transform.zoom * zoomFactor;
  const anchorWorld = screenToWorld(screenPoint, transform);

  return {
    panX: screenPoint.x - anchorWorld.x * nextZoom,
    panY: screenPoint.y - anchorWorld.y * nextZoom,
    zoom: nextZoom,
  };
}

/*
Sanity check examples:

const t = { panX: 100, panY: 50, zoom: 2 };
worldToScreen({ x: 10, y: 20 }, t); // => { x: 120, y: 90 }
screenToWorld({ x: 120, y: 90 }, t); // => { x: 10, y: 20 }

const panned = applyPan(t, 5, -10); // => panX: 105, panY: 40, zoom: 2

const zoomed = applyZoomAtScreenPoint(t, 1.5, { x: 200, y: 200 });
// The world point under screen (200, 200) stays at the same screen position.
*/
