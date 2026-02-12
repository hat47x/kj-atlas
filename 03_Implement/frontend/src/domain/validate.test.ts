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

});
