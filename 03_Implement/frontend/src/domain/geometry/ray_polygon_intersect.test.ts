import { describe, expect, it } from "vitest";

import { rayPolygonBoundaryIntersection } from "./ray_polygon_intersect";

describe("rayPolygonBoundaryIntersection", () => {
  it("finds boundary intersection on convex polygon", () => {
    const point = rayPolygonBoundaryIntersection(
      { x: 2, y: 2 },
      { x: 10, y: 2 },
      [
        { x: 0, y: 0 },
        { x: 4, y: 0 },
        { x: 4, y: 4 },
        { x: 0, y: 4 },
      ]
    );

    expect(point).toEqual({ x: 4, y: 2 });
  });

  it("finds nearest forward intersection on non-convex polygon", () => {
    const point = rayPolygonBoundaryIntersection(
      { x: 1.5, y: 2 },
      { x: 10, y: 2 },
      [
        { x: 0, y: 0 },
        { x: 4, y: 0 },
        { x: 4, y: 4 },
        { x: 2, y: 4 },
        { x: 2, y: 1 },
        { x: 0, y: 1 },
      ]
    );

    expect(point).toEqual({ x: 2, y: 2 });
  });

  it("handles collinear overlap with a polygon edge", () => {
    const point = rayPolygonBoundaryIntersection(
      { x: 0, y: 2 },
      { x: 10, y: 2 },
      [
        { x: 2, y: 2 },
        { x: 5, y: 2 },
        { x: 5, y: 4 },
        { x: 2, y: 4 },
      ]
    );

    expect(point).toEqual({ x: 2, y: 2 });
  });
});
