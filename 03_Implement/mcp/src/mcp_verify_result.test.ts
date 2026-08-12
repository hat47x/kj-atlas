import { describe, expect, it } from "vitest";
import { interpretProjectionResult } from "./mcp_verify_result.js";

describe("interpretProjectionResult", () => {
  it("parses a successful projection JSON when isError is false", () => {
    const text = JSON.stringify({ bundleHash: "a".repeat(64), schemaVersion: "context-projection.v1" });
    const result = interpretProjectionResult(text, false);

    expect(result.outcome).toBe("ok");
    expect(result.errorMessage).toBeNull();
    expect(result.projection).toEqual({ bundleHash: "a".repeat(64), schemaVersion: "context-projection.v1" });
  });

  it("reports not_found for a DocumentNotFound error message (DOGFOOD-03)", () => {
    // This is exactly what the MCP server returns for a missing doc: isError
    // true + a plain message that is NOT valid JSON. Previously verify_mcp.ts
    // crashed on JSON.parse; now it must be classified as not_found.
    const text = "Document not found: missing-doc";
    const result = interpretProjectionResult(text, true);

    expect(result.outcome).toBe("not_found");
    expect(result.errorMessage).toBe("Document not found: missing-doc");
    expect(result.projection).toBeNull();
  });

  it("reports not_found for a 404 message", () => {
    const result = interpretProjectionResult("Failed to fetch document x: HTTP 404", true);
    expect(result.outcome).toBe("not_found");
  });

  it("reports error (not not_found) for a generic failure message", () => {
    const result = interpretProjectionResult("upstream gateway timeout", true);
    expect(result.outcome).toBe("error");
    expect(result.projection).toBeNull();
  });

  it("reports error (not a throw) when a success-flagged result is not valid JSON", () => {
    const result = interpretProjectionResult("{ not json", false);
    expect(result.outcome).toBe("error");
    expect(result.errorMessage).toContain("invalid projection JSON");
    expect(result.projection).toBeNull();
  });

  it("never emits anti-scoring vocabulary in the interpretation", () => {
    const ok = interpretProjectionResult(JSON.stringify({ text: "clean" }), false);
    const notFound = interpretProjectionResult("Document not found", true);
    const err = interpretProjectionResult("gateway timeout", true);
    for (const r of [ok, notFound, err]) {
      expect(JSON.stringify(r).toLowerCase()).not.toMatch(/score|rank|confidence|priority|readiness/i);
    }
  });
});
