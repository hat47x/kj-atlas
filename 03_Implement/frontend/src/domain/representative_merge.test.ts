import { describe, expect, it, vi } from "vitest";

import type { DocumentV2 } from "./types";
import { createRepresentativeMerge } from "./representative_merge";

function createDocument(): DocumentV2 {
  return {
    version: 2,
    id: "doc_1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "A", x: 0, y: 0 },
      { id: "c2", text: "B", x: 20, y: 20 },
      { id: "c3", text: "C", x: 40, y: 40 },
    ],
    edges: [
      { id: "e1", fromId: "c1", toId: "c3", type: "related" },
      { id: "e2", fromId: "c3", toId: "c2", type: "negate" },
    ],
    islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
    readingOrder: [],
    narratives: [],
  };
}

describe("representative_merge", () => {
  it("marks originals and creates representative card", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("rep-1");

    const result = createRepresentativeMerge(createDocument(), ["c1", "c2"], "Representative");

    expect(result).not.toBeNull();
    expect(result?.representativeCardId).toBe("rep-1");
    expect(result?.mergedCardCount).toBe(2);
    expect(result?.nextDocument.cards.find((card) => card.id === "c1")?.mergedIntoCardId).toBe("rep-1");
    expect(result?.nextDocument.cards.find((card) => card.id === "c2")?.mergedIntoCardId).toBe("rep-1");
    expect(result?.nextDocument.cards.find((card) => card.id === "rep-1")?.repOf).toEqual(["c1", "c2"]);
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2"]);
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")?.fromId).toBe("c1");
  });

  it("optionally rewires membership and card edges to representative", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("rep-2");

    const result = createRepresentativeMerge(createDocument(), ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["rep-2"]);
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")?.fromId).toBe("rep-2");
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")?.toId).toBe("rep-2");
  });
});
