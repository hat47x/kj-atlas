import { beforeEach, describe, expect, it } from "vitest";

import { getIslandBounds, resolveIslandRepresentativeTitle } from "./IslandView";
import type { Card, Island } from "../domain/types";
import { setActiveLocale } from "../i18n/translate";

const CARD_WIDTH = 220;
const CARD_MIN_HEIGHT = 80;
const ISLAND_PADDING = 24;

describe("getIslandBounds", () => {
  it("uses polygon points when island shape is polygon", () => {
    const island: Island = {
      id: "i1",
      cardIds: ["c1"],
      shape: {
        kind: "polygon",
        points: [
          { x: 100, y: 100 },
          { x: 260, y: 110 },
          { x: 240, y: 220 },
        ],
      },
    };

    const cards: Card[] = [{ id: "c1", text: "a", x: 0, y: 0 }];
    expect(getIslandBounds(island, cards)).toEqual({
      left: 100,
      top: 100,
      width: 160,
      height: 120,
    });
  });

  it("uses geometry polygon points when island geometry is polygon", () => {
    const island: Island = {
      id: "i1",
      cardIds: ["c1"],
      geometry: {
        type: "polygon",
        points: [
          { x: 10, y: 20 },
          { x: 80, y: 40 },
          { x: 60, y: 120 },
        ],
      },
    };

    const cards: Card[] = [{ id: "c1", text: "a", x: 0, y: 0 }];
    expect(getIslandBounds(island, cards)).toEqual({
      left: 10,
      top: 20,
      width: 70,
      height: 100,
    });
  });

  it("falls back to card bounds when shape is missing", () => {
    const island: Island = {
      id: "i1",
      cardIds: ["c1", "c2"],
    };

    const cards: Card[] = [
      { id: "c1", text: "a", x: 50, y: 40 },
      { id: "c2", text: "b", x: 300, y: 200 },
    ];

    expect(getIslandBounds(island, cards)).toEqual({
      left: 50 - ISLAND_PADDING,
      top: 40 - ISLAND_PADDING,
      width: 300 + CARD_WIDTH - 50 + ISLAND_PADDING * 2,
      height: 200 + CARD_MIN_HEIGHT - 40 + ISLAND_PADDING * 2,
    });
  });

  it("falls back to card bounds when polygon has too few points", () => {
    const island: Island = {
      id: "i1",
      cardIds: ["c1"],
      shape: {
        kind: "polygon",
        points: [
          { x: 0, y: 0 },
          { x: 100, y: 0 },
        ],
      },
    };

    const cards: Card[] = [{ id: "c1", text: "a", x: 10, y: 20 }];

    expect(getIslandBounds(island, cards)).toEqual({
      left: 10 - ISLAND_PADDING,
      top: 20 - ISLAND_PADDING,
      width: CARD_WIDTH + ISLAND_PADDING * 2,
      height: CARD_MIN_HEIGHT + ISLAND_PADDING * 2,
    });
  });
  it("falls back to card bounds when polygon self-intersects", () => {
    const island: Island = {
      id: "i1",
      cardIds: ["c1"],
      shape: {
        kind: "polygon",
        points: [
          { x: 0, y: 0 },
          { x: 120, y: 120 },
          { x: 120, y: 0 },
          { x: 0, y: 120 },
        ],
      },
    };

    const cards: Card[] = [{ id: "c1", text: "a", x: 10, y: 20 }];

    expect(getIslandBounds(island, cards)).toEqual({
      left: 10 - ISLAND_PADDING,
      top: 20 - ISLAND_PADDING,
      width: CARD_WIDTH + ISLAND_PADDING * 2,
      height: CARD_MIN_HEIGHT + ISLAND_PADDING * 2,
    });
  });

});


describe("resolveIslandRepresentativeTitle", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("prefers placard card text when present", () => {
    const island: Island = { id: "i1", cardIds: ["c1"], placardCardId: "c1", title: "Fallback" };
    const cards: Card[] = [{ id: "c1", text: " Placard title ", x: 0, y: 0 }];

    expect(resolveIslandRepresentativeTitle(island, cards)).toBe("Placard title");
  });

  it("falls back to island title when placard text is missing", () => {
    const island: Island = { id: "i1", cardIds: ["c1"], placardCardId: "c1", title: " Island name " };
    const cards: Card[] = [{ id: "c1", text: "   ", x: 0, y: 0 }];

    expect(resolveIslandRepresentativeTitle(island, cards)).toBe("Island name");
  });

  it("uses default label when both placard and title are absent", () => {
    const island: Island = { id: "i1", cardIds: [] };

    expect(resolveIslandRepresentativeTitle(island, [])).toBe("島");
  });

  it("uses localized default label for English locale", () => {
    setActiveLocale("en");
    const island: Island = { id: "i1", cardIds: [] };

    expect(resolveIslandRepresentativeTitle(island, [])).toBe("Island");
  });
});
