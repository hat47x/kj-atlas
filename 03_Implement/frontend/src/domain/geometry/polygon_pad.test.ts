import { describe, expect, it } from "vitest";

import { padPolygonFromCentroid } from "./polygon_pad";

describe("padPolygonFromCentroid", () => {
  it("returns original reference when polygon is invalid or padding is non-positive", () => {
    const segment = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
    ];

    expect(padPolygonFromCentroid(segment, 8)).toBe(segment);

    const triangle = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 0, y: 10 },
    ];
    expect(padPolygonFromCentroid(triangle, 0)).toBe(triangle);
  });

  it("expands each vertex by the requested padding distance", () => {
    const polygon = [
      { x: 0, y: 0 },
      { x: 6, y: 0 },
      { x: 6, y: 6 },
      { x: 0, y: 6 },
    ];

    const padded = padPolygonFromCentroid(polygon, 2);

    const centroid = { x: 3, y: 3 };
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
      { x: 0, y: 0 },
      { x: 4, y: 1 },
      { x: 6, y: 5 },
      { x: 1, y: 7 },
    ];

    const first = padPolygonFromCentroid(polygon, 3);
    const second = padPolygonFromCentroid(polygon, 3);

    expect(second).toEqual(first);
  });
});
