export type MockCaseId = "M1" | "M2" | "M3" | "M4";
export type ValidationResult = "pass" | "fail";
export type OwnerOfFix = "A1" | "A2" | "A3";

export type HandoffLogEntry = {
  contractVersion: string;
  mockCaseId: MockCaseId;
  validationResult: ValidationResult;
  ownerOfFix: OwnerOfFix;
  evidence: string;
};

export type GoNoGoReport = {
  go: boolean;
  reasons: string[];
};

export const REQUIRED_MOCK_CASES: readonly MockCaseId[] = ["M1", "M2", "M3", "M4"];
