import { describe, expect, it } from "vitest";
import { evaluateMergeDecisionTrustBoundary } from "./hil_rs_trusted_boundary";

describe("evaluateMergeDecisionTrustBoundary", () => {
  it("allows decision only when event is trusted and panel is editable", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: false, isTrustedEvent: true })).toEqual({
      allowDecision: true,
      rejectionReason: null,
    });
  });

  it("blocks decision when event is not trusted", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: false, isTrustedEvent: false })).toEqual({
      allowDecision: false,
      rejectionReason: "untrusted_event",
    });
  });

  it("blocks decision in read-only mode without additional error", () => {
    expect(evaluateMergeDecisionTrustBoundary({ isReadOnly: true, isTrustedEvent: true })).toEqual({
      allowDecision: false,
      rejectionReason: "read_only",
    });
  });
});
