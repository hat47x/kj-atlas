import { describe, expect, it } from "vitest";

import { buildCe2ProposalOnlyState } from "./ce2_proposal_only";

describe("ce2_proposal_only", () => {
  it("enforces proposal-only boundary with safe mode on", () => {
    const state = buildCe2ProposalOnlyState({
      safeModeEnabled: true,
      previewEnabled: true,
      hasSuggestion: true,
    });

    expect(state).toEqual({
      canRequestProposal: true,
      canPreviewProposal: true,
      canAutoApply: false,
      blockers: ["auto_apply_blocked"],
    });
  });

  it("adds blockers when safe mode is off and no suggestion preview exists", () => {
    const state = buildCe2ProposalOnlyState({
      safeModeEnabled: false,
      previewEnabled: false,
      hasSuggestion: false,
    });

    expect(state.canRequestProposal).toBe(false);
    expect(state.canPreviewProposal).toBe(false);
    expect(state.canAutoApply).toBe(false);
    expect(state.blockers).toEqual([
      "auto_apply_blocked",
      "safe_mode_required",
      "suggestion_required",
      "preview_opt_in_required",
    ]);
  });
});
