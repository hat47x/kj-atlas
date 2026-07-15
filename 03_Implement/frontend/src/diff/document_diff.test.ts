import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { buildMergeItems, finalizeMergeItems } from "./merge_items";
import { computeDocumentDiff, flattenDocumentDiff } from "./document_diff";
import { computeViewDiff } from "./view_diff";

function doc(overrides: Partial<DocumentV1>): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2025-01-01T00:00:00.000Z",
    updatedAt: "2025-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    relationSummaries: [],
    evidenceLinks: [],
    ...overrides,
  };
}

describe("document/view diff", () => {
  it("matches the previous merge item output (golden parity)", () => {
    const base = doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] });
    const incoming = doc({
      cards: [{ id: "c1", text: "A+", x: 0, y: 0 }, { id: "c2", text: "B", x: 10, y: 10 }],
      islands: [{ id: "i1", cardIds: ["c1", "c2"] }],
      edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "related" }],
      evidenceLinks: [{ id: "ev1", type: "supports", fromCardId: "c1", toCardId: "c2" }],
      readingOrder: ["c2", "c1"],
    });

    const previous = buildMergeItems(base, incoming);
    const next = finalizeMergeItems(base, flattenDocumentDiff(computeDocumentDiff(base, incoming)), computeViewDiff(base, incoming));

    expect(next).toEqual(previous);
  });

  it("is deterministic", () => {
    const base = doc({ cards: [{ id: "z", text: "Z", x: 0, y: 0 }] });
    const incoming = doc({ cards: [{ id: "a", text: "A", x: 0, y: 0 }, { id: "z", text: "Z+", x: 0, y: 0 }] });
    const first = flattenDocumentDiff(computeDocumentDiff(base, incoming)).map((item) => item.id);
    const second = flattenDocumentDiff(computeDocumentDiff(base, incoming)).map((item) => item.id);
    expect(first).toEqual(second);
  });
});
