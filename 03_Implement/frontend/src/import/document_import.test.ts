import { describe, expect, test } from "vitest";
import { parseDocumentJson } from "./document_import";

describe("parseDocumentJson", () => {
  test("returns invalid json error", () => {
    const result = parseDocumentJson("{");
    expect(result.ok).toBe(false);
    if (!result.ok) {
      expect(result.error).toContain("Invalid JSON in document.json");
    }
  });
});
