import { describe, expect, it } from "vitest";

import { padPolygonFromCentroid } from "./geometry/polygon_pad";

describe("FB-P2C-01 A2 mock validation (Stream D)", () => {
  const fixture = [
    { x: 90, y: 80 },
    { x: 250, y: 72 },
    { x: 318, y: 156 },
    { x: 282, y: 248 },
    { x: 154, y: 290 },
    { x: 78, y: 188 },
  ];

  it("keeps deterministic outputPolygonHash for identical input", () => {
    const first = JSON.stringify(padPolygonFromCentroid(fixture, 24));
    const second = JSON.stringify(padPolygonFromCentroid(fixture, 24));
    expect(second).toBe(first);
  });

  it("satisfies padding-first rule with zero padding violations", () => {
    const centroid = fixture.reduce(
      (acc, point) => ({ x: acc.x + point.x / fixture.length, y: acc.y + point.y / fixture.length }),
      { x: 0, y: 0 }
    );

    const padded = padPolygonFromCentroid(fixture, 24);
    const violations = fixture.reduce((count, before, index) => {
      const after = padded[index]!;
      const beforeDistance = Math.hypot(before.x - centroid.x, before.y - centroid.y);
      const afterDistance = Math.hypot(after.x - centroid.x, after.y - centroid.y);
      return afterDistance - beforeDistance < 24 - 1e-6 ? count + 1 : count;
    }, 0);

    expect(violations).toBe(0);
  });
});
