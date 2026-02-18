import { describe, expect, it } from "vitest";

import { validateAndUpgradeImportedDocument } from "./validate";

describe("validateAndUpgradeImportedDocument", () => {
  it("keeps island parentIslandId from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_nested",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "A", x: 0, y: 0, critiqueTags: ["too_close", "unrelated"] },
        { id: "c2", text: "B", x: 300, y: 0 },
      ],
      edges: [],
      islands: [
        { id: "parent", cardIds: ["c1"] },
        { id: "child", cardIds: ["c2"], parentIslandId: "parent", critiqueTags: ["unclear_boundary"] },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    const importedCard = result.document.cards.find((card) => card.id === "c1");
    expect(importedCard?.critiqueTags).toEqual(["too_close", "unrelated"]);

    const child = result.document.islands.find((island) => island.id === "child");
    expect(child?.parentIslandId).toBe("parent");
    expect(child?.critiqueTags).toEqual(["unclear_boundary"]);
  });

  it("defaults island collapsed to false and preserves explicit true", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_collapsed",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        { id: "i1", cardIds: ["c1"] },
        { id: "i2", cardIds: [], collapsed: true },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    const defaultCollapsedIsland = result.document.islands.find((island) => island.id === "i1");
    const explicitCollapsedIsland = result.document.islands.find((island) => island.id === "i2");

    expect(defaultCollapsedIsland?.collapsed).toBe(false);
    expect(explicitCollapsedIsland?.collapsed).toBe(true);
  });

  it("preserves edge endpoint kinds from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_edge_kinds",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [
        { id: "e1", fromId: "c1", toId: "i1", fromKind: "card", toKind: "island", type: "related" },
      ],
      islands: [{ id: "i1", cardIds: ["c1"] }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    expect(result.document.edges[0]).toMatchObject({
      fromKind: "card",
      toKind: "island",
    });
  });

  it("preserves canonical relationship fields from imported cards", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_canonical",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "canonical", x: 0, y: 0, sources: ["c2"] },
        { id: "c2", text: "source", x: 10, y: 20, canonicalId: "c1" },
      ],
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    const canonicalCard = result.document.cards.find((card) => card.id === "c1");
    const sourceCard = result.document.cards.find((card) => card.id === "c2");

    expect(canonicalCard?.sources).toEqual(["c2"]);
    expect(sourceCard?.canonicalId).toBe("c1");
  });

  it("preserves island polygon shape points from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_shapes",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
              { x: 80, y: 60 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    expect(result.document.islands[0]?.shape).toEqual({
      kind: "polygon",
      points: [
        { x: 0, y: 0 },
        { x: 100, y: 0 },
        { x: 80, y: 60 },
      ],
    });
  });

  it("preserves polygon generatedFrom metadata and optional shapeStale flag", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_shape_meta",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shapeStale: true,
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
              { x: 80, y: 60 },
            ],
            generatedFrom: {
              cardIds: ["c1"],
              versionToken: "c1:0,0,220,80",
            },
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    expect(result.document.islands[0]?.shape?.generatedFrom).toEqual({
      cardIds: ["c1"],
      versionToken: "c1:0,0,220,80",
    });
    expect(result.document.islands[0]?.shapeStale).toBe(true);
  });


  it("falls back to card-bounds rendering when imported polygon has fewer than 3 points", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_invalid_polygon",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          shape: {
            kind: "polygon",
            points: [
              { x: 0, y: 0 },
              { x: 100, y: 0 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    expect(result.document.islands[0]?.shape).toBeUndefined();
  });

});
