import { describe, expect, it } from "vitest";

import { buildDiagnosticsBundle, type DiagBundleInput } from "./diagnostics_bundle";


const BASE_INPUT: DiagBundleInput = {
  generatedAt: "2026-09-06T00:00:00.000Z",
  classificationCode: "SAVE-FAILURE",
  safeMode: false,
  providerType: "none",
};

const CASES: Array<[string, string]> = [
  ["rev-2026.09.06_1", "rev-2026.09.06_1"],
  ["a".repeat(64), "a".repeat(64)],
  ["", "unknown"],
  [" release-1 ", "unknown"],
  ["release+1", "unknown"],
  ["feature/revision", "unknown"],
  ["line\nbreak", "unknown"],
  ["a".repeat(65), "unknown"],
];

describe("KJ_ATLAS_APP_REVISION canonical observability contract", () => {
  it.each(CASES)("normalizes %j to %s", (rawRevision, expectedRevision) => {
    const bundle = buildDiagnosticsBundle({ ...BASE_INPUT, appRevision: rawRevision });
    expect(bundle.app.revision).toBe(expectedRevision);
  });
});
