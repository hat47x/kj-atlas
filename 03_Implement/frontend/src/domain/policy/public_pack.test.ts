import { describe, expect, it } from "vitest";

import { resolvePublicPackIdFromSearch } from "./public_pack";

describe("resolvePublicPackIdFromSearch", () => {
  it("returns null when pack query is absent", () => {
    expect(resolvePublicPackIdFromSearch("?readonly=1")).toBeNull();
  });

  it("returns trimmed pack id", () => {
    expect(resolvePublicPackIdFromSearch("?pack=%20public-main%20")).toBe("public-main");
  });

  it("returns null when pack query is empty", () => {
    expect(resolvePublicPackIdFromSearch("?pack=%20%20")).toBeNull();
  });
});
