import { afterEach, describe, expect, it, vi } from "vitest";
import { computeQueryCanonicalHash, emitContextAuditEvent, logAuditEntry } from "./audit_log.js";

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

describe("emitContextAuditEvent", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("POSTs a CE-4 context-audit event with channel=mcp and the query/bundle hashes", async () => {
    const fetchSpy = vi.fn().mockResolvedValue({ ok: true, status: 200 });
    vi.stubGlobal("fetch", fetchSpy);

    await emitContextAuditEvent(
      { baseUrl: "http://127.0.0.1:8000", apiKey: "biz-key" },
      { docId: "doc1", safeMode: true, queryCanonicalHash: "a".repeat(64), bundleHash: "b".repeat(64) },
    );

    expect(fetchSpy).toHaveBeenCalledTimes(1);
    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("http://127.0.0.1:8000/docs/doc1/context-audit");
    expect(init.method).toBe("POST");
    expect((init.headers as Record<string, string>)["X-API-Key"]).toBe("biz-key");
    const body = JSON.parse(init.body as string);
    expect(body).toMatchObject({
      operation: "query",
      safeMode: true,
      equivalenceKey: "a".repeat(64),
      bundleHash: "b".repeat(64),
      queryHash: "a".repeat(64),
      dryRun: true,
      sideEffect: "none",
      command: "context-query",
      channel: "mcp",
      schemaVersion: "ce4.audit.v1",
    });
  });

  it("does not throw on a non-2xx backend response (best-effort; writes a warning to stderr)", async () => {
    const stderrSpy = vi.spyOn(process.stderr, "write").mockImplementation(() => true);
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, status: 422 }));

    await expect(
      emitContextAuditEvent(
        { baseUrl: "http://127.0.0.1:8000" },
        { docId: "doc1", safeMode: true, queryCanonicalHash: "a".repeat(64), bundleHash: "b".repeat(64) },
      ),
    ).resolves.toBeUndefined();

    const written = stderrSpy.mock.calls[0][0] as string;
    expect(JSON.parse(written).message).toContain("CE-4 audit emit failed");
  });

  it("does not throw when fetch itself rejects (best-effort on network error)", async () => {
    const stderrSpy = vi.spyOn(process.stderr, "write").mockImplementation(() => true);
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("connection refused")));

    await expect(
      emitContextAuditEvent(
        { baseUrl: "http://127.0.0.1:8000" },
        { docId: "doc1", safeMode: true, queryCanonicalHash: "a".repeat(64), bundleHash: "b".repeat(64) },
      ),
    ).resolves.toBeUndefined();

    const written = stderrSpy.mock.calls[0][0] as string;
    expect(JSON.parse(written).message).toContain("CE-4 audit emit error");
  });
});
