import { beforeEach, describe, expect, it } from "vitest";

import { formatTimestamp } from "./format_timestamp";
import { setActiveLocale } from "../i18n/translate";

describe("formatTimestamp", () => {
  beforeEach(() => {
    setActiveLocale("ja");
  });

  it("formats a valid ISO timestamp instead of returning it verbatim", () => {
    const raw = "2026-07-20T09:14:03.512Z";
    expect(formatTimestamp(raw)).not.toBe(raw);
  });

  it("formats the same instant differently across locales", () => {
    const raw = "2026-07-20T09:14:03.512Z";
    setActiveLocale("ja");
    const ja = formatTimestamp(raw);
    setActiveLocale("en");
    const en = formatTimestamp(raw);
    expect(ja).not.toBe(en);
  });

  it("returns the original string unchanged for an unparseable value", () => {
    expect(formatTimestamp("not-a-date")).toBe("not-a-date");
  });
});
