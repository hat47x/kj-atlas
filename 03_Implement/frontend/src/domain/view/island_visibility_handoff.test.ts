import { describe, expect, it } from "vitest";

import { validateIslandVisibilityContractV1, type ContractValidationResult, type IslandVisibilityContractV1 } from "../contracts/island_contracts";
import { evaluateIslandVisibilityA3GoNoGo, toIslandVisibilityValidationLog } from "./island_visibility_handoff";

function validValidationResult(isCollapsed: boolean): ContractValidationResult<IslandVisibilityContractV1> {
  return validateIslandVisibilityContractV1({
    island: { id: "root", isCollapsed },
    view: {
      hiddenDescendantIslandIds: isCollapsed ? ["child"] : [],
      hiddenCardIds: isCollapsed ? ["c-child", "c-root"] : [],
    },
  });
}

describe("toIslandVisibilityValidationLog", () => {
  it("builds A2 handoff logs for M1/M2/M3 pass cases", () => {
    const m1 = toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "collapse hides descendants");
    const m2 = toIslandVisibilityValidationLog("M2", validValidationResult(false), "A2", "expand restores hidden ids");
    const m3 = toIslandVisibilityValidationLog("M3", validValidationResult(true), "A2", "double collapse is idempotent");

    expect(m1).toEqual({
      contractVersion: "IslandVisibilityContractV1",
      mockCaseId: "M1",
      validationResult: "pass",
      ownerOfFix: "A3",
      evidence: "collapse hides descendants",
    });

    expect(m2.validationResult).toBe("pass");
    expect(m3.validationResult).toBe("pass");
  });

  it("builds fail-fast log for M4 with A2 ownership", () => {
    const invalid = validateIslandVisibilityContractV1({
      island: { id: "", isCollapsed: true },
      view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
    });

    const m4 = toIslandVisibilityValidationLog("M4", invalid, "A2", "unknown island id rejected");

    expect(m4.contractVersion).toBe("IslandVisibilityContractV1");
    expect(m4.mockCaseId).toBe("M4");
    expect(m4.validationResult).toBe("fail");
    expect(m4.ownerOfFix).toBe("A2");
    expect(m4.evidence).toContain("error=island.id is required");
  });
});

describe("evaluateIslandVisibilityA3GoNoGo", () => {
  it("returns Go when M1/M2/M3 are pass and M4 is fail", () => {
    const logs = [
      toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "M1"),
      toIslandVisibilityValidationLog("M2", validValidationResult(false), "A2", "M2"),
      toIslandVisibilityValidationLog("M3", validValidationResult(true), "A2", "M3"),
      toIslandVisibilityValidationLog(
        "M4",
        validateIslandVisibilityContractV1({
          island: { id: "", isCollapsed: true },
          view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
        }),
        "A2",
        "M4",
      ),
    ];

    expect(evaluateIslandVisibilityA3GoNoGo(logs)).toEqual({ go: true, reason: "go" });
  });



  it("returns NoGo when duplicate mock case is provided", () => {
    const logs = [
      toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "M1-first"),
      toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "M1-duplicate"),
      toIslandVisibilityValidationLog("M2", validValidationResult(false), "A2", "M2"),
      toIslandVisibilityValidationLog("M3", validValidationResult(true), "A2", "M3"),
      toIslandVisibilityValidationLog(
        "M4",
        validateIslandVisibilityContractV1({
          island: { id: "", isCollapsed: true },
          view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
        }),
        "A2",
        "M4",
      ),
    ];

    expect(evaluateIslandVisibilityA3GoNoGo(logs)).toEqual({ go: false, reason: "duplicate mock case: M1" });
  });

  it("returns NoGo when M4 ownerOfFix is A3", () => {
    const logs = [
      toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "M1"),
      toIslandVisibilityValidationLog("M2", validValidationResult(false), "A2", "M2"),
      toIslandVisibilityValidationLog("M3", validValidationResult(true), "A2", "M3"),
      toIslandVisibilityValidationLog(
        "M4",
        validateIslandVisibilityContractV1({
          island: { id: "", isCollapsed: true },
          view: { hiddenDescendantIslandIds: [], hiddenCardIds: [] },
        }),
        "A3",
        "M4-invalid-owner",
      ),
    ];

    const result = evaluateIslandVisibilityA3GoNoGo(logs);
    expect(result.go).toBe(false);
    expect(result.reason).toBe("M4 ownerOfFix must not be A3");
  });
  it("returns NoGo when handoff payload has missing mock case", () => {
    const logs = [
      toIslandVisibilityValidationLog("M1", validValidationResult(true), "A2", "M1"),
      toIslandVisibilityValidationLog("M2", validValidationResult(false), "A2", "M2"),
      toIslandVisibilityValidationLog("M4", validValidationResult(true), "A2", "M4-incorrect"),
    ];

    const result = evaluateIslandVisibilityA3GoNoGo(logs);

    expect(result.go).toBe(false);
    expect(result.reason).toBe("missing mock case: M3");
  });
});
