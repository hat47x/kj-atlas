import { describe, expect, it } from "vitest";
import { evaluateIslandVisibilityA3GoNoGoStreamD } from "./island_visibility_stream_d";
import type { HandoffLogEntry } from "./handoff_types";

const validLogs: HandoffLogEntry[] = [
  {
    contractVersion: "IslandVisibilityContractV1",
    mockCaseId: "M1",
    validationResult: "pass",
    ownerOfFix: "A3",
    evidence: "collapse hides descendants and cards",
  },
  {
    contractVersion: "IslandVisibilityContractV1",
    mockCaseId: "M2",
    validationResult: "pass",
    ownerOfFix: "A3",
    evidence: "expand restores descendants and cards",
  },
  {
    contractVersion: "IslandVisibilityContractV1",
    mockCaseId: "M3",
    validationResult: "pass",
    ownerOfFix: "A3",
    evidence: "double collapse is idempotent",
  },
  {
    contractVersion: "IslandVisibilityContractV1",
    mockCaseId: "M4",
    validationResult: "fail",
    ownerOfFix: "A2",
    evidence: "invalid island collapse rejected",
  },
];

describe("evaluateIslandVisibilityA3GoNoGoStreamD", () => {
  it("returns go for A2 mock validation baseline", () => {
    expect(evaluateIslandVisibilityA3GoNoGoStreamD(validLogs)).toEqual({
      go: true,
      reasons: [],
    });
  });

  it("returns nogo when owner routing is incorrect", () => {
    const invalid = validLogs.map((entry) =>
      entry.mockCaseId === "M4" ? { ...entry, ownerOfFix: "A3" as const } : entry,
    );
    const report = evaluateIslandVisibilityA3GoNoGoStreamD(invalid);
    expect(report.go).toBe(false);
    expect(report.reasons).toContain("M4 ownerOfFix mismatch");
  });

  it("fails fast when contractVersion is mismatched", () => {
    expect(() =>
      evaluateIslandVisibilityA3GoNoGoStreamD([
        { ...validLogs[0], contractVersion: "IslandVisibilityContractV0" },
      ]),
    ).toThrowError("contractVersion mismatch for IslandVisibilityContractV1");
  });
});
