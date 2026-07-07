import { describe, expect, it } from "vitest";

import {
  computeTidyIslandLayout,
  generateOrthogonalIslandOutline,
  traceGridBoundary,
} from "./orthogonal_island_outline";
import type { Card } from "../types";

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
const CELL_GAP = 24;
const CELL_W = CARD_WIDTH + CELL_GAP;
const CELL_H = CARD_HEIGHT + CELL_GAP;

function card(id: string, row: number, col: number): Card {
  return { id, text: id, x: col * CELL_W, y: row * CELL_H };
}

describe("traceGridBoundary", () => {
  it("traces a single cell as a 4-vertex rectangle", () => {
    const loop = traceGridBoundary([{ row: 0, col: 0 }]);
    expect(loop).toHaveLength(4);
  });

  it("returns nothing for an empty cell set", () => {
    expect(traceGridBoundary([])).toEqual([]);
  });

  it("cancels the shared interior edge between two horizontally-adjacent cells", () => {
    const loop = traceGridBoundary([
      { row: 0, col: 0 },
      { row: 0, col: 1 },
    ]);
    // Raw trace before collinear simplification: 6 unit-step vertices (the
    // interior edge is gone, but the midpoints of the now-merged top/bottom
    // edges are still present as separate steps). generateOrthogonalIslandOutline's
    // own tests below cover the post-simplification 4-corner result.
    expect(loop).toHaveLength(6);
  });
});

describe("generateOrthogonalIslandOutline", () => {
  it("returns null for an empty card list", () => {
    expect(generateOrthogonalIslandOutline([])).toBeNull();
  });

  it("a single card produces a plain 4-vertex rectangle with 0 complexity", () => {
    const outline = generateOrthogonalIslandOutline([card("c1", 0, 0)]);
    expect(outline).not.toBeNull();
    expect(outline!.points).toHaveLength(4);
    expect(outline!.complexity).toBe(0);
  });

  it("a filled 2x2 grid has 0 complexity (still just 4 corners)", () => {
    const cards = [card("a", 0, 0), card("b", 0, 1), card("c", 1, 0), card("d", 1, 1)];
    const outline = generateOrthogonalIslandOutline(cards);
    expect(outline).not.toBeNull();
    expect(outline!.points).toHaveLength(4);
    expect(outline!.complexity).toBe(0);
  });

  it("an L-shaped cluster (one reflex corner) has complexity 1", () => {
    // row0: col0, col1, col2 (full); row1: col0 only.
    const cards = [
      card("a", 0, 0),
      card("b", 0, 1),
      card("c", 0, 2),
      card("d", 1, 0),
    ];
    const outline = generateOrthogonalIslandOutline(cards);
    expect(outline).not.toBeNull();
    expect(outline!.points).toHaveLength(6);
    expect(outline!.complexity).toBe(1);
  });

  it("tolerates small positional jitter around the intended grid cell", () => {
    const jitteredCards: Card[] = [
      { id: "a", text: "a", x: 3, y: -4 },
      { id: "b", text: "b", x: CELL_W + 6, y: 2 },
    ];
    const outline = generateOrthogonalIslandOutline(jitteredCards);
    expect(outline).not.toBeNull();
    expect(outline!.points).toHaveLength(4);
    expect(outline!.complexity).toBe(0);
  });

  it("produces an axis-aligned polygon (every edge is purely horizontal or vertical)", () => {
    const cards = [card("a", 0, 0), card("b", 0, 1), card("c", 0, 2), card("d", 1, 0)];
    const outline = generateOrthogonalIslandOutline(cards)!;
    for (let index = 0; index < outline.points.length; index += 1) {
      const current = outline.points[index];
      const next = outline.points[(index + 1) % outline.points.length];
      const isAxisAligned = current.x === next.x || current.y === next.y;
      expect(isAxisAligned).toBe(true);
    }
  });
});

describe("computeTidyIslandLayout", () => {
  it("returns an empty array for no cards", () => {
    expect(computeTidyIslandLayout([])).toEqual([]);
  });

  it("repacks a scattered L-shape into a denser layout that reduces complexity", () => {
    const scattered = [card("a", 0, 0), card("b", 0, 1), card("c", 0, 2), card("d", 1, 0)];
    const before = generateOrthogonalIslandOutline(scattered)!;
    expect(before.complexity).toBe(1);

    const tidied = computeTidyIslandLayout(scattered);
    const tidiedCards: Card[] = tidied.map((position) => ({ id: position.id, text: position.id, x: position.x, y: position.y }));
    const after = generateOrthogonalIslandOutline(tidiedCards)!;

    expect(after.complexity).toBeLessThan(before.complexity);
    // 4 cards -> a near-square 2x2 grid -> a perfect rectangle.
    expect(after.complexity).toBe(0);
  });

  it("is idempotent: tidying an already-dense rectangular grid keeps it at 0 complexity", () => {
    const cards = [card("a", 0, 0), card("b", 0, 1), card("c", 1, 0), card("d", 1, 1)];
    const tidied = computeTidyIslandLayout(cards);
    const tidiedCards: Card[] = tidied.map((position) => ({ id: position.id, text: position.id, x: position.x, y: position.y }));
    const outline = generateOrthogonalIslandOutline(tidiedCards)!;
    expect(outline.complexity).toBe(0);
  });

  it("preserves every card id with no duplicates or drops", () => {
    const cards = [card("a", 0, 0), card("b", 0, 1), card("c", 0, 2), card("d", 1, 0), card("e", 3, 3)];
    const tidied = computeTidyIslandLayout(cards);
    expect(tidied.map((position) => position.id).sort()).toEqual(["a", "b", "c", "d", "e"]);
  });
});
