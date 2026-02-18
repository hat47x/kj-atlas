import { describe, expect, it } from "vitest";

import { DEFAULT_LOD_THRESHOLDS, getLODLevel } from "./lod";

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
