import { describe, expect, it } from "vitest";

import { buildReadingOrderMarkers } from "./ReadingOrderLayer";

describe("buildReadingOrderMarkers", () => {
  it("returns markers only for currently visible readingOrder entries", () => {
    const cards = [
      { id: "card-1", text: "A", x: 100, y: 80 },
      { id: "card-2", text: "B", x: 320, y: 120 },
    ];
    const islands = [{ id: "island-1", cardIds: ["card-2"], title: "Island" }];

    const markers = buildReadingOrderMarkers(
      cards,
      islands,
      ["card-1", "card-hidden", "island-1"],
      new Set(["card-1", "card-2"]),
      new Set(["island-1"])
    );

    expect(markers).toHaveLength(2);
    expect(markers.map((m) => m.entryId)).toEqual(["card-1", "island-1"]);
    expect(markers.map((m) => m.index)).toEqual([0, 2]);
  });

  it("skips islands without computable bounds", () => {
    const cards = [{ id: "card-1", text: "A", x: 100, y: 80 }];
    const islands = [{ id: "island-empty", cardIds: ["missing-card"] }];

    const markers = buildReadingOrderMarkers(
      cards,
      islands,
      ["island-empty"],
      new Set(["card-1"]),
      new Set(["island-empty"])
    );

    expect(markers).toEqual([]);
  });
});
