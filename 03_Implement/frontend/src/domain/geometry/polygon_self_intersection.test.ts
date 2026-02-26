import { describe, expect, it } from "vitest";

import { isSelfIntersectingPolygon } from "./polygon_self_intersection";

describe("isSelfIntersectingPolygon", () => {
  it("returns false for a convex polygon", () => {
    expect(
      isSelfIntersectingPolygon([
        { x: 0, y: 0 },
        { x: 100, y: 0 },
        { x: 80, y: 80 },
        { x: 0, y: 100 },
      ])
    ).toBe(false);
  });

  it("returns true for a bow-tie polygon", () => {
    expect(
      isSelfIntersectingPolygon([
        { x: 0, y: 0 },
        { x: 120, y: 120 },
        { x: 120, y: 0 },
        { x: 0, y: 120 },
      ])
    ).toBe(true);
  });
});
