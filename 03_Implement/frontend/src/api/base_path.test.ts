import { describe, expect, it } from "vitest";

import { resolveFrontendApiBase } from "./base_path";

describe("frontend API base path", () => {
  it.each([
    [undefined, "/api"],
    [null, "/api"],
    ["", "/api"],
    ["   ", "/api"],
    ["/api", "/api"],
    [" /api/ ", "/api"],
    ["/nested/api///", "/nested/api"],
    ["/", ""],
  ])("normalizes %j to a same-origin path prefix", (rawValue, expected) => {
    expect(resolveFrontendApiBase(rawValue)).toBe(expected);
  });

  it.each([
    "api",
    "https://example.invalid/api",
    "//example.invalid/api",
    "///example.invalid/api",
    "/\\example.invalid/api",
    "/api?tenant=other",
    "/api#fragment",
    "/api\nother",
  ])("rejects non-path or cross-origin-capable value %j", (rawValue) => {
    expect(resolveFrontendApiBase(rawValue)).toBe("/api");
  });
});
