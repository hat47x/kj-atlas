import { afterEach, describe, expect, it, vi } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { TraceWorkerClient } from "./trace_client";

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
});

const doc: DocumentV2 = {
  version: 2,
  id: "doc",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [{ id: "c1", text: "SECRET", x: 0, y: 0 }, { id: "c2", text: "SECRET2", x: 1, y: 0 }],
  islands: [],
  edges: [],
  relationSummaries: [],
  evidenceLinks: [{ id: "e1", fromCardId: "c1", toCardId: "c2", type: "supports" }],
  readingOrder: [],
};

describe("TraceWorkerClient", () => {
  it("falls back when worker init fails", async () => {
    globalThis.Worker = class { constructor() { throw new Error("worker unavailable"); } } as unknown as typeof Worker;
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const client = new TraceWorkerClient();
    const result = await client.computeTrace({ doc, options: { kind: "evidence", startCardId: "c1" } });
    expect(result.status).toBe("completed");
    if (result.status === "completed") {
      expect(result.result.traceMd).not.toContain("SECRET");
    }
    expect(result.usedFallback).toBe(true);
    expect(warn).toHaveBeenCalled();
  });
});
