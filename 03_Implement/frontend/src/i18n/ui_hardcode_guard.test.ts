import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

type GuardCase = {
  file: string;
  forbiddenLiterals: string[];
};

const guardCases: GuardCase[] = [
  {
    file: "ui/ImportPanel.tsx",
    forbiddenLiterals: [
      "Import Review Pack (.zip)",
      "Drop .zip file here",
      "Choose .zip",
      "Ignored warnings:",
    ],
  },
  {
    file: "ui/SharePanel.tsx",
    forbiddenLiterals: [
      "Share / Export",
      "Export",
      "Enable SafeMode",
      "Export SVG (Viewport)",
      "Export bundle (.zip)",
      "Replace current document",
    ],
  },
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
  {
    file: "domain/policy/read_only.ts",
    forbiddenLiterals: [
      "Read-only mode: editing actions are disabled.",
      "Read-only mode:",
    ],
  },
  {
    file: "App.tsx",
    forbiddenLiterals: [
      "Import doc JSON (legacy, confirm in Share)",
      "Export doc JSON (legacy)",
      "Legacy entry point. Use “Share &amp; Reproduce” for ordered Diff/Verify flow.",
    ],
  },
  {
    file: "ui/ViewControlsPanel.tsx",
    forbiddenLiterals: [
      "Export (legacy)",
      "Deprecated entry point. Use “Share &amp; Reproduce” for the canonical flow.",
      "Export SVG (Viewport)",
      "Export Abstract Map Report (HTML + PNG)",
      "Load view metadata (JSON)",
      "Review view",
    ],
  },
  {
    file: "ui/SidePanel.tsx",
    forbiddenLiterals: ["Export Trace Analytics"],
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
