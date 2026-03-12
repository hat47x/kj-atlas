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
        schemaVersion: "1.0.0",
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
        schemaVersion: "1.0.0",
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
        schemaVersion: "1.0.0",
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
        schemaVersion: "1.0.0",
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
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        reviewContext: "internal",
      }),
    ).toBe(true);

    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: null,
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
      }),
    ).toBe(false);

    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "unreviewed",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
      }),
    ).toBe(false);

    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "unreviewed",
        reviewedAt: null,
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
      }),
    ).toBe(true);
  });

  it("rejects review attribution payload containing PII-like identity fields", () => {
    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        email: "reviewer@example.com",
      }),
    ).toBe(false);
  });

  it("rejects review attribution override policy violations", () => {
    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "ai_only_override",
        reviewerRef: "user:local:abc",
      }),
    ).toBe(false);
  });
  it("rejects critique payload with unsupported schemaVersion", () => {
    expect(
      validateHilRsCritiqueInput({
        schemaVersion: "2.0.0",
        critiqueId: "crit-5",
        targetRef: "card:c5",
        critiqueType: "too_far",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 1,
      }),
    ).toBe(false);
  });
});
