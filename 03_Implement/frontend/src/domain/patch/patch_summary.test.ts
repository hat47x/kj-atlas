import { describe, expect, it } from "vitest";

import type { PatchDocument } from "./patch_apply";
import { buildPatchSummary, formatPatchSummaryMarkdown } from "./patch_summary";

describe("patch_summary", () => {
  it("builds deterministic stats, highlights, and warnings", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "4", kind: "upsert_card", card: { id: "card-b", text: "Card B detail", x: 0, y: 0 } },
        { id: "3", kind: "upsert_relation_summary", relationSummary: { id: "r1", createdAt: "2024-01-01", islandAId: "a", islandBId: "b", relationType: "related", derived: false, text: "Relation summary text", reviewed: false, groundingCardIds: [], groundingEdgeIds: [], sourceSignature: "sig-b" } },
        { id: "2", kind: "upsert_island", island: { id: "island-a", cardIds: [], title: "Island A", summaryText: "Summary A" } },
        { id: "1", kind: "delete_island", islandId: "island-z" },
      ],
    };

    const summary = buildPatchSummary(
      patch,
      {
        conflicts: [
          {
            opId: "4",
            kind: "upsert_card",
            entityKey: "card:card-b",
            baseValue: null,
            yourValue: { id: "card-b", text: "old", x: 0, y: 0 },
            theirValue: { id: "card-b", text: "new", x: 0, y: 0 },
            reason: "both modified",
          },
        ],
        nonConflictingOpIds: ["3", "2", "1"],
      },
      false,
      false
    );

    expect(summary.headline).toBe("Patch: 1 card updated, 1 island added, 1 island deleted");
    expect(summary.stats.upsertCards).toBe(1);
    expect(summary.stats.upsertIslands).toBe(1);
    expect(summary.stats.deleteIslands).toBe(1);
    expect(summary.stats.upsertRelationSummaries).toBe(1);
    expect(summary.highlights.map((item) => item.label)).toEqual(["Island island-a", "Island island-z", "Relation sig-b", "Card card-b"]);
    expect(summary.warnings).toEqual([
      "Base signature mismatch: loaded patch baseline does not match the current document.",
      "1 conflict(s) detected in patch operations.",
    ]);
  });

  it("formats markdown with optional warnings section", () => {
    const markdown = formatPatchSummaryMarkdown({
      headline: "Patch: no changes",
      stats: {
        upsertCards: 0,
        deleteCards: 0,
        upsertIslands: 0,
        deleteIslands: 0,
        upsertEdges: 0,
        deleteEdges: 0,
        upsertRelationSummaries: 0,
        deleteRelationSummaries: 0,
        upsertEvidenceLinks: 0,
        deleteEvidenceLinks: 0,
      },
      highlights: [],
      warnings: [],
    });

    expect(markdown).toContain("## Summary");
    expect(markdown).toContain("## Stats");
    expect(markdown).toContain("## Highlights");
    expect(markdown).not.toContain("## Warnings");
  });

  it("masks card, island, and relation text in highlights under SafeMode (default)", () => {
    const patch: PatchDocument = {
      kind: "kj-atlas-patch",
      version: 1,
      ops: [
        { id: "1", kind: "upsert_card", card: { id: "card-b", text: "Card B detail", x: 0, y: 0 } },
        { id: "2", kind: "upsert_relation_summary", relationSummary: { id: "r1", createdAt: "2024-01-01", islandAId: "a", islandBId: "b", relationType: "related", derived: false, text: "Relation summary text", reviewed: false, groundingCardIds: [], groundingEdgeIds: [], sourceSignature: "sig-b" } },
        { id: "3", kind: "upsert_island", island: { id: "island-a", cardIds: [], title: "Island A", summaryText: "Summary A" } },
      ],
    };

    const maskedByDefault = buildPatchSummary(patch);
    const maskedExplicit = buildPatchSummary(patch, undefined, undefined, true);

    for (const summary of [maskedByDefault, maskedExplicit]) {
      const detailsByLabel = new Map(summary.highlights.map((item) => [item.label, item.detail]));
      expect(detailsByLabel.get("Card card-b")).not.toContain("Card B detail");
      expect(detailsByLabel.get("Card card-b")).toContain("[REDACTED]");
      expect(detailsByLabel.get("Relation sig-b")).not.toContain("Relation summary text");
      expect(detailsByLabel.get("Relation sig-b")).toContain("[REDACTED]");
      expect(detailsByLabel.get("Island island-a")).toContain("Island A");
      expect(detailsByLabel.get("Island island-a")).not.toContain("Summary A");
      expect(detailsByLabel.get("Island island-a")).toContain("[REDACTED]");
    }
  });
});
