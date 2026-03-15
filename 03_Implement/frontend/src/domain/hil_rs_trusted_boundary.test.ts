import { describe, expect, it } from "vitest";
import {
  evaluateMergeDecisionTrustBoundary,
  MERGE_DECISION_TRUSTED_ERROR_MESSAGE,
} from "./hil_rs_trusted_boundary";

describe("evaluateMergeDecisionTrustBoundary", () => {
  it("allows decision only when event is trusted and panel is editable", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: false, isTrustedEvent: true })).toEqual({
      allowDecision: true,
      errorMessage: null,
    });
  });

  it("blocks decision when event is not trusted", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: false, isTrustedEvent: false })).toEqual({
      allowDecision: false,
      errorMessage: MERGE_DECISION_TRUSTED_ERROR_MESSAGE,
    });
  });

  it("blocks decision in read-only mode without additional error", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: true, isTrustedEvent: true })).toEqual({
      allowDecision: false,
      errorMessage: null,
    });
  });
});
