import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "./types";
import { detectVoidCandidates } from "./void_detection";

const NOW = "2026-08-14T00:00:00.000Z";

function buildDoc(): DocumentV1 {
  return {
    version: 1,
    id: "doc-voids",
    createdAt: "2026-08-14T00:00:00.000Z",
    updatedAt: "2026-08-14T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "alpha", x: 0, y: 0 },
      { id: "c2", text: "beta", x: 10, y: 10 },
      { id: "c3", text: "lone", x: 500, y: 500 },
    ],
    edges: [
      { id: "e1", fromId: "i1", toId: "i2", fromKind: "island", toKind: "island", type: "related" },
    ],
    islands: [
      { id: "i1", cardIds: ["c1"], title: "A", summaryText: "s", summaryReviewed: true },
      { id: "i2", cardIds: ["c2"], title: "B", summaryText: "", summaryReviewed: false },
    ],
    relationSummaries: [],
  };
}

describe("detectVoidCandidates", () => {
  it("detects unintegrated cards, unspoken islands, unexplained relations, unreviewed content", () => {
    const result = detectVoidCandidates(buildDoc(), { nowIso: NOW });

    const kinds = result.voids.map((v) => v.kind);
    // c3 is lone; i2 has empty summary (unspoken) and is unreviewed; i1-i2 are
    // connected but have no relation summary (unexplained). i2 has a connection
    // so it is not orphaned.
    expect(kinds).toContain("unintegrated_card");
    expect(kinds).toContain("unspoken_island");
    expect(kinds).toContain("unexplained_relation");
    expect(kinds).toContain("unreviewed_content");
    expect(kinds).not.toContain("orphaned_island");
    expect(result.warning).toBeNull();

    const unintegrated = result.voids.find((v) => v.kind === "unintegrated_card");
    expect(unintegrated?.cardIds).toEqual(["c3"]);
  });

  it("detects orphaned islands when an island has no island-to-island connection", () => {
    const doc = buildDoc();
    // Remove the i1<->i2 edge so both islands are isolated.
    doc.edges = [];
    const result = detectVoidCandidates(doc, { nowIso: NOW });
    expect(result.voids.some((v) => v.kind === "orphaned_island")).toBe(true);
  });

  it("warns when zero voids are found despite content being present", () => {
    // A fully articulated, connected, reviewed pair of islands with a relation
    // summary: no structural gap remains, so zero voids is itself a warning.
    const doc: DocumentV1 = {
      version: 1,
      id: "doc-complete",
      createdAt: "2026-08-14T00:00:00.000Z",
      updatedAt: "2026-08-14T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "alpha", x: 0, y: 0 },
        { id: "c2", text: "beta", x: 10, y: 10 },
      ],
      edges: [
        { id: "e1", fromId: "i1", toId: "i2", fromKind: "island", toKind: "island", type: "related" },
      ],
      islands: [
        { id: "i1", cardIds: ["c1"], title: "A", summaryText: "s", summaryReviewed: true },
        { id: "i2", cardIds: ["c2"], title: "B", summaryText: "t", summaryReviewed: true },
      ],
      relationSummaries: [
        {
          id: "rs1",
          createdAt: NOW,
          islandAId: "i1",
          islandBId: "i2",
          relationType: "related",
          derived: false,
          text: "why",
          reviewed: true,
          groundingCardIds: ["c1", "c2"],
          groundingEdgeIds: ["e1"],
          sourceSignature: "sig-1",
        },
      ],
    };

    const result = detectVoidCandidates(doc, { nowIso: NOW });
    expect(result.voids).toHaveLength(0);
    expect(result.warning).toContain("空白がゼロ件");
  });

  it("does not warn when there is no content at all", () => {
    const doc: DocumentV1 = {
      version: 1,
      id: "doc-empty",
      createdAt: "2026-08-14T00:00:00.000Z",
      updatedAt: "2026-08-14T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [],
      edges: [],
      islands: [],
    };

    const result = detectVoidCandidates(doc, { nowIso: NOW });
    expect(result.voids).toHaveLength(0);
    expect(result.warning).toBeNull();
  });
});
