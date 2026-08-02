import { describe, expect, test } from "vitest";
import { findNearestPolygonSegmentIndex } from "./segment_pick";

const SQUARE = [
  { x: 0, y: 0 },
  { x: 10, y: 0 },
  { x: 10, y: 10 },
  { x: 0, y: 10 },
];

describe("findNearestPolygonSegmentIndex", () => {
  test("returns the nearest segment index within threshold", () => {
    // Point just below the top edge (segment 0: (0,0)-(10,0)).
    const result = findNearestPolygonSegmentIndex(SQUARE, { x: 5, y: 2 }, 3);
    expect(result).toBe(0);
  });

  test("returns the nearest segment index for a point near the right edge", () => {
    // Segment 1: (10,0)-(10,10).
    const result = findNearestPolygonSegmentIndex(SQUARE, { x: 8, y: 5 }, 3);
    expect(result).toBe(1);
  });

  test("wraps around: returns last segment for a point near the closing edge", () => {
    // Segment 3: (0,10)-(0,0).
    const result = findNearestPolygonSegmentIndex(SQUARE, { x: 2, y: 5 }, 3);
    expect(result).toBe(3);
  });

  test("returns null when the point is beyond the threshold from every segment", () => {
    const result = findNearestPolygonSegmentIndex(SQUARE, { x: 50, y: 50 }, 3);
    expect(result).toBeNull();
  });

  test("returns null for fewer than 2 points", () => {
    expect(findNearestPolygonSegmentIndex([{ x: 0, y: 0 }], { x: 5, y: 5 }, 10)).toBeNull();
    expect(findNearestPolygonSegmentIndex([], { x: 5, y: 5 }, 10)).toBeNull();
  });

  test("picks the strictly nearest segment among multiple within threshold", () => {
    // Point near the bottom-left corner (segment 2: (10,10)-(0,10)).
    const result = findNearestPolygonSegmentIndex(SQUARE, { x: 1, y: 9 }, 3);
    expect(result).toBe(2);
  });
});
