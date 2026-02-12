import { describe, expect, it } from "vitest";

import { alignSelectedCards, distributeSelectedCards, snapValueToGrid } from "./layout_ops";
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
});
