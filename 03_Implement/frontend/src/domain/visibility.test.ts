import { describe, expect, it } from "vitest";

import { isTemporaryRevealEligible } from "./visibility";

describe("isTemporaryRevealEligible", () => {
  it("returns true only when focus and depth constraints are both satisfied", () => {
    expect(isTemporaryRevealEligible({ isInFocusScope: true, isWithinDepth: true })).toBe(true);
    expect(isTemporaryRevealEligible({ isInFocusScope: true, isWithinDepth: false })).toBe(false);
    expect(isTemporaryRevealEligible({ isInFocusScope: false, isWithinDepth: true })).toBe(false);
    expect(isTemporaryRevealEligible({ isInFocusScope: false, isWithinDepth: false })).toBe(false);
  });
});
