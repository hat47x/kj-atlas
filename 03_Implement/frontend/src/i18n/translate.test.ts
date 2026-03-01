import { describe, expect, it } from "vitest";
import {
  DEFAULT_LOCALE,
  getActiveLocale,
  isLocale,
  resolveTemplate,
  resolveTemplateFromCatalogs,
  setActiveLocale,
  subscribeActiveLocaleChange,
  t,
  validateLocaleMessages,
  type Locale,
} from "./translate";
import type { MessageCatalog } from "./messages";
import en from "./locales/en.json";
import ja from "./locales/ja.json";

describe("translate", () => {
  it("resolves known keys in default locale", () => {
    expect(t("share.panel.trigger")).toBe("共有と再現");
  });

  it("interpolates placeholder values", () => {
    expect(
      t("import.panel.summary", {
        fileName: "sample.zip",
        cardCount: 12,
        islandCount: 3,
        perspectiveMode: "default",
      }),
    ).toBe("sample.zip を取り込みました: cards 12, islands 3, perspective default");
  });

  it("falls back to default locale when requested locale misses a key", () => {
    const catalogs = {
      ja: { "safe_mode.indicator.on.label": "セーフモード: ON" },
      en: {} as MessageCatalog,
    };
    expect(resolveTemplateFromCatalogs("safe_mode.indicator.on.label", "en", catalogs)).toBe("セーフモード: ON");
  });

  it("falls back to key string when key is unknown in all locales", () => {
    expect(t("unknown.key" as string, undefined, "en")).toBe("unknown.key");
  });

  it("supports locale override for known locale", () => {
    expect(t("share.panel.export.bundle_cancel", undefined, "en")).toBe("Cancel");
  });

  it("supports active locale switch without per-call locale argument", () => {
    setActiveLocale("en");
    expect(getActiveLocale()).toBe("en");
    expect(t("share.panel.trigger")).toBe("Share & Reproduce");

    setActiveLocale("ja");
    expect(getActiveLocale()).toBe("ja");
    expect(t("share.panel.trigger")).toBe("共有と再現");
  });

  it("normalizes unknown locale to default", () => {
    expect(isLocale("ja")).toBe(true);
    expect(isLocale("en")).toBe(true);
    expect(isLocale("fr")).toBe(false);

    const locale: Locale = DEFAULT_LOCALE;
    expect(locale).toBe("ja");

    setActiveLocale("fr");
    expect(getActiveLocale()).toBe("ja");
  });

  it("validates locale message payload contract", () => {
    expect(validateLocaleMessages({ hello: "world" })).toEqual({ ok: true, errors: [] });
    expect(validateLocaleMessages(null)).toEqual({ ok: false, errors: ["Locale messages must be a JSON object."] });
    expect(validateLocaleMessages({ hello: 1 })).toEqual({
      ok: false,
      errors: ["Locale message value for key \"hello\" must be a string."],
    });
  });

  it("keeps ja/en dictionaries key-equivalent", () => {
    const jaKeys = Object.keys(ja).sort();
    const enKeys = Object.keys(en).sort();
    expect(enKeys).toEqual(jaKeys);
  });

  it("resolves explicit locale via resolveTemplate", () => {
    expect(resolveTemplate("safe_mode.indicator.on.label", "en")).toBe("SafeMode: ON");
  });

  it("notifies listeners when active locale changes", () => {
    const calls: string[] = [];
    const unsubscribe = subscribeActiveLocaleChange((locale) => {
      calls.push(locale);
    });

    setActiveLocale("en");
    setActiveLocale("ja");
    unsubscribe();
    setActiveLocale("en");

    expect(calls).toEqual(["en", "ja"]);
  });
});
