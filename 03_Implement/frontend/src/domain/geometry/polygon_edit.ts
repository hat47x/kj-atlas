import type { Point } from "../types";
import { isSelfIntersectingPolygon } from "./polygon_self_intersection";

export const MIN_POLYGON_VERTEX_COUNT = 3;
const COORDINATE_PRECISION_FACTOR = 100;

export type PolygonEditError = "vertex_out_of_range" | "min_vertex_count" | "self_intersection";

export type PolygonEditResult =
  | {
      ok: true;
      points: Point[];
    }
  | {
      ok: false;
      error: PolygonEditError;
    };

function roundCoordinate(value: number): number {
  return Math.round(value * COORDINATE_PRECISION_FACTOR) / COORDINATE_PRECISION_FACTOR;
}

export function roundPoint(point: Point): Point {
  return {
    x: roundCoordinate(point.x),
    y: roundCoordinate(point.y),
  };
}

function validatePolygonPoints(points: Point[]): PolygonEditResult {
  if (points.length < MIN_POLYGON_VERTEX_COUNT) {
    return { ok: false, error: "min_vertex_count" };
  }

  if (isSelfIntersectingPolygon(points)) {
    return { ok: false, error: "self_intersection" };
  }

  return { ok: true, points };
}

export function canUsePolygonPoints(points: Point[]): boolean {
  return validatePolygonPoints(points).ok;
}

export function movePolygonVertex(points: Point[], vertexIndex: number, point: Point): PolygonEditResult {
  if (vertexIndex < 0 || vertexIndex >= points.length) {
    return { ok: false, error: "vertex_out_of_range" };
  }

  const nextPoint = roundPoint(point);
  const nextPoints = points.map((targetPoint, index) => {
    if (index === vertexIndex) {
      return nextPoint;
    }

    return roundPoint(targetPoint);
  });

  return validatePolygonPoints(nextPoints);
}

export function addPolygonVertex(points: Point[], segmentStartIndex: number, point: Point): PolygonEditResult {
  if (segmentStartIndex < 0 || segmentStartIndex >= points.length) {
    return { ok: false, error: "vertex_out_of_range" };
  }

  const nextPoints = points.map(roundPoint);
  nextPoints.splice(segmentStartIndex + 1, 0, roundPoint(point));

  return validatePolygonPoints(nextPoints);
}

export function removePolygonVertex(points: Point[], vertexIndex: number): PolygonEditResult {
  if (vertexIndex < 0 || vertexIndex >= points.length) {
    return { ok: false, error: "vertex_out_of_range" };
  }

  if (points.length <= MIN_POLYGON_VERTEX_COUNT) {
    return { ok: false, error: "min_vertex_count" };
  }

  const nextPoints = points.map(roundPoint).filter((_, index) => index !== vertexIndex);
  return validatePolygonPoints(nextPoints);
}
