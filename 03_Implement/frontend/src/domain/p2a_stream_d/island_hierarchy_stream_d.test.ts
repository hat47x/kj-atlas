import { describe, expect, it } from "vitest";
import {
  evaluateIslandHierarchyA3GoNoGoStreamD,
  validateIslandHierarchyRoundTripStreamD,
} from "./island_hierarchy_stream_d";
import type { HandoffLogEntry } from "./handoff_types";

const validLogs: HandoffLogEntry[] = [
  {
    contractVersion: "IslandHierarchyContractV1",
    mockCaseId: "M1",
    validationResult: "pass",
    ownerOfFix: "A3",
    evidence: "root hierarchy accepted",
  },
  {
    contractVersion: "IslandHierarchyContractV1",
    mockCaseId: "M2",
    validationResult: "pass",
    ownerOfFix: "A3",
    evidence: "three-level hierarchy accepted",
  },
  {
    contractVersion: "IslandHierarchyContractV1",
    mockCaseId: "M3",
    validationResult: "fail",
    ownerOfFix: "A2",
    evidence: "missing parent rejected",
  },
  {
    contractVersion: "IslandHierarchyContractV1",
    mockCaseId: "M4",
    validationResult: "fail",
    ownerOfFix: "A2",
    evidence: "cycle rejected",
  },
];

describe("evaluateIslandHierarchyA3GoNoGoStreamD", () => {
  it("returns go for fixed A2 results", () => {
    expect(evaluateIslandHierarchyA3GoNoGoStreamD(validLogs)).toEqual({
      go: true,
      reasons: [],
    });
  });

  it("returns nogo when an expected case is missing", () => {
    const report = evaluateIslandHierarchyA3GoNoGoStreamD(validLogs.slice(0, 3));
    expect(report.go).toBe(false);
    expect(report.reasons).toContain("missing mockCaseId: M4");
  });

  it("fails fast on duplicate mockCaseId", () => {
    expect(() =>
      evaluateIslandHierarchyA3GoNoGoStreamD([
        ...validLogs,
        { ...validLogs[0], evidence: "duplicate" },
      ]),
    ).toThrowError("duplicate mockCaseId: M1");
  });

  it("keeps go decision after JSON roundtrip", () => {
    expect(validateIslandHierarchyRoundTripStreamD(validLogs).go).toBe(true);
  });
});
