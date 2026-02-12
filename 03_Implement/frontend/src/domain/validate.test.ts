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
        { id: "c1", text: "A", x: 0, y: 0 },
        { id: "c2", text: "B", x: 300, y: 0 },
      ],
      edges: [],
      islands: [
        { id: "parent", cardIds: ["c1"] },
        { id: "child", cardIds: ["c2"], parentIslandId: "parent" },
      ],
    });

    expect(result.ok).toBe(true);
    if (!result.ok) {
      return;
    }

    const child = result.document.islands.find((island) => island.id === "child");
    expect(child?.parentIslandId).toBe("parent");
  });
});
