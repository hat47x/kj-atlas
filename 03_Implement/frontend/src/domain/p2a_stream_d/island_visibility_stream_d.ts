import {
  evaluateIslandVisibilityA3GoNoGo,
  type IslandVisibilityValidationLog,
} from "../view/island_visibility_handoff";
import {
  type GoNoGoReport,
  type HandoffLogEntry,
  REQUIRED_MOCK_CASES,
} from "./handoff_types";

const CONTRACT_VERSION = "IslandVisibilityContractV1";

const EXPECTED_RESULTS = {
  M1: "pass",
  M2: "pass",
  M3: "pass",
  M4: "fail",
} as const;

const EXPECTED_OWNER = {
  M1: "A3",
  M2: "A3",
  M3: "A3",
  M4: "A2",
} as const;

export const evaluateIslandVisibilityA3GoNoGoStreamD = (
  entries: HandoffLogEntry[],
): GoNoGoReport => {
  const byCase = new Map<string, HandoffLogEntry>();

  for (const entry of entries) {
    if (entry.contractVersion !== CONTRACT_VERSION) {
      throw new Error("contractVersion mismatch for IslandVisibilityContractV1");
    }
    if (byCase.has(entry.mockCaseId)) {
      throw new Error(`duplicate mockCaseId: ${entry.mockCaseId}`);
    }
    byCase.set(entry.mockCaseId, entry);
  }

  for (const mockCaseId of REQUIRED_MOCK_CASES) {
    if (!byCase.has(mockCaseId)) {
      return { go: false, reasons: [`missing mockCaseId: ${mockCaseId}`] };
    }
  }

  const logs = REQUIRED_MOCK_CASES.map((mockCaseId) => {
    const entry = byCase.get(mockCaseId)!;
    return {
      contractVersion: entry.contractVersion,
      mockCaseId,
      validationResult: entry.validationResult,
      ownerOfFix: entry.ownerOfFix,
      evidence: entry.evidence,
    } satisfies IslandVisibilityValidationLog;
  });

  const goNoGo = evaluateIslandVisibilityA3GoNoGo(logs);
  if (goNoGo.go) {
    return { go: true, reasons: [] };
  }

  const reasons: string[] = [];
  for (const mockCaseId of REQUIRED_MOCK_CASES) {
    const entry = byCase.get(mockCaseId)!;
    if (entry.validationResult !== EXPECTED_RESULTS[mockCaseId]) {
      reasons.push(`${mockCaseId} result mismatch`);
    }
    if (entry.ownerOfFix !== EXPECTED_OWNER[mockCaseId]) {
      reasons.push(`${mockCaseId} ownerOfFix mismatch`);
    }
  }

  if (reasons.length === 0) {
    reasons.push(goNoGo.reason);
  }

  return { go: false, reasons };
};
