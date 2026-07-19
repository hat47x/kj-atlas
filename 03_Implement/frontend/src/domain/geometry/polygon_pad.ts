import type { Point } from "../types";
import { P2C_DETERMINISTIC_TIE_BREAK_ORDER, type P2CTieBreakKey } from "../merge/p2c_tie_break_contract";
import { isSelfIntersectingPolygon } from "./polygon_self_intersection";

const PADDING_EPSILON = 1e-6;
const TIE_BREAK_EPSILON = 1e-6;

export const POLYGON_TIE_BREAK_SCHEMA_VERSION = "1.0.0" as const;
export const POLYGON_TIE_BREAK_ORDER = P2C_DETERMINISTIC_TIE_BREAK_ORDER;

type PolygonCandidate = {
  points: Point[];
  score: Record<P2CTieBreakKey, number>;
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
  for (const key of POLYGON_TIE_BREAK_ORDER) {
    const delta = a.score[key] - b.score[key];
    if (Math.abs(delta) > TIE_BREAK_EPSILON) {
      return delta;
    }
  }

  const serializedA = JSON.stringify(a.points);
  const serializedB = JSON.stringify(b.points);
  return serializedA.localeCompare(serializedB);
}

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
    score: {
      padding_compliance: countPaddingViolations(points, candidatePoints, centroid, padding),
      self_intersection_avoidance: Number(isSelfIntersectingPolygon(candidatePoints)),
      area_delta_minimization: Math.abs(polygonArea(candidatePoints) - baseArea),
      vertex_count_minimization: candidatePoints.length,
    },
  }));

  const selected = selectPolygonCandidateByTieBreak(candidates);
  return selected.points;
}
