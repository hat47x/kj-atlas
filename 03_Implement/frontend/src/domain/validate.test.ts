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
    if (!result.ok) return;

    const importedCard = result.document.cards.find((card) => card.id === "c1");
    expect(importedCard?.critiqueTags).toEqual(["too_close", "unrelated"]);

    const child = result.document.islands.find((island) => island.id === "child");
    expect(child?.parentIslandId).toBe("parent");
    expect(child?.critiqueTags).toEqual(["unclear_boundary"]);
  });

  it("preserves island polygon geometry from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_geometry",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
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
    if (!result.ok) return;

    expect(result.document.islands[0]?.geometry).toEqual({
      type: "polygon",
      points: [
        { x: 0, y: 0 },
        { x: 100, y: 0 },
        { x: 80, y: 60 },
      ],
    });
  });

  it("accepts legacy polygon geometry format and normalizes to points", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_geometry_legacy",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            polygon: {
              points: [
                { x: 10, y: 10 },
                { x: 110, y: 10 },
                { x: 90, y: 80 },
              ],
            },
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.geometry).toEqual({
      type: "polygon",
      points: [
        { x: 10, y: 10 },
        { x: 110, y: 10 },
        { x: 90, y: 80 },
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
    if (!result.ok) return;

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
    if (!result.ok) return;

    expect(result.document.islands[0]?.shape).toBeUndefined();
  });

  it("keeps polygon geometry through export/import roundtrip", () => {
    const now = new Date().toISOString();
    const source = {
      version: 2,
      id: "doc_roundtrip_geometry",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [
        {
          id: "i1",
          cardIds: ["c1"],
          geometry: {
            type: "polygon",
            points: [
              { x: 10, y: 10 },
              { x: 110, y: 10 },
              { x: 90, y: 80 },
            ],
          },
        },
      ],
    };

    const exported = JSON.parse(JSON.stringify(source));
    const result = validateAndUpgradeImportedDocument(exported);
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.geometry).toEqual(source.islands[0].geometry);
  });
});
