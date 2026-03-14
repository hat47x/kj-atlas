import { afterEach, describe, expect, it, vi } from "vitest";

import { suggestMerges } from "./client";
import type { DocumentV2 } from "../domain/types";

function createDocument(): DocumentV2 {
  return {
    version: 2,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "Risk mitigation", x: 0, y: 0 },
      { id: "c2", text: "risk mitigation", x: 10, y: 0 },
    ],
    islands: [],
    edges: [],
  };
}

describe("suggestMerges contract validation", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("accepts a contract-valid candidate-group payload", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              candidateCardIds: ["c2"],
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
              rationale: "heuristic:normalized-text",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    const result = await suggestMerges(createDocument(), "collect candidates");

    expect(result.suggestions).toHaveLength(1);
    expect(result.suggestions[0]?.snapshotVersion).toBe("CTR-2B-01-CANDIDATE-GROUP-V1");
  });

  it("fails fast when snapshotVersion breaks the frozen contract", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              candidateCardIds: ["c2"],
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V2",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      name: "Error",
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });

  it("fails fast when required fields are missing", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(
        JSON.stringify({
          suggestions: [
            {
              groupId: "heuristic-risk-c1-c2",
              targetCardId: "c1",
              scoreSummary: { min: 1, max: 1, avg: 1 },
              reasonCodes: ["heuristic:normalized-text"],
              snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
              cardIds: ["c1", "c2"],
              mergedTextDraft: "Risk mitigation",
            },
          ],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } }
      )
    );

    await expect(suggestMerges(createDocument())).rejects.toMatchObject({
      message: "Invalid merge suggestions contract payload",
      status: 500,
    });
  });
});
