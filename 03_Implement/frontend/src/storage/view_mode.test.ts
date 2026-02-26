import { describe, expect, it } from "vitest";

import { parseViewModeByDoc } from "./view_mode";

describe("parseViewModeByDoc", () => {
  it("returns empty object for empty or invalid payload", () => {
    expect(parseViewModeByDoc(null)).toEqual({});
    expect(parseViewModeByDoc("")).toEqual({});
    expect(parseViewModeByDoc("not-json")).toEqual({});
    expect(parseViewModeByDoc("[]")).toEqual({});
    expect(parseViewModeByDoc("123")).toEqual({});
  });

  it("keeps only known mode entries keyed by non-empty doc id", () => {
    expect(
      parseViewModeByDoc(
        JSON.stringify({
          docA: "explore",
          docB: "review",
          docC: "summary",
          docD: "invalid",
          "": "review",
          1: "explore",
        }),
      ),
    ).toEqual({
      docA: "explore",
      docB: "review",
      docC: "summary",
      "1": "explore",
    });
  });
});
