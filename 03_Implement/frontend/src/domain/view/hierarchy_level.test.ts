import { describe, expect, it } from "vitest";

import { clampMaxDepthToAvailable, maxDepthForHierarchyLevel, resolveHierarchyLevel } from "./hierarchy_level";

describe("hierarchy_level", () => {
  it("resolves hierarchy level from maxDepth", () => {
    expect(resolveHierarchyLevel("all")).toBe("detail");
    expect(resolveHierarchyLevel(0)).toBe("overview");
    expect(resolveHierarchyLevel(-1)).toBe("overview");
    expect(resolveHierarchyLevel(1)).toBe("mid");
    expect(resolveHierarchyLevel(4)).toBe("mid");
  });

  it("maps hierarchy level to maxDepth", () => {
    expect(maxDepthForHierarchyLevel("overview")).toBe(0);
    expect(maxDepthForHierarchyLevel("mid")).toBe(1);
    expect(maxDepthForHierarchyLevel("detail")).toBe("all");
  });
});

describe("clampMaxDepthToAvailable (QA-MONKEY-13 regression guard)", () => {
  it("does not clamp an explicit 'mid' choice (maxDepth=1) when the document has no nested islands (maxAvailableDepth=0)", () => {
    // This is the exact QA-MONKEY-13 scenario: without the maxAvailableDepth
    // > 0 guard, this used to clamp to 0, which the sync effect in App.tsx
    // then re-resolved to "overview" -- silently overriding the user's "mid"
    // selection whenever the open document had zero nested islands.
    expect(clampMaxDepthToAvailable(1, 0)).toBe(1);
  });

  it("clamps down when maxDepth exceeds real available depth", () => {
    expect(clampMaxDepthToAvailable(3, 1)).toBe(1);
  });

  it("does not clamp when maxDepth is already within the available depth", () => {
    expect(clampMaxDepthToAvailable(1, 2)).toBe(1);
    expect(clampMaxDepthToAvailable(2, 2)).toBe(2);
  });

  it("never clamps 'all' (detail level), regardless of available depth", () => {
    expect(clampMaxDepthToAvailable("all", 0)).toBe("all");
    expect(clampMaxDepthToAvailable("all", 5)).toBe("all");
  });
});
