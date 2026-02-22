import type { Point } from "../types";

export type PolygonBoundsRect = {
  x: number;
  y: number;
  w: number;
  h: number;
};

export function getPolygonBoundingBox(points: Point[]): PolygonBoundsRect | null {
  if (points.length < 3) {
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
    x: minX,
    y: minY,
    w: Math.max(1, maxX - minX),
    h: Math.max(1, maxY - minY),
  };
}
