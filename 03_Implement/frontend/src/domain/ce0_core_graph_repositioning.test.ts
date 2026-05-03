import { describe, expect, test } from "vitest";
import { validateCoreGraphRepositioning } from "./ce0_core_graph_repositioning";

describe("validateCoreGraphRepositioning", () => {
  test("passes when transition is working -> consensus with patch+approval", () => {
    const result = validateCoreGraphRepositioning({
      transition: { from: "working", to: "consensus", mode: "patch+approval" },
      safeModeDefaultOn: true,
      queryPreviewRequired: true,
    });

    expect(result).toEqual({ ok: true, reason: "ok" });
  });

  test("fails when query preview is bypassed", () => {
    const result = validateCoreGraphRepositioning({
      transition: { from: "working", to: "consensus", mode: "patch+approval" },
      safeModeDefaultOn: true,
      queryPreviewRequired: false,
    });

    expect(result.ok).toBe(false);
    expect(result.noGoId).toBe("preview_bypass");
  });

  test("fails when direct write targets consensus", () => {
    const result = validateCoreGraphRepositioning({
      transition: { from: "working", to: "consensus", mode: "direct_write" },
      safeModeDefaultOn: true,
      queryPreviewRequired: true,
    });

    expect(result.ok).toBe(false);
    expect(result.noGoId).toBe("consensus_direct_write");
  });
});
