import { describe, expect, it } from "vitest";

import { normalizeHilDecisionReason } from "./hil_rs_decision_reason";

describe("normalizeHilDecisionReason", () => {
  it("returns trimmed text when reason is provided", () => {
    expect(normalizeHilDecisionReason("  keep domain distinction ")).toBe("keep domain distinction");
  });

  it("returns null when reason is empty or not a string", () => {
    expect(normalizeHilDecisionReason("   ")).toBeNull();
    expect(normalizeHilDecisionReason(undefined)).toBeNull();
    expect(normalizeHilDecisionReason(null)).toBeNull();
  });
});
