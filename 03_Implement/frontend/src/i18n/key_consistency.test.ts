import { describe, expect, it } from "vitest";

import en from "./locales/en.json";
import ja from "./locales/ja.json";

function diffKeys(left: string[], right: string[]): string[] {
  const rightSet = new Set(right);
  return left.filter((key) => !rightSet.has(key));
}

describe("i18n dictionary key consistency", () => {
  it("keeps ja/en dictionaries in full key parity", () => {
    const jaKeys = Object.keys(ja).sort();
    const enKeys = Object.keys(en).sort();

    const jaOnly = diffKeys(jaKeys, enKeys);
    const enOnly = diffKeys(enKeys, jaKeys);

    expect({ jaOnly, enOnly }).toEqual({ jaOnly: [], enOnly: [] });
  });
});
