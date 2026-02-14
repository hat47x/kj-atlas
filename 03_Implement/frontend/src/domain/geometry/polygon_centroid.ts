import type { Point } from "../types";

const EPSILON = 1e-9;

export function polygonCentroid(points: Point[]): Point | null {
  if (points.length < 3) {
    return null;
  }

  let signedDoubleArea = 0;
  let centroidX = 0;
  let centroidY = 0;

  for (let index = 0; index < points.length; index += 1) {
    const current = points[index];
    const next = points[(index + 1) % points.length];
    const cross = current.x * next.y - next.x * current.y;

    signedDoubleArea += cross;
    centroidX += (current.x + next.x) * cross;
    centroidY += (current.y + next.y) * cross;
  }

  if (Math.abs(signedDoubleArea) <= EPSILON) {
    let averageX = 0;
    let averageY = 0;

    for (const point of points) {
      averageX += point.x;
      averageY += point.y;
    }

    return {
      x: averageX / points.length,
      y: averageY / points.length,
    };
  }

  return {
    x: centroidX / (3 * signedDoubleArea),
    y: centroidY / (3 * signedDoubleArea),
  };
}
