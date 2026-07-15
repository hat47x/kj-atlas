import { afterEach, describe, expect, it, vi } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { DIAGNOSTICS_DATA_SCHEMA_VERSION } from "./diagnostics_protocol";
import { computeDiagnostics } from "./diagnostics_compute";
import { DiagnosticsWorkerClient } from "./diagnostics_client";

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
  vi.restoreAllMocks();
});

function fixtureDoc(): DocumentV1 {
  return {
    version: 1,
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

function installFakeWorkerWithDiagnostics(diagnosticsData: unknown, diagnosticsMd = "# Diagnostics\n") {
  installFakeWorkerWithResultEnvelope({ diagnosticsMd, diagnosticsData });
}

function installFakeWorkerWithResultEnvelope(result: unknown) {
  installFakeWorkerWithRawMessageFactory((requestId) => ({
    requestId,
    type: "diagnostics.result",
    result,
  }));
}

function installFakeWorkerWithRawMessageFactory(factory: (requestId: string) => unknown) {
  class FakeWorker {
    private listeners = new Set<(event: MessageEvent) => void>();

    addEventListener(_type: string, listener: (event: MessageEvent) => void) {
      this.listeners.add(listener);
    }

    removeEventListener(_type: string, listener: (event: MessageEvent) => void) {
      this.listeners.delete(listener);
    }

    postMessage(message: { type: string; requestId: string }) {
      if (message.type !== "diagnostics.request") return;
      queueMicrotask(() => {
        const response = factory(message.requestId);
        const responseList = Array.isArray(response) ? response : [response];
        for (const item of responseList) {
          for (const listener of this.listeners) {
            listener({ data: item } as MessageEvent);
          }
        }
      });
    }

    terminate() {}
  }

  globalThis.Worker = FakeWorker as unknown as typeof Worker;
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
      expect(result.result.diagnosticsData.schemaVersion).toBe(DIAGNOSTICS_DATA_SCHEMA_VERSION);
    }
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns diagnostics data without schemaVersion", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    const { schemaVersion: _, ...withoutSchemaVersion } = diagnostics.diagnosticsData;
    installFakeWorkerWithDiagnostics(withoutSchemaVersion, diagnostics.diagnosticsMd);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});

    const client = new DiagnosticsWorkerClient();
    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });

    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
    if (result.status === "completed") {
      expect(result.result.diagnosticsData.schemaVersion).toBe(DIAGNOSTICS_DATA_SCHEMA_VERSION);
    }
  });

  it("falls back when worker returns unsupported/invalid diagnostics schema", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });

    for (const schemaVersion of [999, 0]) {
      installFakeWorkerWithDiagnostics({ ...diagnostics.diagnosticsData, schemaVersion }, diagnostics.diagnosticsMd);
      const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
      const client = new DiagnosticsWorkerClient();

      const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
      expect(result.status).toBe("completed");
      expect(result.usedFallback).toBe(true);
      expect(warn).toHaveBeenCalled();
      if (result.status === "completed") {
        expect(result.result.diagnosticsData.schemaVersion).toBe(DIAGNOSTICS_DATA_SCHEMA_VERSION);
      }
      warn.mockRestore();
    }
  });

  it("falls back when worker returns non-object diagnostics payload", async () => {
    installFakeWorkerWithDiagnostics(null);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns array-shaped diagnostics payload", async () => {
    installFakeWorkerWithDiagnostics([]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns diagnostics payload missing required fields", async () => {
    installFakeWorkerWithDiagnostics({ schemaVersion: 1, recommendations: [] });
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns diagnostics payload with non-array recommendations", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithDiagnostics({ ...diagnostics.diagnosticsData, recommendations: {} });
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns non-string diagnosticsMd", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithDiagnostics(diagnostics.diagnosticsData, 42 as unknown as string);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns non-object result envelope", async () => {
    installFakeWorkerWithResultEnvelope(null);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker returns array-shaped result envelope", async () => {
    installFakeWorkerWithResultEnvelope([]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });


  it("ignores non-object worker messages and keeps processing", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithRawMessageFactory((requestId) => [
      null,
      { requestId, type: "diagnostics.result", result: { diagnosticsMd: diagnostics.diagnosticsMd, diagnosticsData: diagnostics.diagnosticsData } },
    ]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(false);
    expect(warn).not.toHaveBeenCalled();
  });

  it("ignores worker messages with invalid requestId and keeps processing", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithRawMessageFactory((requestId) => [
      { requestId: 42, type: "diagnostics.result", result: { diagnosticsMd: "# Diagnostics\n", diagnosticsData: {} } },
      { requestId, type: "diagnostics.result", result: { diagnosticsMd: diagnostics.diagnosticsMd, diagnosticsData: diagnostics.diagnosticsData } },
    ]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(false);
    expect(warn).not.toHaveBeenCalled();
  });

  it("ignores malformed messages for other requestIds", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithRawMessageFactory((requestId) => [
      { requestId: "other-request", type: 123, result: null },
      { requestId, type: "diagnostics.result", result: { diagnosticsMd: diagnostics.diagnosticsMd, diagnosticsData: diagnostics.diagnosticsData } },
    ]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(false);
    expect(warn).not.toHaveBeenCalled();
  });

  it("falls back when matched progress message is malformed", async () => {
    const diagnostics = computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    installFakeWorkerWithRawMessageFactory((requestId) => [
      { requestId, type: "diagnostics.progress", stage: "outline", percent: 999 },
      { requestId, type: "diagnostics.result", result: { diagnosticsMd: diagnostics.diagnosticsMd, diagnosticsData: diagnostics.diagnosticsData } },
    ]);
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when matched message type is unknown", async () => {
    installFakeWorkerWithRawMessageFactory((requestId) => ({ requestId, type: "diagnostics.unknown" }));
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when diagnostics.error message is malformed", async () => {
    installFakeWorkerWithRawMessageFactory((requestId) => ({
      requestId,
      type: "diagnostics.error",
      error: { code: "X", message: 42 },
    }));
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiagnosticsWorkerClient();

    const result = await client.computeDiagnostics({ doc: fixtureDoc(), view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(result.status).toBe("completed");
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
