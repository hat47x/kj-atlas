import { beforeEach, describe, expect, it } from "vitest";

import type { Island } from "../domain/types";
import { resolveIslandDisplayTitle } from "./island_title";
import { setActiveLocale } from "./translate";

const untitledIsland: Island = {
  id: "island-b",
  title: "",
  cardIds: [],
};

const islands: Island[] = [
  { id: "island-a", title: "利用者が付けた名前", cardIds: [] },
  untitledIsland,
];

describe("resolveIslandDisplayTitle", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("keeps authored titles unchanged", () => {
    expect(resolveIslandDisplayTitle(islands[0], islands)).toBe("利用者が付けた名前");
  });

  it("derives a numbered Japanese title without mutating the document value", () => {
    expect(resolveIslandDisplayTitle(untitledIsland, islands)).toBe("島 2");
    expect(untitledIsland.title).toBe("");
  });

  it("derives the equivalent English title from the same document", () => {
    setActiveLocale("en");
    expect(resolveIslandDisplayTitle(untitledIsland, islands)).toBe("Island 2");
    expect(untitledIsland.title).toBe("");
  });

  it("preserves legacy stored Island N titles", () => {
    const legacyIsland: Island = { id: "legacy", title: "Island 7", cardIds: [] };
    expect(resolveIslandDisplayTitle(legacyIsland, [legacyIsland])).toBe("Island 7");
  });
});
