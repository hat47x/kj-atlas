import { describe, expect, it } from "vitest";
import { buildHilRsCritiqueInputs, createHilRsReviewAttribution } from "./hil_rs_payload";
import type { DocumentV2 } from "./types";

const BASE_DOC: DocumentV2 = {
  version: 2,
  cards: [
    { id: "c1", text: "alpha", x: 0, y: 0, critique: "too close", critiqueTags: ["too_close"] },
    { id: "c2", text: "beta", x: 10, y: 10, critiqueTags: ["unclear_boundary"] },
  ],
  islands: [{ id: "i1", title: "island", cardIds: ["c1"], critique: "needs split", critiqueTags: ["not_the_same"] }],
  edges: [],
  reviewEvents: [],
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
};

describe("hil_rs_payload", () => {
  it("builds A1-compliant critique payloads from card/island critiques", () => {
    const result = buildHilRsCritiqueInputs(BASE_DOC, {
      iteration: 2,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    expect(result).toHaveLength(3);
    expect(result[0]).toMatchObject({
      targetRef: "card:c1",
      critiqueType: "too_close",
      iteration: 2,
    });
    expect(result[1]).toMatchObject({
      targetRef: "card:c2",
      critiqueType: "no_articulable_reason",
      constraintHints: ["unclear_boundary"],
    });
    expect(result[2]).toMatchObject({
      targetRef: "island:i1",
      critiqueType: "not_the_same",
    });
  });

  it("returns empty list for invalid iteration", () => {
    const result = buildHilRsCritiqueInputs(BASE_DOC, {
      iteration: 0,
      createdAt: "2026-03-11T00:00:00.000Z",
    });

    expect(result).toEqual([]);
  });

  it("creates review attribution only when A1-ATTR-IF is valid", () => {
    expect(
      createHilRsReviewAttribution({
        reviewState: "human_reviewed",
        reviewedAt: "2026-03-11T00:00:00.000Z",
        reviewerRef: "reviewer-1",
        reviewContext: "internal",
      }),
    ).not.toBeNull();

    expect(
      createHilRsReviewAttribution({
        reviewState: "human_reviewed",
        reviewerRef: "reviewer-1",
      }),
    ).toBeNull();
  });
});
