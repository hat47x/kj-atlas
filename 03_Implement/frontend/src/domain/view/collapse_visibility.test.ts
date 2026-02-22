import { describe, expect, it } from "vitest";

import { getCollapsedHiddenCardIds } from "./collapse_visibility";

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
});
