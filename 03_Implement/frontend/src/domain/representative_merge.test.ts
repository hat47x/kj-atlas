import { describe, expect, it, vi } from "vitest";

import type { DocumentV1 } from "./types";
import { createRepresentativeMerge } from "./representative_merge";

function createDocument(): DocumentV1 {
  return {
    version: 1,
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
    islands: [
      { id: "i1", cardIds: ["c1", "c2"] },
      { id: "i2", cardIds: ["c2", "c3"] },
    ],
    readingOrder: [],
    narratives: [],
  };
}

describe("representative_merge", () => {
  it("marks originals and creates representative card without changing structure by default", () => {
    vi.spyOn(crypto, "randomUUID").mockReturnValue("00000000-0000-0000-0000-000000000001");

    const result = createRepresentativeMerge(createDocument(), ["c1", "c2"], "Representative");

    expect(result).not.toBeNull();
    expect(result?.representativeCardId).toBe("00000000-0000-0000-0000-000000000001");
    expect(result?.mergedCardCount).toBe(2);
    expect(result?.nextDocument.cards.find((card) => card.id === "c1")?.mergedIntoCardId).toBe("00000000-0000-0000-0000-000000000001");
    expect(result?.nextDocument.cards.find((card) => card.id === "c2")?.mergedIntoCardId).toBe("00000000-0000-0000-0000-000000000001");
    expect(result?.nextDocument.cards.find((card) => card.id === "00000000-0000-0000-0000-000000000001")?.repOf).toEqual(["c1", "c2"]);
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2"]);
    expect(result?.nextDocument.islands[1]?.cardIds).toEqual(["c2", "c3"]);
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")?.fromId).toBe("c1");
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")?.toId).toBe("c2");
  });

  it("adds representative membership and edge projections without overwriting source structure", () => {
    const representativeId = "00000000-0000-0000-0000-000000000002";
    vi.spyOn(crypto, "randomUUID").mockReturnValue(representativeId);

    const result = createRepresentativeMerge(createDocument(), ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    expect(result?.nextDocument.islands[0]?.cardIds).toEqual(["c1", "c2", representativeId]);
    expect(result?.nextDocument.islands[1]?.cardIds).toEqual(["c2", "c3", representativeId]);

    // 元edgeは変更せず、統合前の構造来歴として残す。
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e1")).toMatchObject({
      fromId: "c1",
      toId: "c3",
      type: "related",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === "e2")).toMatchObject({
      fromId: "c3",
      toId: "c2",
      type: "negate",
    });

    // 表示・探索用には代表カード側の投影edgeを追加する。
    expect(result?.nextDocument.edges.find((edge) => edge.id === `representative:${representativeId}:e1`)).toMatchObject({
      fromId: representativeId,
      toId: "c3",
      type: "related",
    });
    expect(result?.nextDocument.edges.find((edge) => edge.id === `representative:${representativeId}:e2`)).toMatchObject({
      fromId: "c3",
      toId: representativeId,
      type: "negate",
    });
  });

  it("does not create representative self-loops or duplicate equivalent projections", () => {
    const representativeId = "00000000-0000-0000-0000-000000000003";
    vi.spyOn(crypto, "randomUUID").mockReturnValue(representativeId);
    const document = createDocument();
    document.edges = [
      { id: "e1", fromId: "c1", toId: "c3", type: "related" },
      { id: "e2", fromId: "c2", toId: "c3", type: "related" },
      { id: "e3", fromId: "c1", toId: "c2", type: "equivalence" },
    ];

    const result = createRepresentativeMerge(document, ["c1", "c2"], "Representative", {
      rewireMembershipAndEdges: true,
    });

    expect(result).not.toBeNull();
    const projectedToC3 = result?.nextDocument.edges.filter(
      (edge) => edge.fromId === representativeId && edge.toId === "c3" && edge.type === "related",
    );
    expect(projectedToC3).toHaveLength(1);
    expect(
      result?.nextDocument.edges.some(
        (edge) => edge.fromId === representativeId && edge.toId === representativeId,
      ),
    ).toBe(false);

    // 元の三本はすべて残り、代表カードへの投影だけが一件追加される。
    expect(result?.nextDocument.edges).toHaveLength(4);
    expect(result?.nextDocument.edges.map((edge) => edge.id)).toEqual(
      expect.arrayContaining(["e1", "e2", "e3"]),
    );
  });
});
