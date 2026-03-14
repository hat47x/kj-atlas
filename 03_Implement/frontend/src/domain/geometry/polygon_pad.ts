import type { Point } from "../types";
import { isSelfIntersectingPolygon } from "./polygon_self_intersection";

const PADDING_EPSILON = 1e-6;
const TIE_BREAK_EPSILON = 1e-6;

export const POLYGON_TIE_BREAK_SCHEMA_VERSION = "1.0.0" as const;
export const POLYGON_TIE_BREAK_ORDER = [
  "padding_compliance",
  "self_intersection_avoidance",
  "minimum_area_delta",
  "minimum_vertex_count",
] as const;

type PolygonCandidate = {
  points: Point[];
  paddingViolationCount: number;
  selfIntersection: boolean;
  areaDeltaAbs: number;
  vertexCount: number;
};

function polygonArea(points: Point[]): number {
  if (points.length < 3) {
    return 0;
  }

  let signedArea = 0;
  for (let index = 0; index < points.length; index += 1) {
    const current = points[index]!;
    const next = points[(index + 1) % points.length]!;
    signedArea += current.x * next.y - next.x * current.y;
  }

  return Math.abs(signedArea) / 2;
}

function buildCentroid(points: Point[]): Point {
  return points.reduce(
    (accumulator, point) => ({
      x: accumulator.x + point.x / points.length,
      y: accumulator.y + point.y / points.length,
    }),
    { x: 0, y: 0 }
  );
}

function countPaddingViolations(basePoints: Point[], candidatePoints: Point[], centroid: Point, requestedPadding: number): number {
  let violations = 0;
  for (let index = 0; index < basePoints.length; index += 1) {
    const before = basePoints[index]!;
    const after = candidatePoints[index]!;
    const beforeDistance = Math.hypot(before.x - centroid.x, before.y - centroid.y);
    const afterDistance = Math.hypot(after.x - centroid.x, after.y - centroid.y);
    if (afterDistance - beforeDistance + PADDING_EPSILON < requestedPadding) {
      violations += 1;
    }
  }

  return violations;
}

function compareCandidates(a: PolygonCandidate, b: PolygonCandidate): number {
  if (a.paddingViolationCount !== b.paddingViolationCount) {
    return a.paddingViolationCount - b.paddingViolationCount;
  }

  if (a.selfIntersection !== b.selfIntersection) {
    return Number(a.selfIntersection) - Number(b.selfIntersection);
  }

  if (Math.abs(a.areaDeltaAbs - b.areaDeltaAbs) > TIE_BREAK_EPSILON) {
    return a.areaDeltaAbs - b.areaDeltaAbs;
  }

  if (a.vertexCount !== b.vertexCount) {
    return a.vertexCount - b.vertexCount;
  }

  const serializedA = JSON.stringify(a.points);
  const serializedB = JSON.stringify(b.points);
  return serializedA.localeCompare(serializedB);
}

export type PolygonTieBreakMetrics = Omit<PolygonCandidate, "points">;

export function selectPolygonCandidateByTieBreak(candidates: PolygonCandidate[]): PolygonCandidate {
  if (candidates.length === 0) {
    throw new Error("candidates must contain at least one polygon");
  }
  return [...candidates].sort(compareCandidates)[0]!;
}

export function padPolygonFromCentroid(points: Point[], padding: number): Point[] {
  if (points.length < 3 || padding <= 0) {
    return points;
  }

  const centroid = buildCentroid(points);
  const baseArea = polygonArea(points);

  const padded = points.map((point) => {
    const dx = point.x - centroid.x;
    const dy = point.y - centroid.y;
    const distance = Math.hypot(dx, dy);
    if (distance < PADDING_EPSILON) {
      return point;
    }

    const scale = (distance + padding) / distance;
    return {
      x: centroid.x + dx * scale,
      y: centroid.y + dy * scale,
    };
  });

  const candidates: PolygonCandidate[] = [points, padded].map((candidatePoints) => ({
    points: candidatePoints,
    paddingViolationCount: countPaddingViolations(points, candidatePoints, centroid, padding),
    selfIntersection: isSelfIntersectingPolygon(candidatePoints),
    areaDeltaAbs: Math.abs(polygonArea(candidatePoints) - baseArea),
    vertexCount: candidatePoints.length,
  }));

  const selected = selectPolygonCandidateByTieBreak(candidates);
  return selected.points;
}
