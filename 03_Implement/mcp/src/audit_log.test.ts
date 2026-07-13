import { afterEach, describe, expect, it, vi } from "vitest";
import { computeQueryCanonicalHash, logAuditEntry } from "./audit_log.js";

describe("computeQueryCanonicalHash", () => {
  it("is deterministic for identical input", async () => {
    const input = { docId: "doc1", constraint: "reviewed-only" as const, safeMode: true };
    expect(await computeQueryCanonicalHash(input)).toBe(await computeQueryCanonicalHash(input));
  });

  it("changes when any field differs", async () => {
    const base = await computeQueryCanonicalHash({ docId: "doc1", constraint: "reviewed-only", safeMode: true });
    const differentDoc = await computeQueryCanonicalHash({ docId: "doc2", constraint: "reviewed-only", safeMode: true });
    const differentConstraint = await computeQueryCanonicalHash({ docId: "doc1", constraint: "summary", safeMode: true });
    const differentSafeMode = await computeQueryCanonicalHash({ docId: "doc1", constraint: "reviewed-only", safeMode: false });

    expect(differentDoc).not.toBe(base);
    expect(differentConstraint).not.toBe(base);
    expect(differentSafeMode).not.toBe(base);
  });

  it("produces a 64-hex-character sha256 digest", async () => {
    const hash = await computeQueryCanonicalHash({ docId: "doc1", constraint: "reviewed-only", safeMode: true });
    expect(hash).toMatch(/^[0-9a-f]{64}$/);
  });
});

describe("logAuditEntry", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("writes exactly one JSON line to stderr, never stdout (stdout is reserved for the MCP protocol)", () => {
    const stderrSpy = vi.spyOn(process.stderr, "write").mockImplementation(() => true);
    const stdoutSpy = vi.spyOn(process.stdout, "write").mockImplementation(() => true);

    logAuditEntry({
      schemaVersion: "mcp-context-read.v1",
      occurredAt: "2026-07-13T00:00:00.000Z",
      docId: "doc1",
      constraint: "reviewed-only",
      safeMode: true,
      queryCanonicalHash: "a".repeat(64),
      bundleHash: "b".repeat(64),
      outcome: "ok",
    });

    expect(stdoutSpy).not.toHaveBeenCalled();
    expect(stderrSpy).toHaveBeenCalledTimes(1);
    const written = stderrSpy.mock.calls[0][0] as string;
    expect(written.endsWith("\n")).toBe(true);
    const parsed = JSON.parse(written);
    expect(parsed).toEqual({
      schemaVersion: "mcp-context-read.v1",
      occurredAt: "2026-07-13T00:00:00.000Z",
      docId: "doc1",
      constraint: "reviewed-only",
      safeMode: true,
      queryCanonicalHash: "a".repeat(64),
      bundleHash: "b".repeat(64),
      outcome: "ok",
    });
  });

  it("allows bundleHash: null (not_found / error outcomes never hash withheld content)", () => {
    const stderrSpy = vi.spyOn(process.stderr, "write").mockImplementation(() => true);

    logAuditEntry({
      schemaVersion: "mcp-context-read.v1",
      occurredAt: "2026-07-13T00:00:00.000Z",
      docId: "missing-doc",
      constraint: "summary",
      safeMode: true,
      queryCanonicalHash: "a".repeat(64),
      bundleHash: null,
      outcome: "not_found",
    });

    const parsed = JSON.parse(stderrSpy.mock.calls[0][0] as string);
    expect(parsed.bundleHash).toBeNull();
    expect(parsed.outcome).toBe("not_found");
  });
});
