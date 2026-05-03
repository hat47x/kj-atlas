export type CoreGraphRole = "working" | "context_projection" | "consensus";

export type CoreGraphNoGoId =
  | "preview_bypass"
  | "consensus_direct_write"
  | "auto_apply_or_publish"
  | "ai_review_auto_promotion"
  | "safemode_default_relaxation";

export type CoreGraphTransition = {
  from: CoreGraphRole;
  to: CoreGraphRole;
  mode: "patch+approval" | "direct_write" | "auto_apply" | "auto_publish" | string;
};

export type CoreGraphRepositioningInput = {
  transition: CoreGraphTransition;
  safeModeDefaultOn: boolean;
  queryPreviewRequired: boolean;
};

export type CoreGraphValidationResult = {
  ok: boolean;
  noGoId?: CoreGraphNoGoId;
  reason: string;
};

export function validateCoreGraphRepositioning(input: CoreGraphRepositioningInput): CoreGraphValidationResult {
  const { transition, safeModeDefaultOn, queryPreviewRequired } = input;

  if (!queryPreviewRequired) {
    return { ok: false, noGoId: "preview_bypass", reason: "query preview is required" };
  }

  if (!safeModeDefaultOn) {
    return { ok: false, noGoId: "safemode_default_relaxation", reason: "safeMode default must remain ON" };
  }

  if (transition.to === "consensus" && transition.mode === "direct_write") {
    return { ok: false, noGoId: "consensus_direct_write", reason: "direct write into consensus is forbidden" };
  }

  if (transition.mode === "auto_apply" || transition.mode === "auto_publish") {
    return { ok: false, noGoId: "auto_apply_or_publish", reason: "auto apply/publish is forbidden" };
  }

  const isAllowed = transition.from === "working" && transition.to === "consensus" && transition.mode === "patch+approval";

  if (!isAllowed) {
    return {
      ok: false,
      noGoId: "ai_review_auto_promotion",
      reason: "only working -> consensus with patch+approval is allowed",
    };
  }

  return { ok: true, reason: "ok" };
}
