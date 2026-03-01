import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

import en from "./locales/en.json";
import ja from "./locales/ja.json";

function collectSourceFiles(rootDir: string): string[] {
  const collected: string[] = [];

  const walk = (currentDir: string): void => {
    const entries = readdirSync(currentDir, { withFileTypes: true });
    for (const entry of entries) {
      const absolutePath = join(currentDir, entry.name);
      if (entry.isDirectory()) {
        walk(absolutePath);
        continue;
      }

      if (!entry.isFile()) {
        continue;
      }

      const relativePath = relative(rootDir, absolutePath).split("\\").join("/" );
      const isSourceFile = /\.(ts|tsx)$/.test(relativePath);
      const isTestFile = /\.test\.(ts|tsx)$/.test(relativePath);
      const isLocaleJson = relativePath.startsWith("i18n/locales/") && relativePath.endsWith(".json");

      if (isSourceFile && !isTestFile && !isLocaleJson) {
        collected.push(absolutePath);
      }
    }
  };

  walk(rootDir);
  return collected;
}

function collectTranslationKeysFromSource(): Set<string> {
  const files = collectSourceFiles(join(process.cwd(), "src"));

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
  const jaCatalog: Record<string, string> = ja;
  const enCatalog: Record<string, string> = en;

  it("contains dictionary entries for all statically referenced translation keys", () => {
    const usedKeys = [...collectTranslationKeysFromSource()].sort();
    const jaKeys = new Set(Object.keys(jaCatalog));
    const enKeys = new Set(Object.keys(enCatalog));

    const missingInJa = usedKeys.filter((key) => !jaKeys.has(key));
    const missingInEn = usedKeys.filter((key) => !enKeys.has(key));

    expect({ missingInJa, missingInEn }).toEqual({ missingInJa: [], missingInEn: [] });
  });

  it("keeps ja/en placeholder sets aligned for each shared key", () => {
    const sharedKeys = Object.keys(jaCatalog)
      .filter((key) => key in enCatalog)
      .sort();
    const placeholderDiffs = sharedKeys
      .map((key) => ({
        key,
        jaPlaceholders: extractPlaceholders(jaCatalog[key]),
        enPlaceholders: extractPlaceholders(enCatalog[key]),
      }))
      .filter((entry) => entry.jaPlaceholders.join(",") !== entry.enPlaceholders.join(","));

    expect(placeholderDiffs).toEqual([]);
  });
});
