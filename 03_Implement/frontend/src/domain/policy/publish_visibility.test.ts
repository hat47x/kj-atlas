import { describe, expect, it } from "vitest";
import {
  DEFAULT_PACK_VISIBILITY,
  DEFAULT_VIEW_VISIBILITY,
  PUBLISH_VISIBILITY_VALUES,
  isPublishVisibility,
  normalizePackVisibility,
  normalizeViewVisibility,
} from "./publish_visibility";

describe("publish_visibility policy", () => {
  it("accepts only configured visibility enum values", () => {
    for (const value of PUBLISH_VISIBILITY_VALUES) {
      expect(isPublishVisibility(value)).toBe(true);
    }
    expect(isPublishVisibility("FriendsOnly")).toBe(false);
  });

  it("applies restricted fallback for view visibility", () => {
    expect(normalizeViewVisibility(undefined)).toBe(DEFAULT_VIEW_VISIBILITY);
    expect(normalizeViewVisibility("Public")).toBe("Public");
    expect(normalizeViewVisibility("private")).toBe(DEFAULT_VIEW_VISIBILITY);
  });

  it("applies public fallback for pack visibility", () => {
    expect(normalizePackVisibility(undefined)).toBe(DEFAULT_PACK_VISIBILITY);
    expect(normalizePackVisibility("Org")).toBe("Org");
    expect(normalizePackVisibility(1)).toBe(DEFAULT_PACK_VISIBILITY);
  });
});
