import { describe, expect, it } from "vitest";

import { computeConvexHull } from "./convex_hull";

describe("computeConvexHull", () => {
  it("returns a rectangle hull from rectangle corners", () => {
    const hull = computeConvexHull([
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 10 },
      { x: 0, y: 10 },
      { x: 5, y: 5 },
    ]);

    expect(hull).toHaveLength(4);
    expect(hull).toEqual([
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 10, y: 10 },
      { x: 0, y: 10 },
    ]);
  });

  it("handles degenerate inputs", () => {
    expect(computeConvexHull([])).toEqual([]);
    expect(computeConvexHull([{ x: 1, y: 2 }])).toEqual([{ x: 1, y: 2 }]);
    expect(computeConvexHull([{ x: 1, y: 2 }, { x: 1, y: 2 }])).toEqual([{ x: 1, y: 2 }]);
  });
});
