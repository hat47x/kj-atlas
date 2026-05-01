import { describe, expect, it } from "vitest";

import { alignSelectedCards, distributeSelectedCards, repositionCoreGraph, snapValueToGrid } from "./layout_ops";
import type { Card } from "./types";

const cards: Card[] = [
  { id: "a", text: "A", x: 10, y: 10 },
  { id: "b", text: "B", x: 110, y: 70 },
  { id: "c", text: "C", x: 210, y: 130 },
];

describe("layout_ops", () => {
  it("aligns selected cards to the left anchor", () => {
    const next = alignSelectedCards(cards, ["a", "c"], "left", {});
    const cardA = next.find((card) => card.id === "a");
    const cardC = next.find((card) => card.id === "c");

    expect(cardA?.x).toBe(10);
    expect(cardC?.x).toBe(10);
  });

  it("aligns selected cards to the right edge using card width", () => {
    const next = alignSelectedCards(cards, ["a", "c"], "right", { cardWidth: 220 });
    const cardA = next.find((card) => card.id === "a");
    const cardC = next.find((card) => card.id === "c");

    expect(cardA?.x).toBe(210);
    expect(cardC?.x).toBe(210);
  });

  it("distributes selected cards horizontally by x", () => {
    const input: Card[] = [
      { id: "a", text: "A", x: 0, y: 0 },
      { id: "b", text: "B", x: 300, y: 40 },
      { id: "c", text: "C", x: 100, y: 80 },
    ];

    const next = distributeSelectedCards(input, ["a", "b", "c"], "horizontal", {});

    expect(next.find((card) => card.id === "a")?.x).toBe(0);
    expect(next.find((card) => card.id === "c")?.x).toBe(150);
    expect(next.find((card) => card.id === "b")?.x).toBe(300);
  });

  it("returns original array when fewer than three cards are selected for distribute", () => {
    const next = distributeSelectedCards(cards, ["a", "b"], "vertical", {});

    expect(next).toBe(cards);
  });

  it("snaps values to the configured grid", () => {
    expect(snapValueToGrid(14, { gridSize: 10 })).toBe(10);
    expect(snapValueToGrid(16, { gridSize: 10 })).toBe(20);
    expect(snapValueToGrid(16, { gridSize: 0 })).toBe(16);
  });

  it("repositions selected core graph by centroid deterministically", () => {
    const first = repositionCoreGraph(cards, {
      selectedIds: ["a", "b"],
      targetX: 200,
      targetY: 200,
    });
    const second = repositionCoreGraph(cards, {
      selectedIds: ["a", "b"],
      targetX: 200,
      targetY: 200,
    });

    expect(first.cards).toEqual(second.cards);
    expect(first.usedMockAdapter).toBe(true);
    expect(first.cards.find((card) => card.id === "a")).toMatchObject({ x: 150, y: 170 });
    expect(first.cards.find((card) => card.id === "b")).toMatchObject({ x: 250, y: 230 });
  });

  it("repositions using bounds-center anchor with grid snapping", () => {
    const next = repositionCoreGraph(cards, {
      selectedIds: ["a", "c"],
      targetX: 125,
      targetY: 115,
      anchorMode: "bounds-center",
      snapToGridSize: 10,
    });

    expect(next.cards.find((card) => card.id === "a")).toMatchObject({ x: 30, y: 60 });
    expect(next.cards.find((card) => card.id === "c")).toMatchObject({ x: 230, y: 180 });
  });

  it("supports local contract adapter and flags non-mock path", () => {
    const next = repositionCoreGraph(cards, {
      selectedIds: ["b"],
      targetX: 500,
      targetY: 300,
      adapter: {
        toNode: (card) => ({ id: card.id, x: card.x + 1, y: card.y + 1 }),
        applyPosition: (card, pos) => ({ ...card, x: pos.x - 1, y: pos.y - 1 }),
      },
    });

    expect(next.usedMockAdapter).toBe(false);
    expect(next.cards.find((card) => card.id === "b")).toMatchObject({ x: 499, y: 299 });
  });

});
