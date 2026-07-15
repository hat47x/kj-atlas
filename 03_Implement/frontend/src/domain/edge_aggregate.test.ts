import { describe, expect, it } from "vitest";

import { getEdgesToRender } from "./edge_aggregate";
import type { DocumentV1 } from "./types";

const baseDoc: DocumentV1 = {
  version: 1,
  id: "doc-1",
  createdAt: "2026-01-01T00:00:00Z",
  updatedAt: "2026-01-01T00:00:00Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "canon-a", text: "A", x: 0, y: 0 },
    { id: "canon-b", text: "B", x: 300, y: 0 },
    { id: "source-a1", text: "A1", x: 0, y: 100, canonicalId: "canon-a" },
    { id: "source-a2", text: "A2", x: 0, y: 200, canonicalId: "canon-a" },
    { id: "source-b1", text: "B1", x: 300, y: 100, canonicalId: "canon-b" },
  ],
  islands: [{ id: "island-1", cardIds: ["canon-a", "canon-b"] }],
  edges: [],
};

describe("getEdgesToRender", () => {
  it("returns original edges when hideSourceCards is false", () => {
    const doc: DocumentV1 = {
      ...baseDoc,
      edges: [{ id: "e1", fromId: "source-a1", toId: "canon-b", type: "related" }],
    };

    const edges = getEdgesToRender(doc, false);

    expect(edges).toEqual([
      {
        id: "e1",
        fromId: "source-a1",
        toId: "canon-b",
        fromKind: "card",
        toKind: "card",
        type: "related",
      },
    ]);
  });

  it("aggregates hidden source edges and counts duplicates", () => {
    const doc: DocumentV1 = {
      ...baseDoc,
      edges: [
        { id: "e1", fromId: "source-a1", toId: "canon-b", type: "related" },
        { id: "e2", fromId: "source-a2", toId: "canon-b", type: "related" },
        { id: "e3", fromId: "source-a1", toId: "source-b1", type: "related" },
        { id: "e4", fromId: "source-a2", toId: "source-a1", type: "related" },
      ],
    };

    const edges = getEdgesToRender(doc, true);

    expect(edges).toEqual([
      {
        id: "agg:card:canon-a|card:canon-b|related",
        fromId: "canon-a",
        toId: "canon-b",
        fromKind: "card",
        toKind: "card",
        type: "related",
        isDerived: true,
        aggregateCount: 3,
      },
    ]);
  });

  it("aggregates source-to-island edges", () => {
    const doc: DocumentV1 = {
      ...baseDoc,
      edges: [
        {
          id: "e-island",
          fromId: "source-a1",
          toId: "island-1",
          fromKind: "card",
          toKind: "island",
          type: "related",
        } as DocumentV1["edges"][number],
      ],
    };

    const edges = getEdgesToRender(doc, true);

    expect(edges).toEqual([
      {
        id: "agg:card:canon-a|island:island-1|related",
        fromId: "canon-a",
        toId: "island-1",
        fromKind: "card",
        toKind: "island",
        type: "related",
        isDerived: true,
        aggregateCount: 1,
      },
    ]);
  });
});
