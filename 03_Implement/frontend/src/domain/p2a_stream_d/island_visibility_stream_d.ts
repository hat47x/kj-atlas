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
  const reasons: string[] = [];
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
    const entry = byCase.get(mockCaseId);
    if (!entry) {
      reasons.push(`missing mockCaseId: ${mockCaseId}`);
      continue;
    }
    if (entry.validationResult !== EXPECTED_RESULTS[mockCaseId]) {
      reasons.push(`${mockCaseId} result mismatch`);
    }
    if (entry.ownerOfFix !== EXPECTED_OWNER[mockCaseId]) {
      reasons.push(`${mockCaseId} ownerOfFix mismatch`);
    }
  }

  return { go: reasons.length === 0, reasons };
};
