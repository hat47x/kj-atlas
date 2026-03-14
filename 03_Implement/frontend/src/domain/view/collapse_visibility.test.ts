import { describe, expect, it } from "vitest";

import {
  buildIslandVisibilityContractPayload,
  collectCollapsedIslandIds,
  collectHiddenDescendantIslandIds,
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


describe("collectHiddenDescendantIslandIds", () => {
  it("collects descendants only (excluding the collapsed island itself)", () => {
    const hidden = collectHiddenDescendantIslandIds(
      [
        { id: "root", cardIds: ["c-root"] },
        { id: "child", cardIds: ["c-child"], parentIslandId: "root" },
        { id: "grand", cardIds: ["c-grand"], parentIslandId: "child" },
      ],
      new Set(["root"])
    );

    expect([...hidden].sort()).toEqual(["child", "grand"]);
  });
});

describe("buildIslandVisibilityContractPayload", () => {
  it("M1/M2/M3: builds valid contract payload for collapse/expand/idempotent cases", () => {
    const doc = {
      islands: [
        { id: "root", cardIds: ["c-root"] },
        { id: "child", cardIds: ["c-child"], parentIslandId: "root" },
        { id: "grand", cardIds: ["c-grand"], parentIslandId: "child" },
      ],
    };

    const collapse = buildIslandVisibilityContractPayload(doc, new Set(["root"]), "root");
    const expand = buildIslandVisibilityContractPayload(doc, new Set(), "root");
    const idempotent = buildIslandVisibilityContractPayload(doc, new Set(["root"]), "root");

    expect(collapse.ok).toBe(true);
    expect(expand.ok).toBe(true);
    expect(idempotent.ok).toBe(true);

    if (collapse.ok) {
      expect(collapse.value.view.hiddenDescendantIslandIds).toEqual(["child", "grand"]);
      expect(collapse.value.view.hiddenCardIds).toEqual(["c-child", "c-grand", "c-root"]);
    }
    if (expand.ok) {
      expect(expand.value.view.hiddenDescendantIslandIds).toEqual([]);
      expect(expand.value.view.hiddenCardIds).toEqual([]);
    }
  });

  it("M4: returns fail-fast when target island does not exist", () => {
    const result = buildIslandVisibilityContractPayload({ islands: [{ id: "root", cardIds: ["c-root"] }] }, new Set(["missing"]), "missing");
    expect(result).toEqual({ ok: false, error: "unknown island.id: missing" });
  });
});
