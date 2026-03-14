import { describe, expect, it } from "vitest";

import {
  padPolygonFromCentroid,
  POLYGON_TIE_BREAK_ORDER,
  POLYGON_TIE_BREAK_SCHEMA_VERSION,
  selectPolygonCandidateByTieBreak,
} from "./polygon_pad";

describe("padPolygonFromCentroid", () => {
  it("returns original reference when polygon is invalid or padding is non-positive", () => {
    const degenerate = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
    ];

    expect(padPolygonFromCentroid(degenerate, 4)).toBe(degenerate);
    expect(padPolygonFromCentroid(degenerate, 0)).toBe(degenerate);
  });

  it("expands each vertex by the requested padding distance", () => {
    const polygon = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 10 },
      { x: 0, y: 10 },
    ];

    const padded = padPolygonFromCentroid(polygon, 2);
    const centroid = { x: 5, y: 5 };

    for (let index = 0; index < polygon.length; index += 1) {
      const before = polygon[index]!;
      const after = padded[index]!;
      const beforeDistance = Math.hypot(before.x - centroid.x, before.y - centroid.y);
      const afterDistance = Math.hypot(after.x - centroid.x, after.y - centroid.y);
      expect(afterDistance - beforeDistance).toBeCloseTo(2, 6);
    }
  });

  it("is deterministic for identical input", () => {
    const polygon = [
      { x: 2, y: 2 },
      { x: 18, y: 1 },
      { x: 20, y: 14 },
      { x: 8, y: 22 },
      { x: 1, y: 11 },
    ];

    const first = padPolygonFromCentroid(polygon, 3);
    const second = padPolygonFromCentroid(polygon, 3);

    expect(second).toEqual(first);
  });

  it("keeps padding-first tie-break priority over area minimization", () => {
    const polygon = [
      { x: 0, y: 0 },
      { x: 20, y: 0 },
      { x: 20, y: 20 },
      { x: 0, y: 20 },
    ];

    const padded = padPolygonFromCentroid(polygon, 4);

    expect(padded).not.toEqual(polygon);
  });

  it("publishes fixed tie-break contract metadata", () => {
    expect(POLYGON_TIE_BREAK_SCHEMA_VERSION).toBe("1.0.0");
    expect(POLYGON_TIE_BREAK_ORDER).toEqual([
      "padding_compliance",
      "self_intersection_avoidance",
      "area_delta_minimization",
      "vertex_count_minimization",
    ]);
  });

  it("selectPolygonCandidateByTieBreak fails fast when candidates are empty", () => {
    expect(() => selectPolygonCandidateByTieBreak([])).toThrow("candidates must contain at least one polygon");
  });
});
