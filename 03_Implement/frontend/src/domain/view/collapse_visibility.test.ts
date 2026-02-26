import { describe, expect, it } from "vitest";

import {
  collectCollapsedIslandIds,
  collectInitiallyCollapsedIslandIds,
  getCollapsedHiddenCardIds,
} from "./collapse_visibility";

describe("collectCollapsedIslandIds", () => {
  it("includes descendants of explicitly collapsed islands", () => {
    const collapsed = collectCollapsedIslandIds(
      [
        { id: "root", cardIds: ["c-root"] },
        { id: "child", cardIds: ["c-child"], parentIslandId: "root" },
        { id: "grand", cardIds: ["c-grand"], parentIslandId: "child" },
        { id: "other", cardIds: ["c-other"] },
      ],
      new Set(["root"])
    );

    expect([...collapsed].sort()).toEqual(["child", "grand", "root"]);
  });

  it("ignores unknown island ids", () => {
    const collapsed = collectCollapsedIslandIds(
      [{ id: "a", cardIds: ["c1"] }],
      new Set(["missing"])
    );

    expect([...collapsed]).toEqual([]);
  });
});

describe("collectInitiallyCollapsedIslandIds", () => {
  it("expands persisted collapsed flags to descendants", () => {
    const collapsed = collectInitiallyCollapsedIslandIds([
      { id: "p", cardIds: [], collapsed: true },
      { id: "c", cardIds: ["c1"], parentIslandId: "p" },
    ]);

    expect([...collapsed].sort()).toEqual(["c", "p"]);
  });
});

describe("getCollapsedHiddenCardIds", () => {
  it("hides cards that belong to collapsed islands", () => {
    const hidden = getCollapsedHiddenCardIds(
      {
        islands: [
          { id: "i1", cardIds: ["c1", "c2"] },
          { id: "i2", cardIds: ["c3"] },
        ],
      },
      new Set(["i2"])
    );

    expect([...hidden].sort()).toEqual(["c3"]);
  });

  it("hides cards for all collapsed descendants", () => {
    const hidden = getCollapsedHiddenCardIds(
      {
        islands: [
          { id: "root", cardIds: ["a"] },
          { id: "child", cardIds: ["b"], parentIslandId: "root" },
          { id: "grand", cardIds: ["c"], parentIslandId: "child" },
        ],
      },
      new Set(["root", "child", "grand"])
    );

    expect([...hidden].sort()).toEqual(["a", "b", "c"]);
  });
});
