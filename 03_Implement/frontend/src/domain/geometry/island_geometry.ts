import type { Island, Point } from "../types";

export function getIslandPolygonPoints(island: Island): Point[] {
  const geometryPolygon = island.geometry?.type === "polygon" ? island.geometry.polygon?.points ?? [] : [];
  if (geometryPolygon.length >= 3) {
    return geometryPolygon;
  }

  const shapePolygon = island.shape?.kind === "polygon" ? island.shape.points ?? [] : [];
  if (shapePolygon.length >= 3) {
    return shapePolygon;
  }

  return [];
}
