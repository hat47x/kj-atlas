import { describe, expect, it } from "vitest";

import {
  buildRelationSummarySourceSignature,
  getGroundingCardIdsForRelationSummary,
  upsertRelationSummary,
} from "./relation_summary_ops";
import type { DocumentV2 } from "./types";

const baseDocument: DocumentV2 = {
  version: 2,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "A", x: 0, y: 0 },
    { id: "c2", text: "B", x: 10, y: 0 },
  ],
  edges: [{ id: "e1", fromId: "c1", toId: "c2", type: "related" }],
  islands: [
    { id: "i1", cardIds: ["c1"] },
    { id: "i2", cardIds: ["c2"] },
  ],
};

describe("relation_summary_ops", () => {
  it("builds deterministic source signatures", () => {
    const persisted = buildRelationSummarySourceSignature({
      edgeId: "e1",
      fromIslandId: "i1",
      toIslandId: "i2",
      type: "related",
      isDerived: false,
    });

    const derived = buildRelationSummarySourceSignature({
      edgeId: "derived",
      fromIslandId: "i1",
      toIslandId: "i2",
      type: "related",
      isDerived: true,
      contributingEdgeIds: ["e2", "e1"],
    });

    expect(persisted).toBe("edge:e1");
    expect(derived).toContain("derived:i1:i2:related:");
  });

  it("collects grounding cards for persisted relation", () => {
    const ids = getGroundingCardIdsForRelationSummary(baseDocument, {
      edgeId: "e1",
      fromIslandId: "i1",
      toIslandId: "i2",
      type: "related",
      isDerived: false,
    });

    expect(ids).toEqual(["c1", "c2"]);
  });

  it("upserts relation summary by source signature", () => {
    const first = upsertRelationSummary(baseDocument, {
      id: "r1",
      createdAt: "2026-01-01T00:00:00.000Z",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      text: "draft",
      reviewed: false,
      groundingCardIds: ["c1"],
      groundingEdgeIds: ["e1"],
      sourceSignature: "edge:e1",
    });

    const second = upsertRelationSummary(first, {
      ...first.relationSummaries![0],
      text: "edited",
      reviewed: true,
    });

    expect(second.relationSummaries).toHaveLength(1);
    expect(second.relationSummaries?.[0].text).toBe("edited");
    expect(second.relationSummaries?.[0].reviewed).toBe(true);
  });
});
