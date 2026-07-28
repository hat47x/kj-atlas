import { describe, expect, it } from "vitest";

import { stableSerialize } from "./stable_serialize";

describe("stableSerialize", () => {
  it("produces identical output regardless of key insertion order", () => {
    expect(stableSerialize({ b: 1, a: 2 })).toBe(stableSerialize({ a: 2, b: 1 }));
  });

  it("sorts keys lexicographically in the output", () => {
    expect(stableSerialize({ b: 1, a: 2 })).toBe('{"a":2,"b":1}');
  });

  it("recurses into arrays and nested objects", () => {
    expect(stableSerialize([{ b: 1, a: 2 }, { d: 3, c: 4 }])).toBe('[{"a":2,"b":1},{"c":4,"d":3}]');
  });

  it("passes primitives through JSON.stringify unchanged", () => {
    expect(stableSerialize("text")).toBe('"text"');
    expect(stableSerialize(42)).toBe("42");
    expect(stableSerialize(null)).toBe("null");
  });
});
