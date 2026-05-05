import { describe, expect, it } from "vitest";
import { evaluateHilRsGovernanceGate } from "./hil_rs_governance_gate";

describe("evaluateHilRsGovernanceGate", () => {
  it("returns Go when all A1 freeze conditions are satisfied", () => {
    const result = evaluateHilRsGovernanceGate({
      freezeContractId: "HIL-RS-02-A1-CONTRACT-FREEZE-v1",
      schemaVersion: "1.0.0",
      overridePolicy: "human_dual_control_only",
      contractLinkLocked: true,
      sharedResourceFreeze: true,
      safeModeDefault: "ON",
      safeModeBoundary: "SAFE_MODE_STRICT_ON",
      a1Status: "Done",
      pendingDecisionQueueCount: 0,
      hasUndefinedContractChangeRequest: false,
      hasSafeModeRegressionRequest: false,
      hasShareExportLeakageRelaxationRequest: false,
    });

    expect(result).toEqual({ go: true, noGo: false, reasons: [] });
  });

  it("returns NoGo with reason set when fixed values drift", () => {
    const result = evaluateHilRsGovernanceGate({
      freezeContractId: "HIL-RS-02-A1-CONTRACT-FREEZE-v2",
      schemaVersion: "2.0.0",
      overridePolicy: "ai_only_override",
      contractLinkLocked: false,
      sharedResourceFreeze: false,
      safeModeDefault: "OFF",
      safeModeBoundary: "SAFE_MODE_RELAXED",
      a1Status: "InProgress",
      pendingDecisionQueueCount: 2,
      hasUndefinedContractChangeRequest: true,
      hasSafeModeRegressionRequest: true,
      hasShareExportLeakageRelaxationRequest: true,
    });

    expect(result.go).toBe(false);
    expect(result.noGo).toBe(true);
    expect(result.reasons).toEqual([
      "freeze_contract_id_mismatch",
      "schema_version_mismatch",
      "override_policy_mismatch",
      "contract_link_unlocked",
      "shared_resource_not_frozen",
      "safe_mode_default_mismatch",
      "safe_mode_boundary_mismatch",
      "a1_not_done",
      "pending_decision_exists",
      "undefined_contract_change_request",
      "safe_mode_regression_request",
      "share_export_leakage_relaxation_request",
    ]);
  });

  it("tolerates whitespace in fixed-value fields", () => {
    const result = evaluateHilRsGovernanceGate({
      freezeContractId: "  HIL-RS-02-A1-CONTRACT-FREEZE-v1  ",
      schemaVersion: " 1.0.0 ",
      overridePolicy: " human_dual_control_only ",
      contractLinkLocked: true,
      sharedResourceFreeze: true,
      safeModeDefault: " ON ",
      safeModeBoundary: " SAFE_MODE_STRICT_ON ",
      a1Status: " Done ",
      pendingDecisionQueueCount: 0,
      hasUndefinedContractChangeRequest: false,
      hasSafeModeRegressionRequest: false,
      hasShareExportLeakageRelaxationRequest: false,
    });

    expect(result).toEqual({ go: true, noGo: false, reasons: [] });
  });
});
