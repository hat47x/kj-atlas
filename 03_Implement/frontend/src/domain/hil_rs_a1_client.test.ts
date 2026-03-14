import { describe, expect, it } from "vitest";

import {
  proposeReDiff,
  recordReviewAttribution,
  submitCritique,
  toContractError,
} from "./hil_rs_a1_client";

describe("hil_rs_a1_client", () => {
  it("accepts A1-CRITIQUE-IF payload", () => {
    const result = submitCritique({
      schemaVersion: "1.0.0",
      critiqueId: "card:c1:1",
      targetRef: "card:c1",
      critiqueType: "too_close",
      createdAt: "2026-03-14T00:00:00.000Z",
      iteration: 1,
    });

    expect(result).toEqual({
      contractId: "A1-CRITIQUE-IF",
      schemaVersion: "1.0.0",
      critiqueId: "card:c1:1",
      accepted: true,
    });
  });

  it("accepts A1-REDIFF-IF payload with traceKey", () => {
    const result = proposeReDiff({
      schemaVersion: "1.0.0",
      proposalId: "proposal-1",
      basedOnIteration: 1,
      traceKey: "trace:card:c1:1",
      diffOps: [
        {
          opId: "op-1",
          opType: "move",
          targetRef: "card:c1",
          before: { x: 0, y: 0 },
          after: { x: 2, y: 3 },
        },
      ],
    });

    expect(result).toEqual({
      contractId: "A1-REDIFF-IF",
      schemaVersion: "1.0.0",
      proposalId: "proposal-1",
      traceKey: "trace:card:c1:1",
      accepted: true,
    });
  });

  it("records valid A1-ATTR-IF payload", () => {
    const result = recordReviewAttribution({
      schemaVersion: "1.0.0",
      reviewState: "human_reviewed",
      reviewedAt: "2026-03-14T00:00:00.000Z",
      reviewerRef: "opaque-reviewer-01",
      auditRecordedAt: "2026-03-14T00:00:01.000Z",
      overridePolicy: "human_dual_control_only",
    });

    expect(result).toEqual({
      contractId: "A1-ATTR-IF",
      schemaVersion: "1.0.0",
      reviewState: "human_reviewed",
      recorded: true,
    });
  });

  it("builds A1-ERROR-IF envelope", () => {
    const result = toContractError({
      message: "required field missing",
      contractId: "A1-CRITIQUE-IF",
      errorCode: "A1_REQUIRED_FIELD_MISSING",
      retryable: false,
      occurredAt: "2026-03-14T00:00:01.000Z",
    });

    expect(result).toEqual({
      schemaVersion: "1.0.0",
      errorCode: "A1_REQUIRED_FIELD_MISSING",
      message: "required field missing",
      contractId: "A1-CRITIQUE-IF",
      retryable: false,
      occurredAt: "2026-03-14T00:00:01.000Z",
    });
  });

  it("throws on contract violations", () => {
    expect(() =>
      submitCritique({
        schemaVersion: "1.0.0",
        critiqueId: "card:c1:1",
        targetRef: "card:c1",
        critiqueType: "too_close",
        createdAt: "2026-03-14T00:00:00.000Z",
        iteration: 0,
      }),
    ).toThrow("A1-CRITIQUE-IF validation failed");

    expect(() =>
      proposeReDiff({
        schemaVersion: "1.0.0",
        proposalId: "proposal-1",
        basedOnIteration: 1,
        traceKey: "",
        diffOps: [],
      }),
    ).toThrow("A1-REDIFF-IF validation failed");

    expect(() =>
      toContractError({
        message: "contact reviewer@example.com",
        contractId: "A1-CRITIQUE-IF",
        errorCode: "A1_REQUIRED_FIELD_MISSING",
      }),
    ).toThrow("A1-ERROR-IF validation failed");
  });
});
