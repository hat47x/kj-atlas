import { describe, expect, it } from "vitest";

import type { Card, Island } from "../types";
import { buildVersionTokenForCardIds, isPolygonShapeStale } from "./polygon_stale";

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;

function createPolygonIsland(versionToken: string, cardIds: string[] = ["c1"]): Island {
  return {
    id: "island-1",
    cardIds,
    shape: {
      kind: "polygon",
      points: [
        { x: 0, y: 0 },
        { x: 120, y: 0 },
        { x: 80, y: 60 },
      ],
      generatedFrom: {
        cardIds,
        versionToken,
      },
    },
  };
}

describe("polygon_stale", () => {
  it("detects stale polygon when member card position changed", () => {
    const cards: Card[] = [{ id: "c1", text: "A", x: 10, y: 20 }];
    const island = createPolygonIsland("c1:0,0,220,80");

    expect(isPolygonShapeStale(island, cards, CARD_WIDTH, CARD_HEIGHT)).toBe(true);
  });

  it("returns not stale when generated token matches current members", () => {
    const cards: Card[] = [{ id: "c1", text: "A", x: 10, y: 20 }];
    const versionToken = buildVersionTokenForCardIds(cards, ["c1"], CARD_WIDTH, CARD_HEIGHT);
    const island = createPolygonIsland(versionToken);

    expect(isPolygonShapeStale(island, cards, CARD_WIDTH, CARD_HEIGHT)).toBe(false);
  });

  it("returns stale when tracked card ids differ from current island members", () => {
    const cards: Card[] = [
      { id: "c1", text: "A", x: 10, y: 20 },
      { id: "c2", text: "B", x: 30, y: 40 },
    ];
    const versionToken = buildVersionTokenForCardIds(cards, ["c1"], CARD_WIDTH, CARD_HEIGHT);
    const island = createPolygonIsland(versionToken, ["c1", "c2"]);

    expect(isPolygonShapeStale(island, cards, CARD_WIDTH, CARD_HEIGHT)).toBe(true);
  });
});
