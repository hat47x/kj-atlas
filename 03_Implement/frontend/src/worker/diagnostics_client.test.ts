import { afterEach, describe, expect, it, vi } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { DiagnosticsWorkerClient } from "./diagnostics_client";

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
});

function fixtureDoc(): DocumentV2 {
  return {
    version: 2,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "SECRET", x: 0, y: 0, claimType: "claim" }],
    edges: [],
    islands: [{ id: "i1", title: "I", cardIds: ["c1"] }],
    relationSummaries: [],
    evidenceLinks: [],
    readingOrder: ["c1"],
  };
}

describe("DiagnosticsWorkerClient", () => {
  it("falls back when worker init fails", async () => {
    globalThis.Worker = class { constructor() { throw new Error("worker unavailable"); } } as unknown as typeof Worker;
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();
    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    if (result.status === "completed") {
      expect(result.result.diagnosticsMd).not.toContain("SECRET");
    }
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("returns cancelled on abort", async () => {
    class FakeWorker {
      addEventListener() {}
      removeEventListener() {}
      postMessage() {}
      terminate() {}
    }
    globalThis.Worker = FakeWorker as unknown as typeof Worker;
    const client = new DiagnosticsWorkerClient();
    const controller = new AbortController();
    const pending = client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } }, { signal: controller.signal });
    controller.abort();
    const result = await pending;
    expect(result.status).toBe("cancelled");
  });
});
