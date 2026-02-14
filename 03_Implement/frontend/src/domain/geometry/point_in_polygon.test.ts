import { describe, expect, it } from "vitest";

import { isPointInPolygon } from "./point_in_polygon";

describe("isPointInPolygon", () => {
  const polygon = [
    { x: 0, y: 0 },
    { x: 10, y: 0 },
    { x: 10, y: 10 },
    { x: 0, y: 10 },
  ];

  it("returns true for points strictly inside", () => {
    expect(isPointInPolygon({ x: 5, y: 5 }, polygon)).toBe(true);
  });

  it("returns false for points outside even when aligned with bbox", () => {
    const triangle = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 5, y: 10 },
    ];

    expect(isPointInPolygon({ x: 9, y: 9 }, triangle)).toBe(false);
  });

  it("treats boundary points as inside", () => {
    expect(isPointInPolygon({ x: 0, y: 5 }, polygon)).toBe(true);
    expect(isPointInPolygon({ x: 10, y: 10 }, polygon)).toBe(true);
  });

  it("returns false when polygon has fewer than 3 points", () => {
    expect(
      isPointInPolygon(
        { x: 1, y: 1 },
        [
          { x: 0, y: 0 },
          { x: 10, y: 0 },
        ]
      )
    ).toBe(false);
  });
});
