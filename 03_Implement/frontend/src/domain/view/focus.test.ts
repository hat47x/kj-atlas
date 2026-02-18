import { describe, expect, it } from "vitest";

import { getCardWorldBounds, getIslandWorldBounds } from "../geometry/bounds";
import { enforceMinZoomForBounds, fitToBounds, popFocusHistory, pushFocusHistory } from "./focus";

describe("focus view helpers", () => {
  it("fits bounds into viewport with padding", () => {
    const transform = fitToBounds({ x: 100, y: 200, w: 400, h: 200 }, { width: 1000, height: 600 }, 50);
    expect(transform.zoom).toBeCloseTo(2.25);
    expect(transform.panX).toBeCloseTo(-175);
    expect(transform.panY).toBeCloseTo(-375);
  });

  it("pushes and pops focus history", () => {
    const history = pushFocusHistory([], { camera: { panX: 1, panY: 2, zoom: 3 } });
    const { nextHistory, snapshot } = popFocusHistory(history);
    expect(snapshot?.camera.zoom).toBe(3);
    expect(nextHistory).toHaveLength(0);
  });

  it("computes polygon island bounds and card bounds", () => {
    const islandBounds = getIslandWorldBounds(
      {
        id: "i1",
        cardIds: [],
        shape: {
          kind: "polygon",
          points: [
            { x: 10, y: 5 },
            { x: 45, y: 20 },
            { x: 25, y: 60 },
          ],
        },
      },
      new Map()
    );

    expect(islandBounds).toEqual({ x: 10, y: 5, w: 35, h: 55 });
    expect(getCardWorldBounds({ id: "c1", text: "x", x: 2, y: 4 })).toEqual({ x: 2, y: 4, w: 220, h: 80 });
  });

  it("enforces minimum zoom while keeping bounds centered", () => {
    const transform = enforceMinZoomForBounds({ x: 100, y: 120, w: 200, h: 160 }, { width: 800, height: 600 }, 2, 40);
    expect(transform.zoom).toBeGreaterThanOrEqual(2);

    const centerX = 100 + 200 / 2;
    const centerY = 120 + 160 / 2;
    expect(transform.panX).toBeCloseTo(800 / 2 - centerX * transform.zoom);
    expect(transform.panY).toBeCloseTo(600 / 2 - centerY * transform.zoom);
  });
});
