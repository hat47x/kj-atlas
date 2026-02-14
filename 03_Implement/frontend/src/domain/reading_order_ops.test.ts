import { describe, expect, it } from "vitest";

import { appendReadingOrderEntry, moveReadingOrderEntry, removeReadingOrderEntry } from "./reading_order_ops";

describe("reading_order_ops", () => {
  it("appends only visible, missing entries", () => {
    const original = ["card-1"];
    expect(appendReadingOrderEntry(original, "card-2", new Set(["card-1", "card-2"]))).toEqual(["card-1", "card-2"]);
    expect(appendReadingOrderEntry(original, "card-1", new Set(["card-1"]))).toBe(original);
    expect(appendReadingOrderEntry(original, "card-3", new Set(["card-1", "card-2"]))).toBe(original);
  });

  it("removes by entry id", () => {
    expect(removeReadingOrderEntry(["a", "b", "c"], "b")).toEqual(["a", "c"]);
    const original = ["a", "b"];
    expect(removeReadingOrderEntry(original, "z")).toBe(original);
  });

  it("moves an entry before or after target", () => {
    const original = ["a", "b", "c", "d"];
    expect(moveReadingOrderEntry(original, "d", "b", "before")).toEqual(["a", "d", "b", "c"]);
    expect(moveReadingOrderEntry(original, "a", "c", "after")).toEqual(["b", "c", "a", "d"]);
    expect(moveReadingOrderEntry(original, "a", "a", "before")).toBe(original);
  });
});
