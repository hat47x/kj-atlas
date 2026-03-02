import { describe, expect, it } from "vitest";

import type { MessageCatalog } from "./messages";
import { resolveTemplateFromCatalogs } from "./translate";

type TestCase = {
  title: string;
  key: string;
  requestedLocale: "ja" | "en";
  catalogs: Record<"ja" | "en", MessageCatalog>;
  expected: string;
};

const testCases: TestCase[] = [
  {
    title: "returns requested-locale template when requested locale has a valid template",
    key: "k",
    requestedLocale: "en",
    catalogs: {
      ja: { k: "日本語" },
      en: { k: "English" },
    },
    expected: "English",
  },
  {
    title: "falls back to ja when requested locale key is missing",
    key: "k",
    requestedLocale: "en",
    catalogs: {
      ja: { k: "日本語" },
      en: {},
    },
    expected: "日本語",
  },
  {
    title: "falls back to ja when requested locale template is malformed",
    key: "k",
    requestedLocale: "en",
    catalogs: {
      ja: { k: "値: {value}" },
      en: { k: "Value: {value" },
    },
    expected: "値: {value}",
  },
  {
    title: "returns key when neither requested locale nor ja has a usable template",
    key: "k",
    requestedLocale: "en",
    catalogs: {
      ja: { k: "値: {value" },
      en: { k: "Value: {value" },
    },
    expected: "k",
  },
  {
    title: "returns key when key is absent in all locales",
    key: "unknown.key",
    requestedLocale: "en",
    catalogs: {
      ja: {},
      en: {},
    },
    expected: "unknown.key",
  },
];

describe("i18n fallback contract", () => {
  it("enforces requested -> ja -> key fallback order", () => {
    for (const testCase of testCases) {
      expect(
        resolveTemplateFromCatalogs(testCase.key, testCase.requestedLocale, testCase.catalogs),
        testCase.title,
      ).toBe(testCase.expected);
    }
  });
});
