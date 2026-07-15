import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { collectHierarchyHiddenIslandIds, collectHierarchyPlacardHiddenCardIds } from "./hierarchy_visibility";

const documentFixture: DocumentV1 = {
  version: 1,
  id: "doc-hierarchy",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c-root", text: "Root placard", x: 0, y: 0 },
    { id: "c-root-member", text: "Root member", x: 20, y: 0 },
    { id: "c-child", text: "Child placard", x: 40, y: 0 },
    { id: "c-child-member", text: "Child member", x: 60, y: 0 },
  ],
  edges: [],
  islands: [
    { id: "i-root", cardIds: ["c-root", "c-root-member"], placardCardId: "c-root" },
    { id: "i-child", cardIds: ["c-child", "c-child-member"], parentIslandId: "i-root", placardCardId: "c-child" },
  ],
};

describe("hierarchy_visibility", () => {
  it("hides islands deterministically by maxDepth", () => {
    const islandDepthById = new Map<string, number>([
      ["i-root", 0],
      ["i-child", 1],
    ]);

    expect(collectHierarchyHiddenIslandIds(documentFixture.islands, islandDepthById, "all")).toEqual(new Set());
    expect(collectHierarchyHiddenIslandIds(documentFixture.islands, islandDepthById, 0)).toEqual(new Set(["i-child"]));
    expect(collectHierarchyHiddenIslandIds(documentFixture.islands, islandDepthById, 1)).toEqual(new Set());
  });

  it("shows only placard cards in overview and keeps full cards in detail", () => {
    const overviewHidden = collectHierarchyPlacardHiddenCardIds(documentFixture, "overview");
    expect(overviewHidden).toEqual(new Set(["c-root-member", "c-child-member"]));

    expect(collectHierarchyPlacardHiddenCardIds(documentFixture, "mid")).toEqual(new Set());
    expect(collectHierarchyPlacardHiddenCardIds(documentFixture, "detail")).toEqual(new Set());
  });

  it("keeps underlying cards intact while switching hierarchy levels", () => {
    const originalCardIds = documentFixture.cards.map((card) => card.id);

    const overviewHidden = collectHierarchyPlacardHiddenCardIds(documentFixture, "overview");
    expect(overviewHidden).toEqual(new Set(["c-root-member", "c-child-member"]));

    expect(documentFixture.cards.map((card) => card.id)).toEqual(originalCardIds);
    expect(collectHierarchyPlacardHiddenCardIds(documentFixture, "detail")).toEqual(new Set());
    expect(documentFixture.cards.map((card) => card.id)).toEqual(originalCardIds);
  });

  it("falls back safely when placardCardId is missing or outside island membership", () => {
    const fallbackDocument: DocumentV1 = {
      ...documentFixture,
      islands: [
        { id: "i-root", cardIds: ["c-root", "c-root-member"], placardCardId: "missing-card" },
        { id: "i-child", cardIds: ["c-child", "c-child-member"] },
      ],
    };

    expect(collectHierarchyPlacardHiddenCardIds(fallbackDocument, "overview")).toEqual(new Set([
      "c-root",
      "c-root-member",
      "c-child",
      "c-child-member",
    ]));
  });

});

