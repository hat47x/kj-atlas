import { describe, expect, it } from "vitest";

import { shouldLoadLegacyIslandImage } from "./legacy_island_image";

describe("legacy island image loading policy", () => {
  it("blocks every URL while SafeMode is on", () => {
    expect(shouldLoadLegacyIslandImage(true, "https://images.example.test/island.png")).toBe(false);
    expect(shouldLoadLegacyIslandImage(true, "data:image/png;base64,AAAA")).toBe(false);
  });

  it("allows a non-empty legacy URL only after SafeMode is off", () => {
    expect(shouldLoadLegacyIslandImage(false, "https://images.example.test/island.png")).toBe(true);
    expect(shouldLoadLegacyIslandImage(false, "  ")).toBe(false);
    expect(shouldLoadLegacyIslandImage(false, undefined)).toBe(false);
  });
});
