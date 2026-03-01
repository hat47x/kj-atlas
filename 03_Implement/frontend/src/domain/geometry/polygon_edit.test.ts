import { describe, expect, it } from "vitest";

import {
  addPolygonVertex,
  canUsePolygonPoints,
  MIN_POLYGON_VERTEX_COUNT,
  movePolygonVertex,
  removePolygonVertex,
  roundPoint,
} from "./polygon_edit";

describe("polygon_edit", () => {
  it("rounds points with fixed precision", () => {
    expect(roundPoint({ x: 12.34567, y: 89.99123 })).toEqual({ x: 12.35, y: 89.99 });
  });

  it("blocks self-intersection on vertex move", () => {
    const result = movePolygonVertex(
      [
        { x: 0, y: 0 },
        { x: 8, y: 0 },
        { x: 8, y: 8 },
        { x: 0, y: 8 },
      ],
      1,
      { x: -2, y: 6 }
    );

    expect(result).toEqual({ ok: false, error: "self_intersection" });
  });

  it("keeps minimum vertex count when removing", () => {
    const triangle = [
      { x: 0, y: 0 },
      { x: 8, y: 0 },
      { x: 4, y: 8 },
    ];

    const result = removePolygonVertex(triangle, 1);

    expect(MIN_POLYGON_VERTEX_COUNT).toBe(3);
    expect(result).toEqual({ ok: false, error: "min_vertex_count" });
  });

  it("reuses shared validator for add operations", () => {
    const result = addPolygonVertex(
      [
        { x: 0, y: 0 },
        { x: 8, y: 0 },
        { x: 8, y: 8 },
        { x: 0, y: 8 },
      ],
      2,
      { x: 4, y: -2 }
    );

    expect(result).toEqual({ ok: false, error: "self_intersection" });
    expect(
      canUsePolygonPoints([
        { x: 0, y: 0 },
        { x: 8, y: 0 },
        { x: 8, y: 8 },
      ])
    ).toBe(true);
  });
});
