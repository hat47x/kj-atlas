import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { globSync } from "node:fs";

import en from "./locales/en.json";
import ja from "./locales/ja.json";

function collectTranslationKeysFromSource(): Set<string> {
  const files = globSync("src/**/*.{ts,tsx}", {
    cwd: process.cwd(),
    exclude: ["src/**/*.test.ts", "src/**/*.test.tsx", "src/i18n/locales/*.json"],
  });

  const keys = new Set<string>();
  const directCallPattern = /\bt\(\s*["']([^"']+)["']/g;

  for (const relativePath of files) {
    const source = readFileSync(relativePath, "utf8");
    for (const match of source.matchAll(directCallPattern)) {
      keys.add(match[1]);
    }
  }

  return keys;
}

function extractPlaceholders(template: string): string[] {
  const placeholders = template.match(/\{([a-zA-Z0-9_]+)\}/g) ?? [];
  return placeholders.map((token) => token.slice(1, -1)).sort();
}

describe("i18n catalog integrity", () => {
  it("contains dictionary entries for all statically referenced translation keys", () => {
    const usedKeys = [...collectTranslationKeysFromSource()].sort();
    const jaKeys = new Set(Object.keys(ja));
    const enKeys = new Set(Object.keys(en));

    const missingInJa = usedKeys.filter((key) => !jaKeys.has(key));
    const missingInEn = usedKeys.filter((key) => !enKeys.has(key));

    expect({ missingInJa, missingInEn }).toEqual({ missingInJa: [], missingInEn: [] });
  });

  it("keeps ja/en placeholder sets aligned for each shared key", () => {
    const sharedKeys = Object.keys(ja).filter((key) => key in en).sort();
    const placeholderDiffs = sharedKeys
      .map((key) => ({
        key,
        jaPlaceholders: extractPlaceholders(ja[key]),
        enPlaceholders: extractPlaceholders(en[key]),
      }))
      .filter((entry) => entry.jaPlaceholders.join(",") !== entry.enPlaceholders.join(","));

    expect(placeholderDiffs).toEqual([]);
  });
});
