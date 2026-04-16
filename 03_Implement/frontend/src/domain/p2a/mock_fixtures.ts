import {
  P2A02_CONTRACT_ID,
  P2A02_CONTRACT_VERSION,
  type P2AMockFixture,
} from "./contract";

export const P2A_A2_MOCK_FIXTURES: readonly P2AMockFixture[] = [
  {
    fixtureId: "F1",
    fileName: "visibility_collapse_valid.json",
    mockCaseId: "M1",
    payload: {
      contractId: P2A02_CONTRACT_ID,
      contractVersion: P2A02_CONTRACT_VERSION,
      mockCaseId: "M1",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "collapse hides descendants and cards",
    },
  },
  {
    fixtureId: "F2",
    fileName: "visibility_expand_restore_valid.json",
    mockCaseId: "M2",
    payload: {
      contractId: P2A02_CONTRACT_ID,
      contractVersion: P2A02_CONTRACT_VERSION,
      mockCaseId: "M2",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "expand restores hiddenDescendantIslandIds and hiddenCardIds",
    },
  },
  {
    fixtureId: "F3",
    fileName: "visibility_double_collapse_idempotent.json",
    mockCaseId: "M3",
    payload: {
      contractId: P2A02_CONTRACT_ID,
      contractVersion: P2A02_CONTRACT_VERSION,
      mockCaseId: "M3",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "double collapse remains idempotent",
    },
  },
  {
    fixtureId: "F4",
    fileName: "visibility_missing_island_invalid.json",
    mockCaseId: "M4",
    payload: {
      contractId: P2A02_CONTRACT_ID,
      contractVersion: P2A02_CONTRACT_VERSION,
      mockCaseId: "M4",
      validationResult: "fail",
      ownerOfFix: "A2",
      evidence: "fail-fast on unknown island.id request",
    },
  },
] as const;
