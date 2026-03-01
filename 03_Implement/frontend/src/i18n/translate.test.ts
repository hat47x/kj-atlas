import { describe, expect, it } from "vitest";
import { t } from "./translate";

describe("translate", () => {
  it("resolves known keys", () => {
    expect(t("share.panel.trigger")).toBe("Share & Reproduce");
  });

  it("interpolates placeholder values", () => {
    expect(
      t("import.panel.summary", {
        fileName: "sample.zip",
        cardCount: 12,
        islandCount: 3,
        perspectiveMode: "default",
      }),
    ).toBe("Imported sample.zip: cards 12, islands 3, perspective default");
  });

  it("falls back to the key string for unknown keys", () => {
    expect(t("unknown.key" as string)).toBe("unknown.key");
  });
});
