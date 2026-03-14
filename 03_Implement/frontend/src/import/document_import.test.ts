import { describe, expect, test } from "vitest";
import { parseDocumentJson } from "./document_import";

const BASE = {
  version: 2,
  id: "doc-p2a",
  createdAt: "2026-03-01T00:00:00.000Z",
  updatedAt: "2026-03-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "root", x: 0, y: 0 },
    { id: "c2", text: "child", x: 10, y: 10 },
    { id: "c3", text: "grand", x: 20, y: 20 },
  ],
  edges: [],
};

function parseWithIslands(islands: unknown) {
  return parseDocumentJson(JSON.stringify({ ...BASE, islands }));
}

describe("parseDocumentJson", () => {
  test("returns invalid json error", () => {
    const result = parseDocumentJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain("Invalid JSON in document.json");
    }
  });

  test("keeps valid parentIslandId hierarchy", () => {
    const result = parseWithIslands([
      { id: "root", cardIds: ["c1"] },
      { id: "child", cardIds: ["c2"], parentIslandId: "root" },
      { id: "grand", cardIds: ["c3"], parentIslandId: "child" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "child")?.parentIslandId).toBe("root");
      expect(result.document.islands.find((island) => island.id === "grand")?.parentIslandId).toBe("child");
    }
  });

  test("normalizes missing parentIslandId reference to undefined", () => {
    const result = parseWithIslands([
      { id: "root", cardIds: ["c1"] },
      { id: "orphan", cardIds: ["c2"], parentIslandId: "missing" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "orphan")?.parentIslandId).toBeUndefined();
    }
  });

  test("normalizes cycle parentIslandId references to undefined", () => {
    const result = parseWithIslands([
      { id: "a", cardIds: ["c1"], parentIslandId: "b" },
      { id: "b", cardIds: ["c2"], parentIslandId: "a" },
      { id: "c", cardIds: ["c3"], parentIslandId: "c" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "a")?.parentIslandId).toBeUndefined();
      expect(result.document.islands.find((island) => island.id === "b")?.parentIslandId).toBeUndefined();
      expect(result.document.islands.find((island) => island.id === "c")?.parentIslandId).toBeUndefined();
    }
  });
});
