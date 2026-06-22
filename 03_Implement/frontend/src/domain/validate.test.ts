import { describe, expect, it } from "vitest";
import workerFixtureRaw from "../../tests/fixtures/worker/doc.small.json?raw";

import { validateAndUpgradeImportedDocument } from "./validate";

describe("validateAndUpgradeImportedDocument", () => {
  it("keeps card hold state from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_hold_state",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0, holdState: "pending" }],
      edges: [],
      islands: [],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.cards[0]?.holdState).toBe("pending");
  });

  it("keeps shelf entries and normalizes their cards as shelved", () => {
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_shelf",
      createdAt: "2026-06-21T00:00:00.000Z",
      updatedAt: "2026-06-21T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 12, y: 34 }],
      edges: [],
      islands: [],
      shelf: [{ cardId: "c1", shelvedAt: "2026-06-21T01:00:00+09:00", reason: "Later" }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.cards[0]).toMatchObject({ id: "c1", x: 12, y: 34, holdState: "shelved" });
    expect(result.document.shelf).toEqual([{
      cardId: "c1",
      shelvedAt: "2026-06-20T16:00:00.000Z",
      reason: "Later",
    }]);
  });

  it("drops invalid, duplicate, and orphaned shelf entries during tolerant import", () => {
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_shelf_invalid",
      createdAt: "2026-06-21T00:00:00.000Z",
      updatedAt: "2026-06-21T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [],
      shelf: [
        { cardId: "c1", shelvedAt: "2026-06-21T01:00:00.000Z" },
        { cardId: "c1", shelvedAt: "2026-06-21T02:00:00.000Z" },
        { cardId: "missing", shelvedAt: "2026-06-21T03:00:00.000Z" },
        { cardId: "c1", shelvedAt: "not-a-date" },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.document.shelf).toHaveLength(1);
  });

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


  it("keeps island placardCardId from imported v2 JSON", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_placard",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "Placard", x: 0, y: 0 },
        { id: "c2", text: "Body", x: 120, y: 0 },
      ],
      edges: [],
      islands: [{ id: "i1", cardIds: ["c1", "c2"], placardCardId: "c1" }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.placardCardId).toBe("c1");
  });

  it("falls back to root island when parentIslandId points to missing island", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_missing_parent",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [{ id: "child", cardIds: ["c1"], parentIslandId: "unknown" }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.parentIslandId).toBeUndefined();
  });

  it("falls back to root islands when parentIslandId creates a cycle", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_parent_cycle",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "A", x: 0, y: 0 },
        { id: "c2", text: "B", x: 200, y: 0 },
      ],
      edges: [],
      islands: [
        { id: "a", cardIds: ["c1"], parentIslandId: "b" },
        { id: "b", cardIds: ["c2"], parentIslandId: "a" },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const islandsById = new Map(result.document.islands.map((island) => [island.id, island]));
    expect(islandsById.get("a")?.parentIslandId).toBeUndefined();
    expect(islandsById.get("b")?.parentIslandId).toBeUndefined();
  });

  it("keeps backward compatibility for existing fixture without parentIslandId", () => {
    const parsed = JSON.parse(workerFixtureRaw) as unknown;
    const result = validateAndUpgradeImportedDocument(parsed);

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.id).toBe("doc-small");
    expect(result.document.islands[0]?.parentIslandId).toBeUndefined();
  });


  it("defaults imported island shape to rect when shape and geometry are missing", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_default_rect_shape",
      createdAt: now,
      updatedAt: now,
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [{ id: "c1", text: "A", x: 0, y: 0 }],
      edges: [],
      islands: [{ id: "i1", cardIds: ["c1"] }],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.shape).toEqual({ kind: "rect" });
    expect(result.document.islands[0]?.geometry).toEqual({ type: "rect" });
  });

  it("derives polygon shape from imported polygon geometry for compatibility", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_shape_from_geometry",
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
              { x: 120, y: 10 },
              { x: 90, y: 90 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.shape).toEqual({
      kind: "polygon",
      points: [
        { x: 10, y: 10 },
        { x: 120, y: 10 },
        { x: 90, y: 90 },
      ],
    });
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

    expect(result.document.islands[0]?.shape).toEqual({ kind: "rect" });
  });

  it("falls back to card-bounds rendering when imported polygon self-intersects", () => {
    const now = new Date().toISOString();
    const result = validateAndUpgradeImportedDocument({
      version: 2,
      id: "doc_invalid_self_intersection",
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
              { x: 120, y: 120 },
              { x: 120, y: 0 },
              { x: 0, y: 120 },
            ],
          },
        },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;

    expect(result.document.islands[0]?.shape).toEqual({ kind: "rect" });
    expect(result.document.islands[0]?.geometry).toEqual({ type: "rect" });
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
