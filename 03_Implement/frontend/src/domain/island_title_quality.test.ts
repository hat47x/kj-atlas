import { describe, expect, it } from "vitest";

import { inspectIslandTitle } from "./island_title_quality";

describe("inspectIslandTitle (AI-TITLE-01)", () => {
  it("flags exact universal phrases as not grounded", () => {
    const result = inspectIslandTitle("重要な論点", [
      "高齢者は一人で買い物に行けない",
      "商店街の店が次々と閉店している",
    ]);
    expect(result.isUniversal).toBe(true);
    expect(result.grounded).toBe(false);
  });

  it("flags generic analysis markers as universal", () => {
    const result = inspectIslandTitle("買い物弱者について", [
      "高齢者は一人で買い物に行けない",
    ]);
    expect(result.isUniversal).toBe(true);
  });

  it("accepts a placard grounded in card vocabulary", () => {
    const result = inspectIslandTitle("高齢者の買い物困難", [
      "高齢者は一人で買い物に行けない",
      "商店街の店が次々と閉店している",
      "バスの本数が減って不便になっている",
    ]);
    expect(result.isUniversal).toBe(false);
    expect(result.grounded).toBe(true);
  });

  it("flags a floating title with no card overlap", () => {
    const result = inspectIslandTitle("全体的な様子", [
      "高齢者は一人で買い物に行けない",
      "宅配サービスを利用する高齢者が増えている",
    ]);
    expect(result.isUniversal).toBe(true);
  });

  it("treats empty title as universal (must be fixed)", () => {
    const result = inspectIslandTitle("  ", ["何らかのカード"]);
    expect(result.isUniversal).toBe(true);
  });
});
