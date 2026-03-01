import { describe, expect, it } from "vitest";
import { readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const localesDir = join(import.meta.dirname, "locales");

type MessageCatalog = Record<string, string>;

function loadCatalog(localeFileName: string): MessageCatalog {
  const filePath = join(localesDir, localeFileName);
  return JSON.parse(readFileSync(filePath, "utf-8")) as MessageCatalog;
}

function listLocaleFiles(): string[] {
  return readdirSync(localesDir)
    .filter((name) => name.endsWith(".json"))
    .sort();
}

function diffKeys(left: string[], right: string[]): string[] {
  const rightSet = new Set(right);
  return left.filter((key) => !rightSet.has(key));
}

describe("i18n catalog integrity", () => {
  it("keeps key parity across all locale catalogs", () => {
    const localeFiles = listLocaleFiles();
    expect(localeFiles.length).toBeGreaterThan(0);

    const catalogs = localeFiles.map((fileName) => ({
      fileName,
      locale: fileName.replace(/\.json$/, ""),
      catalog: loadCatalog(fileName),
    }));

    const baseline = catalogs[0];
    const baselineKeys = Object.keys(baseline.catalog).sort();

    for (const current of catalogs.slice(1)) {
      const currentKeys = Object.keys(current.catalog).sort();
      const missingInCurrent = diffKeys(baselineKeys, currentKeys);
      const extraInCurrent = diffKeys(currentKeys, baselineKeys);

      expect({
        baseline: baseline.locale,
        current: current.locale,
        missingInCurrent,
        extraInCurrent,
      }).toEqual({
        baseline: baseline.locale,
        current: current.locale,
        missingInCurrent: [],
        extraInCurrent: [],
      });
    }
  });
});
