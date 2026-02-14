import type { Point } from "../types";

export function padPolygonFromCentroid(points: Point[], padding: number): Point[] {
  if (points.length < 3 || padding <= 0) {
    return points;
  }

  const centroid = points.reduce(
    (accumulator, point) => ({
      x: accumulator.x + point.x / points.length,
      y: accumulator.y + point.y / points.length,
    }),
    { x: 0, y: 0 }
  );

  return points.map((point) => {
    const dx = point.x - centroid.x;
    const dy = point.y - centroid.y;
    const distance = Math.hypot(dx, dy);
    if (distance < 1e-6) {
      return point;
    }

    const scale = (distance + padding) / distance;
    return {
      x: centroid.x + dx * scale,
      y: centroid.y + dy * scale,
    };
  });
}
