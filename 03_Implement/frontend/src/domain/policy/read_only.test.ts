import { describe, expect, test } from "vitest";

import { buildReadOnlyBlockedMessage, resolveReadOnlyFromSearch } from "./read_only";

describe("resolveReadOnlyFromSearch", () => {
  test("returns false when no readonly flags are provided", () => {
    expect(resolveReadOnlyFromSearch("")).toBe(false);
    expect(resolveReadOnlyFromSearch("?doc=sample")).toBe(false);
  });

  test("returns true for truthy readonly query flags", () => {
    expect(resolveReadOnlyFromSearch("?readonly=true")).toBe(true);
    expect(resolveReadOnlyFromSearch("?readonly=1")).toBe(true);
    expect(resolveReadOnlyFromSearch("?readOnly=YES")).toBe(true);
    expect(resolveReadOnlyFromSearch("?isReadOnly=on")).toBe(true);
  });

  test("returns true for mode=readonly flag", () => {
    expect(resolveReadOnlyFromSearch("?mode=readonly")).toBe(true);
    expect(resolveReadOnlyFromSearch("?mode=read-only")).toBe(true);
  });

  test("keeps non-truthy values disabled", () => {
    expect(resolveReadOnlyFromSearch("?readonly=false")).toBe(false);
    expect(resolveReadOnlyFromSearch("?readOnly=0")).toBe(false);
    expect(resolveReadOnlyFromSearch("?isReadOnly=no")).toBe(false);
  });
});

describe("buildReadOnlyBlockedMessage", () => {
  test("builds generic message when no action label is supplied", () => {
    expect(buildReadOnlyBlockedMessage()).toBe("Read-only mode: editing is disabled.");
  });

  test("builds action specific message", () => {
    expect(buildReadOnlyBlockedMessage("card update")).toBe("Read-only mode: card update is disabled.");
  });
});
