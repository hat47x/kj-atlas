import { describe, expect, test } from "vitest";
import type { Island } from "../types";
import { getIslandPolygonPoints } from "./island_geometry";

function island(overrides: Partial<Island> = {}): Island {
  return { id: "i1", cardIds: ["c1"], ...overrides };
}

describe("getIslandPolygonPoints", () => {
  test("returns geometry polygon points when present with 3+ points", () => {
    const points = [
      { x: 0, y: 0 },
      { x: 10, y: 0 },
      { x: 5, y: 10 },
    ];
    const result = getIslandPolygonPoints(
      island({ geometry: { type: "polygon", points } }),
    );
    expect(result).toEqual(points);
  });

  test("falls back to shape polygon when geometry is missing", () => {
    const points = [
      { x: 1, y: 1 },
      { x: 5, y: 1 },
      { x: 3, y: 6 },
    ];
    const result = getIslandPolygonPoints(
      island({ shape: { kind: "polygon", points } }),
    );
    expect(result).toEqual(points);
  });

  test("prefers geometry polygon over shape polygon", () => {
    const geometryPoints = [
      { x: 0, y: 0 },
      { x: 4, y: 0 },
      { x: 2, y: 4 },
    ];
    const shapePoints = [
      { x: 10, y: 10 },
      { x: 14, y: 10 },
      { x: 12, y: 14 },
    ];
    const result = getIslandPolygonPoints(
      island({
        geometry: { type: "polygon", points: geometryPoints },
        shape: { kind: "polygon", points: shapePoints },
      }),
    );
    expect(result).toEqual(geometryPoints);
  });

  test("returns [] when geometry polygon has fewer than 3 points", () => {
    const result = getIslandPolygonPoints(
      island({
        geometry: { type: "polygon", points: [{ x: 0, y: 0 }, { x: 1, y: 1 }] },
      }),
    );
    expect(result).toEqual([]);
  });

  test("returns [] when neither geometry nor shape has a polygon", () => {
    const result = getIslandPolygonPoints(island());
    expect(result).toEqual([]);
  });
});
