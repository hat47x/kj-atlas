import { describe, expect, it } from "vitest";

import {
  type ContractValidationResult,
  validateIslandHierarchyContractV1,
  validateIslandVisibilityContractV1,
} from "./island_contracts";

type HandoffPayload = {
  contractVersion: "IslandHierarchyContractV1" | "IslandVisibilityContractV1";
  mockCaseId: string;
  validationResult: "pass" | "fail";
  ownerOfFix: "A1" | "A2" | "A3";
};

function toHandoffPayload(
  contractVersion: HandoffPayload["contractVersion"],
  mockCaseId: string,
  result: ContractValidationResult<unknown>,
  ownerOfFixOnFailure: HandoffPayload["ownerOfFix"],
): HandoffPayload {
  if (result.ok) {
    return { contractVersion, mockCaseId, validationResult: "pass", ownerOfFix: "A3" };
  }

  return { contractVersion, mockCaseId, validationResult: "fail", ownerOfFix: ownerOfFixOnFailure };
}

describe("IslandHierarchyContractV1 mock validation", () => {
  it("M1: accepts root island with parentIslandId=null", () => {
    const result = validateIslandHierarchyContractV1({
      schemaVersion: "2.0.0",
      islands: [{ id: "root", parentIslandId: null, childIslandIds: [] }],
    });

    expect(result.ok).toBe(true);
    expect(toHandoffPayload("IslandHierarchyContractV1", "M1", result, "A2")).toEqual({
      contractVersion: "IslandHierarchyContractV1",
      mockCaseId: "M1",
      validationResult: "pass",
      ownerOfFix: "A3",
    });
  });

  it("M2: accepts 3-level hierarchy", () => {
    const result = validateIslandHierarchyContractV1({
      schemaVersion: "2.0.0",
      islands: [
        { id: "root", parentIslandId: null, childIslandIds: ["child"] },
        { id: "child", parentIslandId: "root", childIslandIds: ["grand"] },
        { id: "grand", parentIslandId: "child", childIslandIds: [] },
      ],
    });

    expect(result.ok).toBe(true);
  });

  it("M3: rejects missing parent reference with fail-fast", () => {
    const result = validateIslandHierarchyContractV1({
      schemaVersion: "2.0.0",
      islands: [{ id: "child", parentIslandId: "unknown", childIslandIds: [] }],
    });

    expect(result.ok).toBe(false);
    expect(toHandoffPayload("IslandHierarchyContractV1", "M3", result, "A1")).toEqual({
      contractVersion: "IslandHierarchyContractV1",
      mockCaseId: "M3",
      validationResult: "fail",
      ownerOfFix: "A1",
    });
  });

  it("M4: rejects cyclic reference with fail-fast", () => {
    const result = validateIslandHierarchyContractV1({
      schemaVersion: "2.0.0",
      islands: [
        { id: "a", parentIslandId: "b", childIslandIds: ["b"] },
        { id: "b", parentIslandId: "a", childIslandIds: ["a"] },
      ],
    });

    expect(result.ok).toBe(false);
  });
});

describe("IslandVisibilityContractV1 mock validation", () => {
  it("M1/M2/M3: accepts collapse, expand, and idempotent payloads", () => {
    const collapse = validateIslandVisibilityContractV1({
      island: { id: "root", isCollapsed: true },
      view: { hiddenDescendantIslandIds: ["child", "grand"], hiddenCardIds: ["c-child", "c-grand"] },
    });

    const expand = validateIslandVisibilityContractV1({
      island: { id: "root", isCollapsed: false },
      view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
    });

    const idempotent = validateIslandVisibilityContractV1({
      island: { id: "root", isCollapsed: true },
      view: { hiddenDescendantIslandIds: ["child"], hiddenCardIds: ["c-child"] },
    });

    expect(collapse.ok).toBe(true);
    expect(expand.ok).toBe(true);
    expect(idempotent.ok).toBe(true);
  });

  it("M4: rejects missing island id with fail-fast", () => {
    const result = validateIslandVisibilityContractV1({
      island: { id: "", isCollapsed: true },
      view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
    });

    expect(result.ok).toBe(false);
    expect(toHandoffPayload("IslandVisibilityContractV1", "M4", result, "A2")).toEqual({
      contractVersion: "IslandVisibilityContractV1",
      mockCaseId: "M4",
      validationResult: "fail",
      ownerOfFix: "A2",
    });
  });
});
