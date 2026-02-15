import { describe, expect, it } from "vitest";

import { buildRelationSummarySourceSignature } from "../domain/relation_summary_ops";
import type { DocumentV2 } from "../domain/types";
import { buildAbstractMapExport, exportAbstractMapHTML, exportAbstractMapMarkdown } from "./abstract_map_export";

function createDocument(): DocumentV2 {
  return {
    version: 2,
    id: "doc_1",
    title: "Doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Card one text for grounding", x: 0, y: 0 },
      { id: "c2", text: "Card two text", x: 0, y: 0 },
      { id: "c3", text: "Card three text", x: 0, y: 0, canonicalId: "c2" },
    ],
    edges: [
      { id: "e1", fromId: "i1", toId: "i2", fromKind: "island", toKind: "island", type: "related" },
      { id: "e2", fromId: "c1", toId: "c2", type: "negate" },
      { id: "e3", fromId: "i1", toId: "i2", fromKind: "island", toKind: "island", type: "negate" },
    ],
    islands: [
      { id: "i1", cardIds: ["c1", "c3"], title: "Alpha", summaryText: "Island summary A", summaryReviewed: false },
      { id: "i2", cardIds: ["c2"], title: "Beta", summaryText: "Island summary B", summaryReviewed: true },
    ],
    relationSummaries: [
      {
        id: "rs1",
        createdAt: "2026-01-03T00:00:00.000Z",
        islandAId: "i1",
        islandBId: "i2",
        relationType: "related",
        derived: false,
        text: "Persisted summary",
        reviewed: true,
        groundingCardIds: ["c1"],
        groundingEdgeIds: ["e1"],
        sourceSignature: "edge:e1",
      },
      {
        id: "rs2",
        createdAt: "2026-01-03T00:00:00.000Z",
        islandAId: "i1",
        islandBId: "i2",
        relationType: "negate",
        derived: true,
        text: "Derived summary",
        reviewed: false,
        groundingCardIds: ["c1", "c2"],
        groundingEdgeIds: ["e2"],
        sourceSignature: buildRelationSummarySourceSignature({
          edgeId: "derived-island:i1|i2|negate",
          fromIslandId: "i1",
          toIslandId: "i2",
          type: "negate",
          isDerived: true,
          contributingEdgeIds: ["e2"],
          contributingCardIds: ["c1", "c2"],
        }),
      },
    ],
    readingOrder: [],
    narratives: [],
  };
}

describe("abstract map export", () => {
  it("builds deterministic export model with reviewed labels and grounding snippets", () => {
    const doc = createDocument();
    const viewState = { visibleIslandIds: new Set(["i1", "i2"]), abstractMapView: true };

    const first = buildAbstractMapExport(doc, viewState);
    const second = buildAbstractMapExport(doc, viewState);

    expect(first).toEqual(second);
    expect(first.generatedAt).toBe(doc.updatedAt);
    expect(first.islands[0].summaryReviewed).toBe(false);
    expect(first.relations.some((item) => item.derived)).toBe(true);
    const firstGroundedRelation = first.relations.find((item) => (item.groundingCards ?? []).length > 0);
    expect(firstGroundedRelation?.groundingCards?.[0].snippet).toContain("Card");
  });

  it("renders markdown/html with derived and unreviewed labels", () => {
    const doc = createDocument();
    const model = buildAbstractMapExport(doc, { visibleIslandIds: new Set(["i1", "i2"]), abstractMapView: true });

    const markdown = exportAbstractMapMarkdown(model, { snapshotFilename: "snapshot.png" });
    const html = exportAbstractMapHTML(model, { snapshotDataUrl: "data:image/png;base64,abc123" });

    expect(markdown).toContain("![Abstract Map Snapshot](snapshot.png)");
    expect(markdown).toContain("UNREVIEWED");
    expect(markdown).toContain("derived");
    expect(markdown).toContain("Grounding cards:");
    expect(markdown).toContain("Grounding edge IDs:");
    expect(markdown).toContain("Summary (UNREVIEWED draft template)");
    expect(html).toContain("Abstract Map Snapshot");
    expect(html).toContain("data:image/png;base64,abc123");
    expect(html).toContain("UNREVIEWED");
    expect(html).toContain("derived");
    expect(html).toContain("Grounding cards:");
    expect(html).toContain("Grounding edge IDs:");
  });
});
