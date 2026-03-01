import { describe, expect, it } from "vitest";

import { maxDepthForHierarchyLevel, resolveHierarchyLevel } from "./hierarchy_level";

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
