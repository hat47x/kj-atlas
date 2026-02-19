import { describe, expect, test } from "vitest";
import { parseViewJson } from "./view_import";

describe("parseViewJson", () => {
  test("returns invalid json error", () => {
    const result = parseViewJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain("Invalid JSON in view.json");
    }
  });
});
