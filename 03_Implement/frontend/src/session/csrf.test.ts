import { describe, expect, it } from "vitest";

import { CSRF_HEADER, csrfTokenFromCookie } from "./csrf";

const TOKEN = "a".repeat(64);

describe("session CSRF cookie", () => {
  it("extracts only the canonical bound token cookie", () => {
    expect(csrfTokenFromCookie(`other=x; Kj-Atlas-Csrf=${TOKEN}; tail=y`)).toBe(TOKEN);
  });

  it("rejects missing, malformed, and non-hex token values", () => {
    expect(csrfTokenFromCookie("other=x")).toBeUndefined();
    expect(csrfTokenFromCookie("Kj-Atlas-Csrf=short")).toBeUndefined();
    expect(csrfTokenFromCookie(`Kj-Atlas-Csrf=${"g".repeat(64)}`)).toBeUndefined();
  });

  it("keeps the wire header name stable", () => {
    expect(CSRF_HEADER).toBe("X-Kj-Atlas-Csrf");
  });
});
