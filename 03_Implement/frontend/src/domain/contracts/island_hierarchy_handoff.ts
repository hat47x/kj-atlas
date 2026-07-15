import type { DocumentV1 } from "../types";
import {
  type ContractValidationResult,
  type IslandHierarchyContractV1Document,
  validateIslandHierarchyContractV1,
} from "./island_contracts";

export type IslandHierarchyMockCaseId = "M1" | "M2" | "M3" | "M4";
export type IslandHierarchyOwnerOfFix = "A1" | "A2" | "A3";

export type IslandHierarchyValidationLog = {
  contractVersion: "IslandHierarchyContractV1";
  mockCaseId: IslandHierarchyMockCaseId;
  validationResult: "pass" | "fail";
  ownerOfFix: IslandHierarchyOwnerOfFix;
  evidence: string;
};

export function projectIslandHierarchyContractV1(document: DocumentV1): IslandHierarchyContractV1Document {
  return {
    schemaVersion: String(document.version),
    islands: document.islands.map((island) => ({
      id: island.id,
      parentIslandId: island.parentIslandId ?? null,
      childIslandIds: document.islands.filter((candidate) => candidate.parentIslandId === island.id).map((candidate) => candidate.id),
    })),
  };
}

export function toIslandHierarchyValidationLog(
  mockCaseId: IslandHierarchyMockCaseId,
  validation: ContractValidationResult<IslandHierarchyContractV1Document>,
  ownerOnFailure: IslandHierarchyOwnerOfFix,
  evidence: string,
): IslandHierarchyValidationLog {
  if (validation.ok) {
    return {
      contractVersion: "IslandHierarchyContractV1",
      mockCaseId,
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence,
    };
  }

  return {
    contractVersion: "IslandHierarchyContractV1",
    mockCaseId,
    validationResult: "fail",
    ownerOfFix: ownerOnFailure,
    evidence: `${evidence}; error=${validation.error}`,
  };
}

export function evaluateIslandHierarchyA3GoNoGo(logs: IslandHierarchyValidationLog[]): { go: boolean; reason: string } {
  const byCase = new Map<IslandHierarchyMockCaseId, IslandHierarchyValidationLog>();
  for (const log of logs) {
    if (byCase.has(log.mockCaseId)) {
      return { go: false, reason: `duplicate mock case: ${log.mockCaseId}` };
    }
    if (log.contractVersion !== "IslandHierarchyContractV1") {
      return { go: false, reason: `contract version mismatch: ${log.contractVersion}` };
    }
    byCase.set(log.mockCaseId, log);
  }

  const requiredCases: IslandHierarchyMockCaseId[] = ["M1", "M2", "M3", "M4"];
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

  if (m1.validationResult !== "pass" || m2.validationResult !== "pass") {
    return { go: false, reason: "M1/M2 must be pass" };
  }
  if (m3.validationResult !== "fail" || m4.validationResult !== "fail") {
    return { go: false, reason: "M3/M4 must be fail" };
  }

  if (m1.ownerOfFix !== "A3" || m2.ownerOfFix !== "A3") {
    return { go: false, reason: "pass cases must be owned by A3" };
  }

  if (m3.ownerOfFix === "A3" || m4.ownerOfFix === "A3") {
    return { go: false, reason: "fail cases must route to A1/A2" };
  }

  return { go: true, reason: "go" };
}

export function validateIslandHierarchyRoundTrip(document: DocumentV1): ContractValidationResult<IslandHierarchyContractV1Document> {
  const projected = projectIslandHierarchyContractV1(document);
  const reloaded = JSON.parse(JSON.stringify(projected)) as IslandHierarchyContractV1Document;
  return validateIslandHierarchyContractV1(reloaded);
}
