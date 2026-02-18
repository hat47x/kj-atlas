import { describe, expect, it } from "vitest";

import { DEFAULT_LOD_THRESHOLDS, getLODLevel, isEffectivelyCollapsed, isVirtualCollapsedByLOD } from "./lod";

describe("getLODLevel", () => {
  it("returns close/mid/far using defaults", () => {
    expect(getLODLevel(DEFAULT_LOD_THRESHOLDS.close).level).toBe("close");
    expect(getLODLevel(0.75).level).toBe("mid");
    expect(getLODLevel(0.3).level).toBe("far");
  });

  it("supports override", () => {
    expect(getLODLevel(10, { lodLevelOverride: "far" }).level).toBe("far");
  });

  it("returns compact card rules at mid", () => {
    const resolved = getLODLevel(0.75);
    expect(resolved.rules.compactCards).toBe(true);
    expect(resolved.rules.showCardEdges).toBe(false);
  });
});


describe("virtual collapse", () => {
  it("activates only in far LOD when enabled", () => {
    expect(isVirtualCollapsedByLOD(true, "far")).toBe(true);
    expect(isVirtualCollapsedByLOD(true, "mid")).toBe(false);
    expect(isVirtualCollapsedByLOD(false, "far")).toBe(false);
  });

  it("computes effective collapse from user and virtual states", () => {
    expect(isEffectivelyCollapsed(false, true, "far")).toBe(true);
    expect(isEffectivelyCollapsed(true, true, "close")).toBe(true);
    expect(isEffectivelyCollapsed(false, true, "close")).toBe(false);
  });
});
