import { describe, expect, it } from "vitest";
import { buildHilRsCritiqueInputs, createHilRsReviewAttribution } from "./hil_rs_payload";
import type { DocumentV2 } from "./types";

const BASE_DOC: DocumentV2 = {
  version: 2,
  id: "doc",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    { id: "c1", text: "alpha", x: 0, y: 0, critique: "too close", critiqueTags: ["too_close"] },
    { id: "c2", text: "beta", x: 10, y: 10, critiqueTags: ["unclear_boundary"] },
  ],
  islands: [{ id: "i1", title: "island", cardIds: ["c1"], critique: "needs split", critiqueTags: ["not_the_same"] }],
  edges: [],
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



  it("normalizes critique tags by trimming whitespace before mapping critiqueType", () => {
    const result = buildHilRsCritiqueInputs(
      {
        ...BASE_DOC,
        cards: [{ id: "c9", text: "delta", x: 0, y: 0, critiqueTags: ["  too_far  "] }],
        islands: [],
      },
      {
        iteration: 1,
        createdAt: "2026-03-11T00:00:00.000Z",
      },
    );

    expect(result).toHaveLength(1);
    expect(result[0]).toMatchObject({
      targetRef: "card:c9",
      critiqueType: "too_far",
      constraintHints: ["too_far"],
    });
  });

  it("maps every first-class critique type without changing the schema", () => {
    const result = buildHilRsCritiqueInputs(
      {
        ...BASE_DOC,
        cards: [
          { id: "c1", text: "one", x: 0, y: 0, critiqueTags: ["not_the_same"] },
          { id: "c2", text: "two", x: 10, y: 0, critiqueTags: ["feels_off"] },
          { id: "c3", text: "three", x: 20, y: 0, critiqueTags: ["no_articulable_reason"] },
        ],
        islands: [],
      },
      {
        iteration: 3,
        createdAt: "2026-06-23T00:00:00.000Z",
      },
    );

    expect(result.map((item) => item.critiqueType)).toEqual([
      "not_the_same",
      "feels_off",
      "no_articulable_reason",
    ]);
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
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: "2026-03-11T00:00:00.000Z",
        auditRecordedAt: "2026-03-11T00:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "reviewer-1",
        reviewContext: "internal",
      }),
    ).not.toBeNull();

    expect(
      createHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: null,
        auditRecordedAt: "2026-03-11T00:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "reviewer-1",
      }),
    ).toBeNull();
  });
});
