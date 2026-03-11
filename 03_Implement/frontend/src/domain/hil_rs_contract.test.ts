import { describe, expect, it } from "vitest";

import {
  validateHilRsCritiqueInput,
  validateHilRsRediffPayload,
  validateHilRsReviewAttribution,
} from "./hil_rs_contract";

describe("hil_rs_contract validators", () => {
  it("accepts valid critique input and rejects unknown critique type", () => {
    expect(
      validateHilRsCritiqueInput({
        critiqueId: "crit-1",
        targetRef: "card:c1",
        critiqueType: "feels_off",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 2,
        comment: "layout feels off",
        constraintHints: ["keep-distance", "preserve-order"],
      }),
    ).toBe(true);

    expect(
      validateHilRsCritiqueInput({
        critiqueId: "crit-2",
        targetRef: "card:c2",
        critiqueType: "belongs_together",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 1,
      }),
    ).toBe(false);
  });

  it("rejects critique payload containing PII-like identity fields", () => {
    expect(
      validateHilRsCritiqueInput({
        critiqueId: "crit-3",
        targetRef: "card:c3",
        critiqueType: "too_close",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 1,
        email: "test@example.com",
      }),
    ).toBe(false);
  });


  it("rejects critique payload that attempts review state mutation fields", () => {
    expect(
      validateHilRsCritiqueInput({
        critiqueId: "crit-4",
        targetRef: "card:c4",
        critiqueType: "too_far",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 1,
        reviewState: "human_reviewed",
      }),
    ).toBe(false);
  });

  it("accepts reversible rediff payload and rejects irreversible ops", () => {
    expect(
      validateHilRsRediffPayload({
        proposalId: "proposal-1",
        basedOnIteration: 1,
        traceKey: "trace-crit-1",
        diffOps: [
          {
            opId: "op-1",
            opType: "move",
            targetRef: "card:c1",
            before: { x: 0, y: 0 },
            after: { x: 100, y: 80 },
          },
          {
            opId: "op-2",
            opType: "add",
            targetRef: "edge:e1",
            before: null,
            after: { id: "e1" },
            rationale: "connect related cards",
          },
        ],
      }),
    ).toBe(true);

    expect(
      validateHilRsRediffPayload({
        proposalId: "proposal-2",
        basedOnIteration: 2,
        traceKey: "trace-crit-2",
        diffOps: [
          {
            opId: "op-3",
            opType: "move",
            targetRef: "card:c2",
            before: null,
            after: null,
          },
        ],
      }),
    ).toBe(false);
  });

  it("enforces review attribution state transition requirements", () => {
    expect(
      validateHilRsReviewAttribution({
        reviewState: "human_reviewed",
        reviewerRef: "user:local:abc",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        reviewContext: "internal",
      }),
    ).toBe(true);

    expect(
      validateHilRsReviewAttribution({
        reviewState: "human_reviewed",
        reviewerRef: "user:local:abc",
      }),
    ).toBe(false);

    expect(
      validateHilRsReviewAttribution({
        reviewState: "unreviewed",
        reviewerRef: "user:local:abc",
        reviewedAt: "2026-03-11T09:00:00.000Z",
      }),
    ).toBe(false);
  });

  it("rejects review attribution payload containing PII-like identity fields", () => {
    expect(
      validateHilRsReviewAttribution({
        reviewState: "human_reviewed",
        reviewerRef: "user:local:abc",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        email: "reviewer@example.com",
      }),
    ).toBe(false);
  });
});
