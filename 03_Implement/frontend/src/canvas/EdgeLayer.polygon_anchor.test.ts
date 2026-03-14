import { describe, expect, it } from "vitest";

import type { Island } from "../domain/types";
import { getRenderableIslandPolygonPoints } from "./EdgeLayer";

describe("getRenderableIslandPolygonPoints", () => {
  it("uses geometry polygon when available and keeps deterministic output", () => {
    const island: Island = {
      id: "i-geometry",
      cardIds: ["c1"],
      geometry: {
        type: "polygon",
        points: [
          { x: 10, y: 10 },
          { x: 100, y: 10 },
          { x: 100, y: 80 },
          { x: 10, y: 80 },
        ],
      },
      shape: {
        kind: "polygon",
        points: [
          { x: 0, y: 0 },
          { x: 10, y: 10 },
          { x: 20, y: 0 },
        ],
      },
    };

    const first = JSON.stringify(getRenderableIslandPolygonPoints(island));
    const second = JSON.stringify(getRenderableIslandPolygonPoints(island));

    expect(first).toBe(second);
    expect(first).toContain('"x":100');
    expect(first).not.toContain('"x":20');
  });

  it("falls back to empty polygon for self-intersecting input", () => {
    const island: Island = {
      id: "i-self-intersect",
      cardIds: ["c1"],
      shape: {
        kind: "polygon",
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 100 },
          { x: 100, y: 0 },
          { x: 0, y: 100 },
        ],
      },
    };

    expect(getRenderableIslandPolygonPoints(island)).toEqual([]);
  });
});
