import { describe, expect, test } from "vitest";
import type { DocumentV1 } from "./types";
import { buildReadingOrderSnippets } from "./snippet";

function doc(overrides: Partial<DocumentV1> = {}): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "card one", x: 0, y: 0 },
      { id: "c2", text: "card two", x: 10, y: 0 },
      { id: "c3", text: "", x: 20, y: 0 },
    ],
    edges: [],
    ...overrides,
  };
}

describe("buildReadingOrderSnippets", () => {
  test("maps every card id to its text", () => {
    const snippets = buildReadingOrderSnippets(doc({ islands: [] }));
    expect(snippets).toMatchObject({ c1: "card one", c2: "card two", c3: "" });
  });

  test("returns empty text for a card with an empty string", () => {
    const snippets = buildReadingOrderSnippets(doc({ islands: [] }));
    expect(snippets.c3).toBe("");
  });

  test("maps island ids to summaryText when available, falling back to title", () => {
    const d = doc({
      islands: [
        { id: "i1", cardIds: ["c1"], summaryText: "summary 1", title: "title 1" },
        { id: "i2", cardIds: ["c2"], title: "title 2" },
      ],
    });
    const snippets = buildReadingOrderSnippets(d);
    expect(snippets.i1).toBe("summary 1");
    expect(snippets.i2).toBe("title 2");
  });

  test("returns undefined for an island with neither summaryText nor title", () => {
    const d = doc({
      islands: [{ id: "i3", cardIds: ["c3"] }],
    });
    const snippets = buildReadingOrderSnippets(d);
    expect(snippets.i3).toBeUndefined();
  });

  test("returns an empty record for a document with no cards or islands", () => {
    const d = doc({ cards: [], islands: [] });
    expect(buildReadingOrderSnippets(d)).toEqual({});
  });
});
