import { describe, expect, it } from "vitest";

import {
  validateHilRsContractErrorEnvelope,
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



  it("rejects critique payload with extra non-contract fields (A1-CRITIQUE-IF)", () => {
    expect(
      validateHilRsCritiqueInput({
        schemaVersion: "1.0.0",
        critiqueId: "crit-extra-1",
        targetRef: "card:c6",
        critiqueType: "too_close",
        createdAt: "2026-03-11T09:00:00.000Z",
        iteration: 1,
        unexpected: "not-allowed",
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
        schemaVersion: "1.0.0",
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
        schemaVersion: "1.0.0",
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


  it("rejects rediff payload with extra top-level fields (A1-REDIFF-IF)", () => {
    expect(
      validateHilRsRediffPayload({
        schemaVersion: "1.0.0",
        proposalId: "proposal-extra-1",
        basedOnIteration: 2,
        traceKey: "trace-extra-1",
        extra: true,
        diffOps: [
          {
            opId: "op-extra-1",
            opType: "move",
            targetRef: "card:c2",
            before: { x: 0, y: 0 },
            after: { x: 1, y: 1 },
          },
        ],
      }),
    ).toBe(false);
  });

  it("rejects rediff payloads that attempt to mutate review protections", () => {
    expect(
      validateHilRsRediffPayload({
        schemaVersion: "1.0.0",
        proposalId: "proposal-review-injection",
        basedOnIteration: 1,
        traceKey: "trace-review-injection",
        diffOps: [
          {
            opId: "op-review-injection",
            opType: "add",
            targetRef: "card:c2",
            before: null,
            after: { id: "c2", text: "beta", x: 10, y: 20, textReviewed: true },
          },
        ],
      }),
    ).toBe(false);

    expect(
      validateHilRsRediffPayload({
        schemaVersion: "1.0.0",
        proposalId: "proposal-nested-review-injection",
        basedOnIteration: 1,
        traceKey: "trace-nested-review-injection",
        diffOps: [
          {
            opId: "op-nested-review-injection",
            opType: "relabel",
            targetRef: "island:i1",
            before: { metadata: { reviewState: "unreviewed" } },
            after: { metadata: { reviewState: "human_reviewed" } },
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


  it("rejects review attribution payload with extra fields (A1-ATTR-IF)", () => {
    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        reviewedAt: "2026-03-11T09:00:00.000Z",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "user:local:abc",
        extraAuditFlag: true,
      }),
    ).toBe(false);
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

    expect(
      validateHilRsReviewAttribution({
        schemaVersion: "1.0.0",
        reviewState: "human_reviewed",
        auditRecordedAt: "2026-03-11T09:01:00.000Z",
        overridePolicy: "human_dual_control_only",
        reviewerRef: "reviewer@example.com",
        reviewedAt: "2026-03-11T09:00:00.000Z",
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

  it("validates A1-ERROR-IF envelope", () => {
    expect(
      validateHilRsContractErrorEnvelope({
        schemaVersion: "1.0.0",
        errorCode: "A1_TRACE_KEY_MISSING",
        message: "traceKey is required",
        contractId: "A1-REDIFF-IF",
        retryable: false,
        occurredAt: "2026-03-11T09:01:00.000Z",
      }),
    ).toBe(true);

    expect(
      validateHilRsContractErrorEnvelope({
        schemaVersion: "1.0.0",
        errorCode: "A1_TRACE_KEY_MISSING",
        message: "contact reviewer@example.com",
        contractId: "A1-REDIFF-IF",
        retryable: false,
        occurredAt: "2026-03-11T09:01:00.000Z",
      }),
    ).toBe(false);
  });

});
