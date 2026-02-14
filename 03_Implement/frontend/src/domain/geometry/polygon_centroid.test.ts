import { describe, expect, it } from "vitest";

import { polygonCentroid } from "./polygon_centroid";

describe("polygonCentroid", () => {
  it("returns centroid for a convex polygon", () => {
    const centroid = polygonCentroid([
      { x: 0, y: 0 },
      { x: 4, y: 0 },
      { x: 4, y: 4 },
      { x: 0, y: 4 },
    ]);

    expect(centroid).toEqual({ x: 2, y: 2 });
  });

  it("falls back to average when polygon area is degenerate", () => {
    const centroid = polygonCentroid([
      { x: 0, y: 0 },
      { x: 2, y: 0 },
      { x: 4, y: 0 },
    ]);

    expect(centroid).toEqual({ x: 2, y: 0 });
  });
});
