import { describe, expect, test } from "vitest";
import { parseDocumentJson } from "./document_import";

const BASE = {
  version: 1,
  id: "doc-p2a",
  createdAt: "2026-03-01T00:00:00.000Z",
  updatedAt: "2026-03-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "root", x: 0, y: 0 },
    { id: "c2", text: "child", x: 10, y: 10 },
    { id: "c3", text: "grand", x: 20, y: 20 },
  ],
  edges: [],
};

function parseWithIslands(islands: unknown) {
  return parseDocumentJson(JSON.stringify({ ...BASE, islands }));
}

describe("parseDocumentJson", () => {
  test("returns invalid json error", () => {
    const result = parseDocumentJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain("Invalid JSON in document.json");
    }
  });

  test("keeps valid parentIslandId hierarchy", () => {
    const result = parseWithIslands([
      { id: "root", cardIds: ["c1"] },
      { id: "child", cardIds: ["c2"], parentIslandId: "root" },
      { id: "grand", cardIds: ["c3"], parentIslandId: "child" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "child")?.parentIslandId).toBe("root");
      expect(result.document.islands.find((island) => island.id === "grand")?.parentIslandId).toBe("child");
    }
  });

  test("normalizes missing parentIslandId reference to undefined", () => {
    const result = parseWithIslands([
      { id: "root", cardIds: ["c1"] },
      { id: "orphan", cardIds: ["c2"], parentIslandId: "missing" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "orphan")?.parentIslandId).toBeUndefined();
    }
  });

  test("normalizes cycle parentIslandId references to undefined", () => {
    const result = parseWithIslands([
      { id: "a", cardIds: ["c1"], parentIslandId: "b" },
      { id: "b", cardIds: ["c2"], parentIslandId: "a" },
      { id: "c", cardIds: ["c3"], parentIslandId: "c" },
    ]);

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.islands.find((island) => island.id === "a")?.parentIslandId).toBeUndefined();
      expect(result.document.islands.find((island) => island.id === "b")?.parentIslandId).toBeUndefined();
      expect(result.document.islands.find((island) => island.id === "c")?.parentIslandId).toBeUndefined();
    }
  });

  test("preserves valid A1 contract-only fields during import normalization", () => {
    const result = parseDocumentJson(JSON.stringify({
      ...BASE,
      islands: [{ id: "i1", cardIds: ["c1"] }],
      critiqueInputs: [
        {
          schemaVersion: "1.0.0",
          critiqueId: "crit-1",
          targetRef: "island:i1",
          critiqueType: "feels_off",
          createdAt: "2026-03-01T00:01:00.000Z",
          iteration: 1,
        },
      ],
      reproposalDiffs: [
        {
          schemaVersion: "1.0.0",
          proposalId: "proposal-1",
          basedOnIteration: 1,
          traceKey: "trace:crit-1",
          diffOps: [
            {
              opId: "op-1",
              opType: "remove",
              targetRef: "card:c3",
              before: { id: "c3", text: "grand", x: 20, y: 20 },
              after: null,
            },
          ],
        },
      ],
      reviewAttribution: {
        schemaVersion: "1.0.0",
        reviewState: "unreviewed",
        reviewedAt: null,
        reviewerRef: "reviewer:opaque-1",
        auditRecordedAt: "2026-03-01T00:02:00.000Z",
        overridePolicy: "human_dual_control_only",
      },
      deterministicTieBreak: {
        schemaVersion: "1.0.0",
        order: [
          "padding_compliance",
          "self_intersection_avoidance",
          "minimum_area_delta",
          "minimum_vertex_count",
        ],
      },
    }));

    expect(result.ok).toBe(true);
    if (result.ok) {
      expect(result.document.critiqueInputs?.[0]?.targetRef).toBe("island:i1");
      expect(result.document.reproposalDiffs?.[0]?.diffOps[0]?.after).toBeNull();
      expect(result.document.reviewAttribution?.reviewState).toBe("unreviewed");
      expect(result.document.deterministicTieBreak?.order[0]).toBe("padding_compliance");
    }
  });
});
