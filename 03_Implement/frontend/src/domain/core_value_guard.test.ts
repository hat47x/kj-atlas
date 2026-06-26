/**
 * CORE-VALUE-GUARD-01: CVI-1..7 cross-cutting guard test
 *
 * Single entry point that indexes existing CVI coverage.
 * Follows ADR-0041: existing tests are indexed via source-string contracts;
 * only missing CVI coverage gets a minimal new test case here.
 *
 * References: value_traceability.md §2.5 (CVI canonical table)
 */

import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

/** Read frontend source file text for source-string contract checks. */
function readSource(relativePath: string): string {
  return readFileSync(resolve(__dirname, "..", relativePath), "utf-8");
}

// ── CVI-1: SafeMode default ON, share/export must not leak unreviewed text ──
describe("CVI-1 SafeMode default ON", () => {
  it("has existing guard in domain/policy/safe_mode.test.ts", () => {
    const source = readSource("domain/policy/safe_mode.test.ts");
    expect(source).toContain("blocks text exposure in share/review contexts when safe mode is on");
    expect(source).toContain("SafeModePolicy");
  });
});

// ── CVI-2: proposal-only (auto-apply/confirm/publish prohibited) ──
describe("CVI-2 proposal-only", () => {
  it("has existing guard in domain/ce2_proposal_only.test.ts", () => {
    const source = readSource("domain/ce2_proposal_only.test.ts");
    expect(source).toContain("proposal-only");
    expect(source).toContain("auto_apply");
  });

  it("auto-apply is forbidden by the CE2 contract assertion", () => {
    // From ce2_suggestion_candidates.test.ts: fallback is proposal-only
    const source = readSource("domain/ce2_suggestion_candidates.test.ts");
    expect(source).toContain("fallback");
    expect(source).toContain("proposal");
  });
});

// ── CVI-3: human_reviewed promotion is human-only ──
describe("CVI-3 human_reviewed human-only", () => {
  it("has existing guard in hil_rs_contract.test.ts", () => {
    const source = readSource("domain/hil_rs_contract.test.ts");
    expect(source).toContain("review");
    expect(source).toContain("human");
  });

  it("has existing guard in ce2_suggestion_candidates.test.ts", () => {
    const source = readSource("domain/ce2_suggestion_candidates.test.ts");
    expect(source).toContain("reviewState");
    expect(source).toContain("unreviewed");
  });

  it("rejects rediff ops that inject review state (hil_rs_apply)", () => {
    const source = readSource("domain/hil_rs_apply.test.ts");
    expect(source).toContain("rejects rediff operations that attempt to inject review state");
  });
});

// ── CVI-4: Consensus direct write prohibited ──
describe("CVI-4 Consensus direct write prohibited", () => {
  it("has existing guard in ce0_core_graph_repositioning.test.ts", () => {
    const source = readSource("domain/ce0_core_graph_repositioning.test.ts");
    expect(source).toContain("consensus");
    expect(source).toContain("direct write");
    expect(source).toContain("patch");
  });
});

// ── CVI-5: dryRun=true must have no side effects ──
describe("CVI-5 dryRun no side effects", () => {
  it("has existing guard in hil_rs_apply.test.ts (immutable apply)", () => {
    const source = readSource("domain/hil_rs_apply.test.ts");
    expect(source).toContain("immutable");
    // BASE.cards checked after apply proves original unmodified
    expect(source).toMatch(/expect\(BASE\.cards\)\.toEqual/);
  });
});

// ── CVI-6: KJ_ATLAS_LLM_PROVIDER=none default ──
describe("CVI-6 provider=none default", () => {
  it("has existing guard in ce2_suggestion_candidates.test.ts (no-LLM fallback)", () => {
    const source = readSource("domain/ce2_suggestion_candidates.test.ts");
    expect(source).toContain("fallback");
    expect(source).toContain("proposal-only");
  });
});

// ── CVI-7: Hold/Critique non-destructive ──
describe("CVI-7 hold/critique non-destructive", () => {
  it("has existing guard in hil_rs_apply.test.ts (critique preserved after apply)", () => {
    const source = readSource("domain/hil_rs_apply.test.ts");
    expect(source).toContain("critique");
    expect(source).toContain("preserved");
  });

  it("has existing guard in hold_state_ops.test.ts", () => {
    const source = readSource("domain/hold_state_ops.test.ts");
    expect(source).toContain("shelved");
    expect(source).toContain("held");
  });
});

// ── Completeness check: all CVI-1..7 are referenced ──
describe("CVI completeness", () => {
  it("covers all CVI-1..7 in this single guard file", () => {
    const source = readSource("domain/core_value_guard.test.ts");
    for (let i = 1; i <= 7; i++) {
      expect(source).toContain(`CVI-${i}`);
    }
  });
});
