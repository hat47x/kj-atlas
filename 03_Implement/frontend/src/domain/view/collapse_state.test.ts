import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "../types";
import { setAllIslandsCollapsed, setIslandCollapsed } from "./collapse_state";

function makeDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [
      { id: "i-1", cardIds: ["c-1"], collapsed: false },
      { id: "i-2", cardIds: ["c-2"], collapsed: true },
    ],
  };
}

describe("setIslandCollapsed", () => {
  it("updates only the target island", () => {
    const doc = makeDocument();
    const result = setIslandCollapsed(doc, "i-1", true);

    expect(result.changed).toBe(true);
    expect(result.nextDocument.islands.find((island) => island.id === "i-1")?.collapsed).toBe(true);
    expect(result.nextDocument.islands.find((island) => island.id === "i-2")?.collapsed).toBe(true);
  });

  it("returns fail-fast metadata for unknown island id", () => {
    const doc = makeDocument();
    const result = setIslandCollapsed(doc, "missing", true);

    expect(result.changed).toBe(false);
    expect(result.rejectedReason).toBe("island-not-found");
    expect(result.nextDocument).toBe(doc);
  });

  it("returns unchanged result when collapsed value is already the same", () => {
    const doc = makeDocument();
    const result = setIslandCollapsed(doc, "i-1", false);

    expect(result.changed).toBe(false);
    expect(result.rejectedReason).toBeUndefined();
    expect(result.nextDocument).toBe(doc);
  });
});

describe("setAllIslandsCollapsed", () => {
  it("sets collapsed flag for every island", () => {
    const doc = makeDocument();
    const result = setAllIslandsCollapsed(doc, true);

    expect(result.changed).toBe(true);
    expect(result.nextDocument.islands.every((island) => island.collapsed === true)).toBe(true);
  });

  it("returns unchanged result when all islands already match", () => {
    const doc = makeDocument();
    const collapsedDoc = setAllIslandsCollapsed(doc, true).nextDocument;
    const result = setAllIslandsCollapsed(collapsedDoc, true);

    expect(result.changed).toBe(false);
    expect(result.nextDocument).toBe(collapsedDoc);
  });
});
