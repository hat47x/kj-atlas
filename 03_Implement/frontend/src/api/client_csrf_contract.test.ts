import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const source = readFileSync(new URL("./client.ts", import.meta.url), "utf8");

describe("API client CSRF contract", () => {
  it("keeps every unsafe API fetch near the shared tenant/CSRF header path", () => {
    const methodPattern = /method:\s*"(?:POST|PUT|PATCH|DELETE)"/g;
    const matches = [...source.matchAll(methodPattern)];
    expect(matches.length).toBeGreaterThan(0);
    for (const match of matches) {
      const offset = match.index ?? 0;
      const window = source.slice(Math.max(0, offset - 900), Math.min(source.length, offset + 900));
      expect(
        window.includes("tenantSessionPreconditionHeaders") || window.includes("csrfHeader"),
        `unsafe fetch near offset ${offset} bypasses the CSRF header path`,
      ).toBe(true);
    }
  });
});
