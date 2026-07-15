import { describe, expect, it } from "vitest";

import { buildReadingList, clampReadingIndex } from "./reading_path";
import type { DocumentV1 } from "../types";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-1", text: "Card A", x: 100, y: 200 },
      { id: "c-2", text: "Card B", x: 150, y: 260 },
      { id: "c-3", text: "Card C", x: 500, y: 40 },
      { id: "c-lone", text: "Lone card", x: 800, y: 900 },
    ],
    edges: [],
    islands: [
      { id: "i-bottom", cardIds: ["c-1", "c-2"], title: "Bottom", summaryText: "Needs review", summaryReviewed: false },
      { id: "i-top", cardIds: ["c-3"], title: "Top", summaryText: "Reviewed", summaryReviewed: true },
    ],
  };
}

describe("reading path", () => {
  it("builds deterministic islands-only list by spatial order", () => {
    const list = buildReadingList(buildDoc(), { readingMode: "islands", reviewedOnly: false });

    expect(list.map((item) => item.id)).toEqual(["i-top", "i-bottom"]);
    expect(list.every((item) => item.kind === "island")).toBe(true);
  });

  it("skips unreviewed islands when reviewedOnly is enabled", () => {
    const list = buildReadingList(buildDoc(), { readingMode: "islands", reviewedOnly: true });
    expect(list.map((item) => item.id)).toEqual(["i-top"]);
  });

  it("includes island cards and lone cards at end in islands+cards mode", () => {
    const list = buildReadingList(buildDoc(), { readingMode: "islands+cards", reviewedOnly: false });
    expect(list.map((item) => `${item.kind}:${item.id}`)).toEqual([
      "island:i-top",
      "card:c-3",
      "island:i-bottom",
      "card:c-1",
      "card:c-2",
      "card:c-lone",
    ]);
  });

  it("keeps cards in islands+cards mode even when reviewedOnly filters out islands", () => {
    const list = buildReadingList(buildDoc(), { readingMode: "islands+cards", reviewedOnly: true });
    expect(list.map((item) => `${item.kind}:${item.id}`)).toEqual([
      "island:i-top",
      "card:c-3",
      "card:c-1",
      "card:c-2",
      "card:c-lone",
    ]);
  });

  it("clamps reading index", () => {
    expect(clampReadingIndex(-1, 3)).toBe(0);
    expect(clampReadingIndex(2, 3)).toBe(2);
    expect(clampReadingIndex(9, 3)).toBe(2);
    expect(clampReadingIndex(0, 0)).toBe(0);
  });
});
