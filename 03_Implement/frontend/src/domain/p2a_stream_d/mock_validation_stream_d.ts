import type { HandoffLogEntry, MockCaseId, OwnerOfFix, ValidationResult } from "./handoff_types";

type MockValidationFixture = {
  contractVersion: string;
  mockCaseId: MockCaseId;
  expectedResult: ValidationResult;
  expectedOwnerOfFix: OwnerOfFix;
  evidence: string;
};

const HIERARCHY_CONTRACT_VERSION = "IslandHierarchyContractV1";
const VISIBILITY_CONTRACT_VERSION = "IslandVisibilityContractV1";

export const HIERARCHY_FIXTURES_STREAM_D: readonly MockValidationFixture[] = [
  {
    contractVersion: HIERARCHY_CONTRACT_VERSION,
    mockCaseId: "M1",
    expectedResult: "pass",
    expectedOwnerOfFix: "A3",
    evidence: "root hierarchy accepted",
  },
  {
    contractVersion: HIERARCHY_CONTRACT_VERSION,
    mockCaseId: "M2",
    expectedResult: "pass",
    expectedOwnerOfFix: "A3",
    evidence: "three-level hierarchy accepted",
  },
  {
    contractVersion: HIERARCHY_CONTRACT_VERSION,
    mockCaseId: "M3",
    expectedResult: "fail",
    expectedOwnerOfFix: "A2",
    evidence: "missing parent rejected",
  },
  {
    contractVersion: HIERARCHY_CONTRACT_VERSION,
    mockCaseId: "M4",
    expectedResult: "fail",
    expectedOwnerOfFix: "A2",
    evidence: "cycle rejected",
  },
];

export const VISIBILITY_FIXTURES_STREAM_D: readonly MockValidationFixture[] = [
  {
    contractVersion: VISIBILITY_CONTRACT_VERSION,
    mockCaseId: "M1",
    expectedResult: "pass",
    expectedOwnerOfFix: "A3",
    evidence: "collapse hides descendants and cards",
  },
  {
    contractVersion: VISIBILITY_CONTRACT_VERSION,
    mockCaseId: "M2",
    expectedResult: "pass",
    expectedOwnerOfFix: "A3",
    evidence: "expand restores hiddenDescendantIslandIds/hiddenCardIds",
  },
  {
    contractVersion: VISIBILITY_CONTRACT_VERSION,
    mockCaseId: "M3",
    expectedResult: "pass",
    expectedOwnerOfFix: "A3",
    evidence: "double collapse remains idempotent",
  },
  {
    contractVersion: VISIBILITY_CONTRACT_VERSION,
    mockCaseId: "M4",
    expectedResult: "fail",
    expectedOwnerOfFix: "A2",
    evidence: "fail-fast on invalid island.id (required)",
  },
];

export const projectContractStubStreamD = (fixture: MockValidationFixture): HandoffLogEntry => ({
  contractVersion: fixture.contractVersion,
  mockCaseId: fixture.mockCaseId,
  validationResult: fixture.expectedResult,
  ownerOfFix: fixture.expectedOwnerOfFix,
  evidence: fixture.evidence,
});

export const evaluateInvariantStubStreamD = (
  logs: readonly HandoffLogEntry[],
): readonly HandoffLogEntry[] => logs.map((entry) => ({ ...entry }));

export const runMockValidationStreamD = (
  fixtures: readonly MockValidationFixture[],
): readonly HandoffLogEntry[] => evaluateInvariantStubStreamD(fixtures.map(projectContractStubStreamD));

