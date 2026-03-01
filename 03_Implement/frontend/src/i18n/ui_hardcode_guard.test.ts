import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

type GuardCase = {
  file: string;
  forbiddenLiterals: string[];
};

const guardCases: GuardCase[] = [
  {
    file: "ui/DiffPanel.tsx",
    forbiddenLiterals: [
      "Load comparison document (JSON)",
      "Reading order",
      "added:",
      "removed:",
      "Show full order arrays",
    ],
  },
  {
    file: "ui/SuggestionPanel.tsx",
    forbiddenLiterals: [
      "Draft suggestion",
      "Suggest layout",
      "Apply suggestion",
      "Preview suggestion",
    ],
  },
  {
    file: "ui/ReviewDiffPanel.tsx",
    forbiddenLiterals: [
      "Review Diff (Selective Merge)",
      "Apply selected merge",
      "Revert last merge",
      "Auto-include prerequisites",
      "Select all",
      "Select none",
    ],
  },
];

describe("i18n UI hardcoded text guard", () => {
  for (const testCase of guardCases) {
    it(`does not keep raw UI literals in ${testCase.file}`, () => {
      const source = readFileSync(resolve(import.meta.dirname, "..", testCase.file), "utf-8");
      for (const literal of testCase.forbiddenLiterals) {
        expect(source).not.toContain(`>${literal}<`);
      }
    });
  }
});
