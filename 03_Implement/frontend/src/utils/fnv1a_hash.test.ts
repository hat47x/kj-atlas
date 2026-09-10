import { describe, expect, it } from "vitest";

import { fnv1aHash } from "./fnv1a_hash";

describe("fnv1aHash", () => {
  it("is deterministic for the same input", () => {
    expect(fnv1aHash("sui-sensemaking")).toBe(fnv1aHash("sui-sensemaking"));
  });

  it("produces an 8-character lowercase hex digest", () => {
    expect(fnv1aHash("sui-sensemaking")).toMatch(/^[0-9a-f]{8}$/);
  });

  it("differs for different inputs", () => {
    expect(fnv1aHash("a")).not.toBe(fnv1aHash("b"));
  });

  it("matches the known FNV-1a digest for the empty string", () => {
    expect(fnv1aHash("")).toBe("811c9dc5");
  });
});
