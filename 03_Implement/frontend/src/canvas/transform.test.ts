import { describe, expect, it } from "vitest";

import { screenToWorld, worldToScreen } from "./transform";

describe("transform utilities", () => {
  const epsilon = 1e-9;

  it("screenToWorld(worldToScreen(point)) returns original point", () => {
    const transform = { panX: 120.5, panY: -44.25, zoom: 2.75 };
    const worldPoint = { x: -31.125, y: 89.5 };

    const screenPoint = worldToScreen(worldPoint, transform);
    const reconstructed = screenToWorld(screenPoint, transform);

    expect(reconstructed.x).toBeCloseTo(worldPoint.x, 9);
    expect(reconstructed.y).toBeCloseTo(worldPoint.y, 9);
    expect(Math.abs(reconstructed.x - worldPoint.x)).toBeLessThan(epsilon);
    expect(Math.abs(reconstructed.y - worldPoint.y)).toBeLessThan(epsilon);
  });

  it("worldToScreen(screenToWorld(point)) returns original point", () => {
    const transform = { panX: -10, panY: 250, zoom: 0.5 };
    const screenPoint = { x: 401.2, y: -200.8 };

    const worldPoint = screenToWorld(screenPoint, transform);
    const reconstructed = worldToScreen(worldPoint, transform);

    expect(reconstructed.x).toBeCloseTo(screenPoint.x, 9);
    expect(reconstructed.y).toBeCloseTo(screenPoint.y, 9);
    expect(Math.abs(reconstructed.x - screenPoint.x)).toBeLessThan(epsilon);
    expect(Math.abs(reconstructed.y - screenPoint.y)).toBeLessThan(epsilon);
  });
});
