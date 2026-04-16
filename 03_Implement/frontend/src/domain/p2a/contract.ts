export const P2A02_CONTRACT_ID = "CTR-2A-02-COLLAPSE-EXPAND-V1" as const;
export const P2A02_CONTRACT_VERSION = "IslandVisibilityContractV1" as const;

export type P2AMockCaseId = "M1" | "M2" | "M3" | "M4";
export type P2AOwnerOfFix = "A1" | "A2" | "A3";
export type P2AValidationResult = "pass" | "fail";

export type P2ARequiredField =
  | "island.id"
  | "island.isCollapsed"
  | "view.hiddenDescendantIslandIds"
  | "view.hiddenCardIds";

export type P2AInvariant =
  | "collapsed descendants are excluded from render/hit-test"
  | "expand restores previous visibility state"
  | "collapse/expand mutates view state only"
  | "collapse/expand does not change safeMode share/export gates";

export type P2AA1ContractLock = {
  contractId: typeof P2A02_CONTRACT_ID;
  contractVersion: typeof P2A02_CONTRACT_VERSION;
  requiredFields: readonly P2ARequiredField[];
  invariants: readonly P2AInvariant[];
};

export type P2AMockFixture = {
  fixtureId: string;
  fileName: string;
  mockCaseId: P2AMockCaseId;
  payload: {
    contractId: string;
    contractVersion: string;
    mockCaseId: string;
    validationResult: P2AValidationResult;
    ownerOfFix: P2AOwnerOfFix;
    evidence: string;
  };
};

export type P2AValidationLog = {
  contractId: typeof P2A02_CONTRACT_ID;
  contractVersion: typeof P2A02_CONTRACT_VERSION;
  mockCaseId: P2AMockCaseId;
  validationResult: P2AValidationResult;
  ownerOfFix: P2AOwnerOfFix;
  evidence: string;
};

const REQUIRED_FIELDS: readonly P2ARequiredField[] = [
  "island.id",
  "island.isCollapsed",
  "view.hiddenDescendantIslandIds",
  "view.hiddenCardIds",
] as const;

const INVARIANTS: readonly P2AInvariant[] = [
  "collapsed descendants are excluded from render/hit-test",
  "expand restores previous visibility state",
  "collapse/expand mutates view state only",
  "collapse/expand does not change safeMode share/export gates",
] as const;

export const P2A_A1_CONTRACT_LOCK: P2AA1ContractLock = {
  contractId: P2A02_CONTRACT_ID,
  contractVersion: P2A02_CONTRACT_VERSION,
  requiredFields: REQUIRED_FIELDS,
  invariants: INVARIANTS,
};
