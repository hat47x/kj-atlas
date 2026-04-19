import { describe, expect, it } from "vitest";
import { P2A_A1_CONTRACT_LOCK } from "./contract";
import { P2A_A2_MOCK_FIXTURES } from "./mock_fixtures";
import {
  buildP2AImplementationReadiness,
  evaluateP2AA3Proceed,
  toP2AValidationLedger,
  validateP2AA1ContractLock,
  validateP2AA2FixtureSignature,
} from "./validation";

describe("FB-P2A contract validation flow", () => {
  it("A1 contract lock passes with fixed contract and invariant set", () => {
    const result = validateP2AA1ContractLock(P2A_A1_CONTRACT_LOCK);
    expect(result.ok).toBe(true);
    expect(result.errors).toEqual([]);
  });

  it("A2 fixture signature passes for M1..M4 and required handoff fields", () => {
    const result = validateP2AA2FixtureSignature(P2A_A2_MOCK_FIXTURES);
    expect(result.ok).toBe(true);
    expect(result.errors).toEqual([]);
  });

  it("A3 proceed gate returns go for M1/M2/M3 pass + M4 fail", () => {
    const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES);
    expect(evaluateP2AA3Proceed(logs)).toEqual({ go: true, reason: "go" });
  });

  it("A3 proceed gate returns no-go when M4 owner is not A2", () => {
    const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES);
    const altered = logs.map((log) => (log.mockCaseId === "M4" ? { ...log, ownerOfFix: "A3" as const } : log));
    expect(evaluateP2AA3Proceed(altered)).toEqual({ go: false, reason: "M4 ownerOfFix must be A2" });
  });

  it("builds A3 implementation readiness output from fixed handoff logs", () => {
    const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES);
    expect(buildP2AImplementationReadiness(logs)).toEqual({
      implementationReadiness: "go",
      acceptedMockCases: ["M1", "M2", "M3"],
      blockedMockCases: ["M4"],
      rollbackTrigger: [],
      notes: ["GoNoGo passed (M1/M2/M3=pass and M4=fail)"],
    });
  });

  it("returns no-go readiness with rollback trigger when contract constraints fail", () => {
    const logs = toP2AValidationLedger(P2A_A2_MOCK_FIXTURES).map((log) =>
      log.mockCaseId === "M4" ? { ...log, validationResult: "pass" as const } : log
    );
    expect(buildP2AImplementationReadiness(logs)).toEqual({
      implementationReadiness: "no-go",
      acceptedMockCases: [],
      blockedMockCases: ["M1", "M2", "M3", "M4"],
      rollbackTrigger: ["M4 must be fail"],
      notes: ["Rollback to A2 fixed ledger and resolve ownerOfFix / contract mismatch"],
    });
  });
});
