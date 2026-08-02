import { describe, expect, test } from "vitest";
import type { Card, DocumentV1, Island } from "../types";
import {
  computeVisibleBounds,
  getCardWorldBounds,
  getIslandCenter,
  getIslandWorldBounds,
  type VisibleBoundsViewState,
} from "./bounds";

function card(id: string, x: number, y: number): Card {
  return { id, text: "", x, y };
}

function island(id: string, cardIds: string[], overrides: Partial<Island> = {}): Island {
  return { id, cardIds, ...overrides };
}

function doc(cards: Card[], islands: Island[]): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    islands,
    edges: [],
  };
}

function fullViewState(): VisibleBoundsViewState {
  return {
    visibleIslandIds: new Set(),
    hiddenCardIds: new Set(),
    hideSourceCards: false,
    summaryView: false,
    abstractMapView: false,
  };
}

describe("getCardWorldBounds", () => {
  test("returns fixed card dimensions anchored at the card origin", () => {
    const bounds = getCardWorldBounds(card("c1", 10, 20));
    expect(bounds).toEqual({ x: 10, y: 20, w: 220, h: 80 });
  });
});

describe("getIslandWorldBounds", () => {
  test("uses the polygon bounding box when geometry is present", () => {
    const islandWithPolygon = island("i1", [], {
      geometry: {
        type: "polygon",
        points: [
          { x: 0, y: 0 },
          { x: 50, y: 0 },
          { x: 50, y: 40 },
        ],
      },
    });
    const bounds = getIslandWorldBounds(islandWithPolygon, new Map());
    expect(bounds).toEqual({ x: 0, y: 0, w: 50, h: 40 });
  });

  test("derives bounds from member cards with padding when no polygon exists", () => {
    const cardsById = new Map([
      ["c1", card("c1", 0, 0)],
      ["c2", card("c2", 100, 50)],
    ]);
    const bounds = getIslandWorldBounds(island("i1", ["c1", "c2"]), cardsById);
    expect(bounds).toEqual({
      x: 0 - 24,
      y: 0 - 24,
      w: 100 + 220 - 0 + 48,
      h: 50 + 80 - 0 + 48,
    });
  });

  test("returns null for an empty island with no polygon and no cards", () => {
    expect(getIslandWorldBounds(island("i1", []), new Map())).toBeNull();
  });
});

describe("getIslandCenter", () => {
  test("returns the midpoint of the island bounds", () => {
    const cardsById = new Map([["c1", card("c1", 0, 0)]]);
    const center = getIslandCenter(island("i1", ["c1"]), cardsById);
    expect(center).toEqual({ x: (0 - 24 + 220 + 24) / 2, y: (0 - 24 + 80 + 24) / 2 });
  });

  test("returns null when bounds cannot be computed", () => {
    expect(getIslandCenter(island("i1", []), new Map())).toBeNull();
  });
});

describe("computeVisibleBounds", () => {
  test("returns null for an empty document", () => {
    const document = doc([], []);
    expect(computeVisibleBounds(document, fullViewState())).toBeNull();
  });

  test("includes visible cards and island bounds", () => {
    const document = doc(
      [card("c1", 0, 0), card("c2", 100, 50)],
      [island("i1", ["c1", "c2"])],
    );
    const viewState = fullViewState();
    viewState.visibleIslandIds = new Set(["i1"]);

    const bounds = computeVisibleBounds(document, viewState);
    expect(bounds).not.toBeNull();
    // The union includes the island bounds (with padding) plus card rects.
    expect(bounds!.x).toBeLessThanOrEqual(0);
    expect(bounds!.y).toBeLessThanOrEqual(0);
  });

  test("excludes cards in hiddenCardIds", () => {
    const document = doc(
      [card("c1", 0, 0), card("c2", 1000, 1000)],
      [],
    );
    const viewState = fullViewState();
    viewState.hiddenCardIds = new Set(["c2"]);

    const bounds = computeVisibleBounds(document, viewState);
    expect(bounds).not.toBeNull();
    expect(bounds!.w).toBeLessThan(500);
  });
});
