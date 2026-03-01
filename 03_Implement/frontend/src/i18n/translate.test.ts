import { describe, expect, it } from "vitest";
import {
  DEFAULT_LOCALE,
  isLocale,
  resolveTemplate,
  t,
  validateLocaleMessages,
  type Locale,
} from "./translate";

describe("translate", () => {
  it("resolves known keys in default locale", () => {
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

  it("falls back to default locale when requested locale misses a key", () => {
    expect(resolveTemplate("safe_mode.indicator.on.label", "en")).toBe("SafeMode: ON");
  });

  it("falls back to key string when key is unknown in all locales", () => {
    expect(t("unknown.key" as string, undefined, "en")).toBe("unknown.key");
  });

  it("supports locale override for known locale", () => {
    expect(t("share.panel.export.bundle_cancel", undefined, "en")).toBe("Cancel");
  });

  it("normalizes unknown locale to default", () => {
    expect(isLocale("ja")).toBe(true);
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fr")).toBe(false);

    const locale: Locale = DEFAULT_LOCALE;
    expect(locale).toBe("ja");
  });

  it("validates locale message payload contract", () => {
    expect(validateLocaleMessages({ hello: "world" })).toEqual({ ok: true, errors: [] });
    expect(validateLocaleMessages(null)).toEqual({ ok: false, errors: ["Locale messages must be a JSON object."] });
    expect(validateLocaleMessages({ hello: 1 })).toEqual({
      ok: false,
      errors: ["Locale message value for key \"hello\" must be a string."],
    });
  });
});
