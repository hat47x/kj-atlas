import { describe, expect, it } from "vitest";

import { getPolygonBoundingBox } from "./polygon_bbox";

describe("getPolygonBoundingBox", () => {
  it("returns bounding box for a polygon", () => {
    expect(
      getPolygonBoundingBox([
        { x: 10, y: 20 },
        { x: 30, y: 15 },
        { x: 25, y: 50 },
      ])
    ).toEqual({ x: 10, y: 15, w: 20, h: 35 });
  });

  it("returns null when polygon has fewer than 3 points", () => {
    expect(
      getPolygonBoundingBox([
        { x: 10, y: 20 },
        { x: 30, y: 15 },
      ])
    ).toBeNull();
  });
});
