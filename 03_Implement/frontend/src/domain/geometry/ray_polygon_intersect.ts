import type { Point } from "../types";

const EPSILON = 1e-9;

function cross(a: Point, b: Point): number {
  return a.x * b.y - a.y * b.x;
}

function dot(a: Point, b: Point): number {
  return a.x * b.x + a.y * b.y;
}

function subtract(a: Point, b: Point): Point {
  return {
    x: a.x - b.x,
    y: a.y - b.y,
  };
}

export function rayPolygonBoundaryIntersection(origin: Point, target: Point, polygonPoints: Point[]): Point | null {
  if (polygonPoints.length < 3) {
    return null;
  }

  const rayDirection = subtract(target, origin);
  const rayLengthSquared = rayDirection.x * rayDirection.x + rayDirection.y * rayDirection.y;
  if (rayLengthSquared <= EPSILON) {
    return null;
  }

  let nearestT: number | null = null;
  let nearestPoint: Point | null = null;

  for (let index = 0; index < polygonPoints.length; index += 1) {
    const segmentStart = polygonPoints[index];
    const segmentEnd = polygonPoints[(index + 1) % polygonPoints.length];
    const segmentDirection = subtract(segmentEnd, segmentStart);
    const originToSegmentStart = subtract(segmentStart, origin);

    const denominator = cross(rayDirection, segmentDirection);
    if (Math.abs(denominator) <= EPSILON) {
      if (Math.abs(cross(originToSegmentStart, rayDirection)) > EPSILON) {
        continue;
      }

      const startT = dot(originToSegmentStart, rayDirection) / rayLengthSquared;
      const endT = dot(subtract(segmentEnd, origin), rayDirection) / rayLengthSquared;
      const minT = Math.min(startT, endT);
      const maxT = Math.max(startT, endT);

      if (maxT <= EPSILON) {
        continue;
      }

      const rayT = minT > EPSILON ? minT : maxT;
      if (rayT <= EPSILON) {
        continue;
      }

      if (nearestT === null || rayT < nearestT) {
        nearestT = rayT;
        nearestPoint = {
          x: origin.x + rayDirection.x * rayT,
          y: origin.y + rayDirection.y * rayT,
        };
      }
      continue;
    }

    const rayT = cross(originToSegmentStart, segmentDirection) / denominator;
    const segmentT = cross(originToSegmentStart, rayDirection) / denominator;

    if (rayT <= EPSILON || segmentT < -EPSILON || segmentT > 1 + EPSILON) {
      continue;
    }

    if (nearestT === null || rayT < nearestT) {
      nearestT = rayT;
      nearestPoint = {
        x: origin.x + rayDirection.x * rayT,
        y: origin.y + rayDirection.y * rayT,
      };
    }
  }

  return nearestPoint;
}
