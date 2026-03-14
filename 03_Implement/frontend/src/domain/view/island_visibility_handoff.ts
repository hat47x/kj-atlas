import type { ContractValidationResult, IslandVisibilityContractV1 } from "../contracts/island_contracts";

export type IslandVisibilityMockCaseId = "M1" | "M2" | "M3" | "M4";
export type IslandVisibilityOwnerOfFix = "A1" | "A2" | "A3";

export type IslandVisibilityValidationLog = {
  contractVersion: "IslandVisibilityContractV1";
  mockCaseId: IslandVisibilityMockCaseId;
  validationResult: "pass" | "fail";
  ownerOfFix: IslandVisibilityOwnerOfFix;
  evidence: string;
};

export function toIslandVisibilityValidationLog(
  mockCaseId: IslandVisibilityMockCaseId,
  validation: ContractValidationResult<IslandVisibilityContractV1>,
  ownerOnFailure: IslandVisibilityOwnerOfFix,
  evidence: string,
): IslandVisibilityValidationLog {
  if (validation.ok) {
    return {
      contractVersion: "IslandVisibilityContractV1",
      mockCaseId,
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence,
    };
  }

  return {
    contractVersion: "IslandVisibilityContractV1",
    mockCaseId,
    validationResult: "fail",
    ownerOfFix: ownerOnFailure,
    evidence: `${evidence}; error=${validation.error}`,
  };
}

export function evaluateIslandVisibilityA3GoNoGo(logs: IslandVisibilityValidationLog[]): {
  go: boolean;
  reason: string;
} {
  const byCase = new Map<IslandVisibilityMockCaseId, IslandVisibilityValidationLog>();
  for (const log of logs) {
    byCase.set(log.mockCaseId, log);
  }

  const requiredCases: IslandVisibilityMockCaseId[] = ["M1", "M2", "M3", "M4"];
  for (const requiredCase of requiredCases) {
    if (!byCase.has(requiredCase)) {
      return { go: false, reason: `missing mock case: ${requiredCase}` };
    }
  }

  const m1 = byCase.get("M1");
  const m2 = byCase.get("M2");
  const m3 = byCase.get("M3");
  const m4 = byCase.get("M4");

  if (!m1 || !m2 || !m3 || !m4) {
    return { go: false, reason: "missing mock case details" };
  }

  if (m1.validationResult !== "pass" || m2.validationResult !== "pass" || m3.validationResult !== "pass") {
    return { go: false, reason: "M1/M2/M3 must be pass" };
  }

  if (m4.validationResult !== "fail") {
    return { go: false, reason: "M4 must be fail" };
  }

  return { go: true, reason: "go" };
}
