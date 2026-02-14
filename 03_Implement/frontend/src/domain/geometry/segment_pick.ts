import type { Point } from "../types";

function squaredDistanceToSegment(point: Point, segmentStart: Point, segmentEnd: Point): number {
  const dx = segmentEnd.x - segmentStart.x;
  const dy = segmentEnd.y - segmentStart.y;

  if (dx === 0 && dy === 0) {
    const singleDx = point.x - segmentStart.x;
    const singleDy = point.y - segmentStart.y;
    return singleDx * singleDx + singleDy * singleDy;
  }

  const t = Math.max(
    0,
    Math.min(1, ((point.x - segmentStart.x) * dx + (point.y - segmentStart.y) * dy) / (dx * dx + dy * dy))
  );
  const projectionX = segmentStart.x + t * dx;
  const projectionY = segmentStart.y + t * dy;
  const diffX = point.x - projectionX;
  const diffY = point.y - projectionY;

  return diffX * diffX + diffY * diffY;
}

export function findNearestPolygonSegmentIndex(points: Point[], point: Point, threshold: number): number | null {
  if (points.length < 2) {
    return null;
  }

  const thresholdSquared = threshold * threshold;
  let nearestIndex: number | null = null;
  let nearestDistance = Number.POSITIVE_INFINITY;

  for (let index = 0; index < points.length; index += 1) {
    const start = points[index];
    const end = points[(index + 1) % points.length];
    const distance = squaredDistanceToSegment(point, start, end);

    if (distance > thresholdSquared || distance >= nearestDistance) {
      continue;
    }

    nearestDistance = distance;
    nearestIndex = index;
  }

  return nearestIndex;
}
