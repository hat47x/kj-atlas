import { describe, expect, it } from "vitest";

import { getPresetIdForViewMode, getViewModeForPresetId, getViewModeLabel, isViewMode } from "./view_mode";

describe("view_mode", () => {
  it("maps each mode to the default preset id", () => {
    expect(getPresetIdForViewMode("explore")).toBe("default-explore");
    expect(getPresetIdForViewMode("review")).toBe("default-review");
    expect(getPresetIdForViewMode("summary")).toBe("default-summary");
  });

  it("maps default preset ids back to modes", () => {
    expect(getViewModeForPresetId("default-explore")).toBe("explore");
    expect(getViewModeForPresetId("default-review")).toBe("review");
    expect(getViewModeForPresetId("default-summary")).toBe("summary");
  });

  it("returns null for non-default preset ids", () => {
    expect(getViewModeForPresetId("preset-custom")).toBeNull();
    expect(getViewModeForPresetId(null)).toBeNull();
    expect(getViewModeForPresetId(undefined)).toBeNull();
  });

  it("validates known modes only", () => {
    expect(isViewMode("explore")).toBe(true);
    expect(isViewMode("review")).toBe(true);
    expect(isViewMode("summary")).toBe(true);
    expect(isViewMode("default")).toBe(false);
    expect(isViewMode(1)).toBe(false);
  });

  it("provides user-facing labels", () => {
    expect(getViewModeLabel("explore")).toBe("Explore");
    expect(getViewModeLabel("review")).toBe("Review");
    expect(getViewModeLabel("summary")).toBe("Summary");
  });
});
