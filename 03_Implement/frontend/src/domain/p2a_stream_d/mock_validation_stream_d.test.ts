import { describe, expect, it } from "vitest";

import {
  HIERARCHY_FIXTURES_STREAM_D,
  VISIBILITY_FIXTURES_STREAM_D,
  runMockValidationStreamD,
} from "./mock_validation_stream_d";

describe("runMockValidationStreamD", () => {
  it("produces hierarchy handoff logs with M1/M2 pass and M3/M4 fail", () => {
    const logs = runMockValidationStreamD(HIERARCHY_FIXTURES_STREAM_D);

    expect(logs).toEqual([
      {
        contractVersion: "IslandHierarchyContractV1",
        mockCaseId: "M1",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "root hierarchy accepted",
      },
      {
        contractVersion: "IslandHierarchyContractV1",
        mockCaseId: "M2",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "three-level hierarchy accepted",
      },
      {
        contractVersion: "IslandHierarchyContractV1",
        mockCaseId: "M3",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "missing parent rejected",
      },
      {
        contractVersion: "IslandHierarchyContractV1",
        mockCaseId: "M4",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "cycle rejected",
      },
    ]);
  });

  it("produces visibility handoff logs with M1/M2/M3 pass and M4 fail", () => {
    const logs = runMockValidationStreamD(VISIBILITY_FIXTURES_STREAM_D);

    expect(logs).toEqual([
      {
        contractVersion: "IslandVisibilityContractV1",
        mockCaseId: "M1",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "collapse hides descendants and cards",
      },
      {
        contractVersion: "IslandVisibilityContractV1",
        mockCaseId: "M2",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "expand restores hiddenDescendantIslandIds/hiddenCardIds",
      },
      {
        contractVersion: "IslandVisibilityContractV1",
        mockCaseId: "M3",
        validationResult: "pass",
        ownerOfFix: "A3",
        evidence: "double collapse remains idempotent",
      },
      {
        contractVersion: "IslandVisibilityContractV1",
        mockCaseId: "M4",
        validationResult: "fail",
        ownerOfFix: "A2",
        evidence: "fail-fast on invalid island.id (required)",
      },
    ]);
  });
});
