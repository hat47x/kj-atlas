export type HilRsGovernanceGateInput = {
  freezeContractId: string;
  schemaVersion: string;
  overridePolicy: string;
  contractLinkLocked: boolean;
  sharedResourceFreeze: boolean;
  safeModeDefault: string;
  safeModeBoundary: string;
  a1Status: string;
  pendingDecisionQueueCount: number;
  hasUndefinedContractChangeRequest: boolean;
  hasSafeModeRegressionRequest: boolean;
  hasShareExportLeakageRelaxationRequest: boolean;
};

export type HilRsGovernanceGateResult = {
  go: boolean;
  noGo: boolean;
  reasons: string[];
};

const FREEZE_CONTRACT_ID = "HIL-RS-02-A1-CONTRACT-FREEZE-v1";
const SCHEMA_VERSION = "1.0.0";
const OVERRIDE_POLICY = "human_dual_control_only";
const SAFE_MODE_DEFAULT = "ON";
const SAFE_MODE_BOUNDARY = "SAFE_MODE_STRICT_ON";
const A1_STATUS_DONE = "Done";

export function evaluateHilRsGovernanceGate(input: HilRsGovernanceGateInput): HilRsGovernanceGateResult {
  const reasons: string[] = [];

  if (input.freezeContractId !== FREEZE_CONTRACT_ID) reasons.push("freeze_contract_id_mismatch");
  if (input.schemaVersion !== SCHEMA_VERSION) reasons.push("schema_version_mismatch");
  if (input.overridePolicy !== OVERRIDE_POLICY) reasons.push("override_policy_mismatch");
  if (!input.contractLinkLocked) reasons.push("contract_link_unlocked");
  if (!input.sharedResourceFreeze) reasons.push("shared_resource_not_frozen");
  if (input.safeModeDefault !== SAFE_MODE_DEFAULT) reasons.push("safe_mode_default_mismatch");
  if (input.safeModeBoundary !== SAFE_MODE_BOUNDARY) reasons.push("safe_mode_boundary_mismatch");
  if (input.a1Status !== A1_STATUS_DONE) reasons.push("a1_not_done");
  if (input.pendingDecisionQueueCount !== 0) reasons.push("pending_decision_exists");
  if (input.hasUndefinedContractChangeRequest) reasons.push("undefined_contract_change_request");
  if (input.hasSafeModeRegressionRequest) reasons.push("safe_mode_regression_request");
  if (input.hasShareExportLeakageRelaxationRequest) reasons.push("share_export_leakage_relaxation_request");

  const go = reasons.length === 0;
  return { go, noGo: !go, reasons };
}
