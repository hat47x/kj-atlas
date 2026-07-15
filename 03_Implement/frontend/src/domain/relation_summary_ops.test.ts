import { describe, expect, it } from "vitest";

import {
  buildRelationSummarySourceSignature,
  getGroundingCardIdsForRelationSummary,
  upsertRelationSummary,
  upsertRelationSummaryWithHistory,
  RELATION_SUMMARY_TEXT_MAX_LENGTH,
} from "./relation_summary_ops";
import type { DocumentV1 } from "./types";

const baseDocument: DocumentV1 = {
  version: 1,
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

  it("records AI, manual, and rollback history entries", () => {
    const aiDraft = upsertRelationSummaryWithHistory(baseDocument, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "AI draft",
      newWarnings: ["check nuance"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "ai",
      newReviewed: true,
    });

    expect(aiDraft.relationSummaries?.[0].reviewed).toBe(false);
    expect(aiDraft.relationSummaries?.[0].history).toHaveLength(1);
    expect(aiDraft.relationSummaries?.[0].history?.[0].changeKind).toBe("ai");

    const manualEdit = upsertRelationSummaryWithHistory(aiDraft, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "Manual edit",
      newWarnings: ["check nuance"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "manual",
    });

    expect(manualEdit.relationSummaries?.[0].reviewed).toBe(true);
    expect(manualEdit.relationSummaries?.[0].history).toHaveLength(2);
    expect(manualEdit.relationSummaries?.[0].history?.[1].changeKind).toBe("manual");

    const rollback = upsertRelationSummaryWithHistory(manualEdit, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "AI draft",
      newWarnings: ["check nuance"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "rollback",
      note: "restore:test",
    });

    expect(rollback.relationSummaries?.[0].history).toHaveLength(3);
    expect(rollback.relationSummaries?.[0].history?.[2].changeKind).toBe("rollback");
    expect(rollback.relationSummaries?.[0].history?.[2].note).toBe("restore:test");
  });

  it("does not append history when text/reviewed/warnings are unchanged", () => {
    const initial = upsertRelationSummaryWithHistory(baseDocument, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "Stable",
      newWarnings: ["warn"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "ai",
    });

    const unchanged = upsertRelationSummaryWithHistory(initial, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "Stable",
      newWarnings: ["warn"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "manual",
      newReviewed: false,
    });

    expect(unchanged).toBe(initial);
    expect(unchanged.relationSummaries?.[0].history).toHaveLength(1);
  });


  it("caps relation summary text length before persisting", () => {
    const longText = "x".repeat(RELATION_SUMMARY_TEXT_MAX_LENGTH + 25);
    const result = upsertRelationSummaryWithHistory(baseDocument, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: longText,
      newWarnings: [],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "ai",
    });

    const savedText = result.relationSummaries?.[0].text ?? "";
    expect(savedText.length).toBe(RELATION_SUMMARY_TEXT_MAX_LENGTH);
    expect(result.relationSummaries?.[0].history?.[0].toText?.length).toBe(RELATION_SUMMARY_TEXT_MAX_LENGTH);
  });


  it("updates grounding metadata without appending history when text/reviewed/warnings are unchanged", () => {
    const initial = upsertRelationSummaryWithHistory(baseDocument, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "Stable",
      newWarnings: ["warn"],
      newGroundingCardIds: ["c1", "c2"],
      newGroundingEdgeIds: ["e1"],
      changeKind: "ai",
    });

    const updatedGrounding = upsertRelationSummaryWithHistory(initial, {
      sourceSignature: "edge:e1",
      islandAId: "i1",
      islandBId: "i2",
      relationType: "related",
      derived: false,
      newText: "Stable",
      newWarnings: ["warn"],
      newGroundingCardIds: ["c1"],
      newGroundingEdgeIds: ["e1", "e2"],
      changeKind: "manual",
      newReviewed: false,
    });

    expect(updatedGrounding).not.toBe(initial);
    expect(updatedGrounding.relationSummaries?.[0].groundingCardIds).toEqual(["c1"]);
    expect(updatedGrounding.relationSummaries?.[0].groundingEdgeIds).toEqual(["e1", "e2"]);
    expect(updatedGrounding.relationSummaries?.[0].history).toHaveLength(1);
    expect(updatedGrounding.relationSummaries?.[0].history?.[0].changeKind).toBe("ai");
  });

  it("trims history to max 50 entries", () => {
    let doc = baseDocument;
    for (let i = 0; i < 55; i += 1) {
      doc = upsertRelationSummaryWithHistory(doc, {
        sourceSignature: "edge:e1",
        islandAId: "i1",
        islandBId: "i2",
        relationType: "related",
        derived: false,
        newText: `v${i}`,
        newWarnings: [],
        newGroundingCardIds: ["c1", "c2"],
        newGroundingEdgeIds: ["e1"],
        changeKind: i === 0 ? "ai" : "manual",
      });
    }

    const history = doc.relationSummaries?.[0].history ?? [];
    expect(history).toHaveLength(50);
    expect(history[history.length - 1].toText).toBe("v54");
  });
});
