import { describe, expect, it } from "vitest";

import { mergeMethodFieldLabel, mergeMethodLabel } from "./merge_method_label";

describe("mergeMethodLabel", () => {
  it("keeps the two merge approaches explicit in Japanese", () => {
    expect(mergeMethodFieldLabel("ja")).toBe("統合方式");
    expect(mergeMethodLabel("near_duplicate", "ja")).toBe("類似カードの整理（04ステップ型）");
    expect(mergeMethodLabel("kernel_fusion", "ja")).toBe("意味核の統合（核融合法型）");
  });

  it("keeps the two merge approaches explicit in English", () => {
    expect(mergeMethodFieldLabel("en")).toBe("Merge method");
    expect(mergeMethodLabel("near_duplicate", "en")).toBe("Near-duplicate consolidation (04-step style)");
    expect(mergeMethodLabel("kernel_fusion", "en")).toBe("Meaning-kernel integration (KJ nuclear-fusion style)");
  });
});
