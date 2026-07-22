import { describe, expect, it } from "vitest";

import { buildRelationSummarySourceSignature } from "../domain/relation_summary_ops";
import type { DocumentV1 } from "../domain/types";
import { buildAbstractMapExport, exportAbstractMapHTML, exportAbstractMapMarkdown } from "./abstract_map_export";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc_1",
    title: "Doc",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-03T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "c1",
        text: "Card one text for grounding. ".repeat(12),
        x: 0,
        y: 0,
        mergedIntoCardId: "c4",
      },
      { id: "c2", text: "Card two text", x: 0, y: 0, mergedIntoCardId: "c4" },
      { id: "c3", text: "Card three text", x: 0, y: 0, canonicalId: "c2" },
      { id: "c4", text: "Representative text", x: 0, y: 0, repOf: ["c1", "c2"] },
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
  it("builds deterministic export model and stays pure", () => {
    const doc = createDocument();
    const viewState = { visibleIslandIds: new Set(["i1", "i2"]), abstractMapView: true, safeMode: false };

    const first = buildAbstractMapExport(doc, viewState);
    const second = buildAbstractMapExport(doc, viewState);

    expect(first).toEqual(second);
    expect(doc.transform).toEqual({ panX: 0, panY: 0, zoom: 1 });
    expect(doc.updatedAt).toBe("2026-01-03T00:00:00.000Z");
  });

  it("includes reviewed flags, derived labels, and grounding snippets", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      safeMode: false,
    });

    expect(model.islands.find((item) => item.id === "i1")?.summaryReviewed).toBe(false);
    expect(model.islands.find((item) => item.id === "i2")?.summaryReviewed).toBe(true);
    expect(model.relations.some((item) => item.derived)).toBe(true);

    const snippet = model.relations
      .flatMap((item) => item.groundingCards ?? [])
      .find((item) => item.id === "c1")?.snippet;
    expect(snippet).toBeDefined();
    expect(snippet?.length).toBeLessThanOrEqual(160);
  });

  it("does not include derived relations when abstractMapView is off", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: false,
      safeMode: false,
    });

    expect(model.relations.some((item) => item.derived)).toBe(false);
  });


  it("excludes unreviewed summary drafts when includeUnreviewedDrafts is disabled", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      includeUnreviewedDrafts: false,
      safeMode: false,
    });

    expect(model.islands.find((item) => item.id === "i1")?.summaryText).toBe("UNREVIEWED hidden");
    expect(model.relations.some((item) => item.summaryText === "Derived summary")).toBe(false);
  });

  it("defaults to excluding unreviewed summary drafts", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      safeMode: false,
    });

    expect(model.islands.find((item) => item.id === "i1")?.summaryText).toBe("UNREVIEWED hidden");
    expect(model.relations.some((item) => item.summaryText === "Derived summary")).toBe(false);
  });

  it("renders markdown/html with reviewed semantics and draft template text", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      includeUnreviewedDrafts: true,
      safeMode: false,
    });

    const markdown = exportAbstractMapMarkdown(model);
    const html = exportAbstractMapHTML(model);

    expect(markdown).toContain("Reviewed semantics");
    expect(markdown).toContain("UNREVIEWED");
    expect(markdown).toContain("derived");
    expect(markdown).toContain("Grounding cards:");
    expect(markdown).toContain("Grounding edge IDs:");
    expect(markdown).toContain("Summary (UNREVIEWED draft template)");
    expect(markdown).toContain("## Representative cards");
    expect(markdown).toContain("Rep count: 2");

    expect(html).toContain("Reviewed semantics");
    expect(html).toContain("UNREVIEWED");
    expect(html).toContain("derived");
    expect(html).toContain("Grounding cards:");
    expect(html).toContain("Grounding edge IDs:");
    expect(html).toContain("Summary (UNREVIEWED draft template)");
    expect(html).toContain("Representative cards");
  });

  it("embeds snapshot references in markdown/html exports", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      safeMode: false,
    });

    const markdown = exportAbstractMapMarkdown(model, { snapshotFilename: "snapshot.png" });
    const html = exportAbstractMapHTML(model, { snapshotDataUrl: "data:image/png;base64,abc" });

    expect(markdown).toContain("![Abstract Map Snapshot](snapshot.png)");
    expect(html).toContain('<img src="data:image/png;base64,abc"');
    expect(html).toContain("Abstract Map Snapshot");
  });

  it("masks island summary, relation summary, grounding snippets, and representative text under SafeMode (default)", () => {
    const model = buildAbstractMapExport(createDocument(), {
      visibleIslandIds: new Set(["i1", "i2"]),
      abstractMapView: true,
      includeUnreviewedDrafts: true,
    });

    const reviewedIsland = model.islands.find((item) => item.id === "i2");
    expect(reviewedIsland?.summaryReviewed).toBe(true);
    expect(reviewedIsland?.summaryText).toBe("UNREVIEWED hidden");

    const persistedRelation = model.relations.find((item) => !item.derived && item.type === "related");
    expect(persistedRelation?.summaryText).toBeUndefined();

    const snippet = model.relations
      .flatMap((item) => item.groundingCards ?? [])
      .find((item) => item.id === "c1")?.snippet;
    expect(snippet).toMatch(/^\[REDACTED\]/);

    const representative = model.representatives.find((item) => item.representativeCardId === "c4");
    expect(representative?.representativeText).toMatch(/^\[REDACTED\]/);
  });

});
