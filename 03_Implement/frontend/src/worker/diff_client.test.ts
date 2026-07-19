import { afterEach, describe, expect, it, vi } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { DiffWorkerClient } from "./diff_client";

function doc(overrides: Partial<DocumentV1>): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2025-01-01T00:00:00.000Z",
    updatedAt: "2025-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    relationSummaries: [],
    evidenceLinks: [],
    ...overrides,
  };
}

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
});

describe("DiffWorkerClient", () => {
  it("returns progress in expected order and resolves result", async () => {
    class FakeWorker {
      private readonly listeners = new Set<(event: MessageEvent) => void>();
      addEventListener(type: string, listener: (event: MessageEvent) => void) { if (type === "message") this.listeners.add(listener); }
      removeEventListener(type: string, listener: (event: MessageEvent) => void) { if (type === "message") this.listeners.delete(listener); }
      postMessage(message: { type: string; requestId: string }) {
        if (message.type !== "diff.request") return;
        const stages = ["cards", "islands", "edges", "evidence", "view"];
        for (const [index, stage] of stages.entries()) {
          for (const listener of this.listeners) {
            listener({ data: { type: "diff.progress", requestId: message.requestId, stage, percent: (index + 1) * 20, protocolVersion: 1 } } as MessageEvent);
          }
        }
        for (const listener of this.listeners) {
          listener({ data: { type: "diff.result", requestId: message.requestId, result: { documentDiff: [], viewDiff: [] }, protocolVersion: 1 } } as MessageEvent);
        }
      }
      terminate() {}
    }

    globalThis.Worker = FakeWorker as unknown as typeof Worker;

    const client = new DiffWorkerClient();
    const observed: string[] = [];
    const result = await client.computeDiff({ baseDoc: doc({}), baseView: {}, incomingDoc: doc({}), incomingView: {} }, { onProgress: (progress) => observed.push(progress.stage) });

    expect(observed).toEqual(["cards", "islands", "edges", "evidence", "view"]);
    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(false);
  });

  it("falls back when worker protocol version is unsupported", async () => {
    class FakeWorker {
      private readonly listeners = new Set<(event: MessageEvent) => void>();
      addEventListener(type: string, listener: (event: MessageEvent) => void) { if (type === "message") this.listeners.add(listener); }
      removeEventListener(type: string, listener: (event: MessageEvent) => void) { if (type === "message") this.listeners.delete(listener); }
      postMessage(message: { type: string; requestId: string }) {
        if (message.type !== "diff.request") return;
        for (const listener of this.listeners) {
          listener({ data: { type: "diff.result", requestId: message.requestId, protocolVersion: 999, result: { documentDiff: [], viewDiff: [] } } } as MessageEvent);
        }
      }
      terminate() {}
    }

    globalThis.Worker = FakeWorker as unknown as typeof Worker;

    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiffWorkerClient();
    const result = await client.computeDiff({ baseDoc: doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] }), baseView: {}, incomingDoc: doc({ cards: [{ id: "c1", text: "A+", x: 0, y: 0 }] }), incomingView: {} });

    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("falls back when worker construction fails", async () => {
    globalThis.Worker = class {
      constructor() {
        throw new Error("worker unavailable");
      }
    } as unknown as typeof Worker;

    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new DiffWorkerClient();
    const result = await client.computeDiff({ baseDoc: doc({ cards: [{ id: "c1", text: "A", x: 0, y: 0 }] }), baseView: {}, incomingDoc: doc({ cards: [{ id: "c1", text: "A+", x: 0, y: 0 }] }), incomingView: {} });

    expect(result.status).toBe("completed");
    if (result.status === "completed") {
      expect(result.result.documentDiff.length).toBeGreaterThan(0);
    }
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });

  it("cancels worker request and resolves cancelled without applying result", async () => {
    class FakeWorker {
      private readonly listeners = new Set<(event: MessageEvent) => void>();
      private cancelled = false;

      addEventListener(_: string, listener: (event: MessageEvent) => void) {
        this.listeners.add(listener);
      }

      removeEventListener(_: string, listener: (event: MessageEvent) => void) {
        this.listeners.delete(listener);
      }

      postMessage(message: { type: string; requestId: string }) {
        if (message.type === "diff.cancel") {
          this.cancelled = true;
          return;
        }

        if (message.type !== "diff.request") {
          return;
        }

        queueMicrotask(() => {
          if (this.cancelled) {
            return;
          }
          for (const listener of this.listeners) {
            listener({
              data: {
                type: "diff.result",
                requestId: message.requestId,
                protocolVersion: 1,
                result: {
                  documentDiff: [
                    {
                      id: "card.add:c1",
                      kind: "card.add",
                      entityRef: { kind: "card", id: "c1" },
                      prerequisites: [],
                    },
                  ],
                  viewDiff: [],
                },
              },
            } as MessageEvent);
          }
        });
      }

      terminate() {}
    }

    globalThis.Worker = FakeWorker as unknown as typeof Worker;

    const controller = new AbortController();
    const client = new DiffWorkerClient();
    const promise = client.computeDiff({ baseDoc: doc({}), baseView: {}, incomingDoc: doc({}), incomingView: {} }, { signal: controller.signal });
    controller.abort();
    const result = await promise;

    expect(result.status).toBe("cancelled");
    expect(result.usedFallback).toBe(false);
  });
});
