import { describe, expect, it } from "vitest";
import { SafeModePolicy } from "./safe_mode";

describe("SafeModePolicy", () => {
  it("blocks text exposure in share/review contexts when safe mode is on", () => {
    expect(SafeModePolicy.canExposeText("card.text", "share", true)).toBe(false);
    expect(SafeModePolicy.canExposeText("card.text", "review-pack", true)).toBe(false);
    expect(SafeModePolicy.canExposeText("card.text", "ui", true)).toBe(true);
  });

  it("redacts and summarizes text", () => {
    const text = "SECRET_TEXT_DO_NOT_LEAK";
    expect(SafeModePolicy.redactText(text, true)).toContain("[REDACTED]");
    expect(SafeModePolicy.summarizeForSafeMode(text)).not.toContain(text);
  });
});
