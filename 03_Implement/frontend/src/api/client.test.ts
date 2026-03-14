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

  it("preserves mock group order and targetCardId mapping under a fixed snapshotVersion", async () => {
    const responseBody = JSON.stringify({
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
        {
          groupId: "heuristic-timeline-c3-c4",
          targetCardId: "c3",
          candidateCardIds: ["c4"],
          scoreSummary: { min: 0.75, max: 0.75, avg: 0.75 },
          reasonCodes: ["heuristic:token-signature"],
          snapshotVersion: "CTR-2B-01-CANDIDATE-GROUP-V1",
          cardIds: ["c3", "c4"],
          mergedTextDraft: "Timeline review",
          rationale: "heuristic:token-signature",
        },
      ],
    });

    vi.spyOn(globalThis, "fetch")
      .mockResolvedValueOnce(new Response(responseBody, { status: 200, headers: { "Content-Type": "application/json" } }))
      .mockResolvedValueOnce(new Response(responseBody, { status: 200, headers: { "Content-Type": "application/json" } }));

    const first = await suggestMerges(createDocument(), "collect candidates");
    const second = await suggestMerges(createDocument(), "collect candidates");

    expect(first).toEqual(second);
    expect(first.suggestions.map((suggestion) => suggestion.groupId)).toEqual([
      "heuristic-risk-c1-c2",
      "heuristic-timeline-c3-c4",
    ]);
    expect(first.suggestions.map((suggestion) => suggestion.targetCardId)).toEqual(["c1", "c3"]);
    expect(first.suggestions.every((suggestion) => suggestion.snapshotVersion === "CTR-2B-01-CANDIDATE-GROUP-V1")).toBe(true);
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
