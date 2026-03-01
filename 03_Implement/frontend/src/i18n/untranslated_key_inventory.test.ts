import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { join, relative } from "node:path";

import ja from "./locales/ja.json";
import en from "./locales/en.json";

type MissingByScreen = Record<string, string[]>;

function collectSourceFiles(rootDir: string): string[] {
  const files: string[] = [];

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

      const relativePath = relative(rootDir, absolutePath).split("\\").join("/");
      if (/\.(ts|tsx)$/.test(relativePath) && !/\.test\.(ts|tsx)$/.test(relativePath)) {
        files.push(absolutePath);
      }
    }
  };

  walk(rootDir);
  return files;
}

function collectMissingKeysByScreen(): { missingInJa: MissingByScreen; missingInEn: MissingByScreen } {
  const jaKeys = new Set(Object.keys(ja));
  const enKeys = new Set(Object.keys(en));
  const rootDir = join(process.cwd(), "src");
  const files = collectSourceFiles(rootDir);

  const missingInJa: MissingByScreen = {};
  const missingInEn: MissingByScreen = {};
  const keyPattern = /\bt\(\s*["']([^"']+)["']/g;

  for (const absolutePath of files) {
    const source = readFileSync(absolutePath, "utf8");
    const relativePath = relative(rootDir, absolutePath).split("\\").join("/");
    for (const match of source.matchAll(keyPattern)) {
      const key = match[1];
      if (!jaKeys.has(key)) {
        missingInJa[relativePath] ??= [];
        if (!missingInJa[relativePath].includes(key)) {
          missingInJa[relativePath].push(key);
        }
      }
      if (!enKeys.has(key)) {
        missingInEn[relativePath] ??= [];
        if (!missingInEn[relativePath].includes(key)) {
          missingInEn[relativePath].push(key);
        }
      }
    }
  }

  return { missingInJa, missingInEn };
}

describe("i18n untranslated key inventory", () => {
  it("keeps missing key inventory empty by screen", () => {
    const inventory = collectMissingKeysByScreen();
    expect(inventory).toEqual({ missingInJa: {}, missingInEn: {} });
  });
});
