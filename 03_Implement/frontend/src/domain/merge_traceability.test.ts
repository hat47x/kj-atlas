import { describe, expect, it } from "vitest";

import type { DocumentV1 } from "./types";
import { resolveDecisionOriginTrace, resolveRepresentativeOriginTrace } from "./merge_traceability";

function createDocument(overrides: Partial<DocumentV1> = {}): DocumentV1 {
  return {
    version: 1,
    id: "doc-trace",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    ...overrides,
  };
}

describe("merge_traceability", () => {
  it("resolves representative trace deterministically from repOf and mergedIntoCardId", () => {
    const document = createDocument({
      cards: [
        { id: "rep", text: "Representative", x: 0, y: 0, repOf: ["c2", "c1", "c1"] },
        { id: "c1", text: "source-1", x: 1, y: 1, mergedIntoCardId: "rep" },
        { id: "c2", text: "source-2", x: 2, y: 2, mergedIntoCardId: "rep" },
      ],
    });

    expect(resolveRepresentativeOriginTrace(document, "rep")).toEqual({
      representativeCardId: "rep",
      sourceCardIds: ["c1", "c2"],
      missingSourceCardIds: [],
      representativeResolvedBy: "repOf",
    });
  });

  it("keeps missing source ids when representative references deleted cards", () => {
    const document = createDocument({
      cards: [
        { id: "rep", text: "Representative", x: 0, y: 0, repOf: ["c-live", "c-deleted"] },
        { id: "c-live", text: "source-live", x: 1, y: 1, mergedIntoCardId: "rep" },
      ],
    });

    expect(resolveRepresentativeOriginTrace(document, "rep")).toEqual({
      representativeCardId: "rep",
      sourceCardIds: ["c-live"],
      missingSourceCardIds: ["c-deleted"],
      representativeResolvedBy: "repOf",
    });
  });

  it("falls back to sorted decision ids when representative is unresolved", () => {
    const document = createDocument({
      cards: [
        { id: "a", text: "a", x: 0, y: 0 },
        { id: "b", text: "b", x: 0, y: 0 },
      ],
    });

    expect(resolveDecisionOriginTrace(document, ["b", "a"])).toEqual({
      representativeCardId: "a",
      sourceCardIds: ["b"],
      missingSourceCardIds: [],
      representativeResolvedBy: "fallback",
    });
  });

  it("selects representative by highest repOf overlap before fallback", () => {
    const document = createDocument({
      cards: [
        { id: "rep-z", text: "rep z", x: 0, y: 0, repOf: ["a"] },
        { id: "rep-a", text: "rep a", x: 0, y: 0, repOf: ["a", "b"] },
        { id: "a", text: "a", x: 0, y: 0 },
        { id: "b", text: "b", x: 0, y: 0 },
      ],
    });

    expect(resolveDecisionOriginTrace(document, ["b", "a"])).toEqual({
      representativeCardId: "rep-a",
      sourceCardIds: ["a", "b"],
      missingSourceCardIds: [],
      representativeResolvedBy: "repOf",
    });
  });
});
