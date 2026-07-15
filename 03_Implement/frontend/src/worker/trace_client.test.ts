import { afterEach, describe, expect, it, vi } from "vitest";
import type { DocumentV1, EvidenceLink } from "../domain/types";
import { TraceWorkerClient } from "./trace_client";

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
});

const doc: DocumentV1 = {
  version: 1,
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

  it("computes analytics for ~150 cards via fallback without leaking text", async () => {
    globalThis.Worker = class { constructor() { throw new Error("worker unavailable"); } } as unknown as typeof Worker;
    const warn = vi.spyOn(console, "warn").mockImplementation(() => {});
    const cards = Array.from({ length: 150 }, (_, index) => ({ id: `c${index + 1}`, text: `SECRET_TEXT_DO_NOT_LEAK_${index + 1}`, x: index, y: 0 }));
    const evidenceLinks: EvidenceLink[] = Array.from({ length: 149 }, (_, index) => ({
      id: `e${index + 1}`,
      fromCardId: `c${index + 1}`,
      toCardId: `c${index + 2}`,
      type: index % 2 === 0 ? "supports" : "contradicts",
    }));
    const largeDoc: DocumentV1 = { ...doc, cards, evidenceLinks };

    const client = new TraceWorkerClient();
    const result = await client.computeTraceAnalytics({ doc: largeDoc, options: { startCardId: "c1", kind: "both", maxHops: 4, maxNodes: 80, safeMode: true } });

    expect(result.status).toBe("completed");
    expect(result.usedFallback).toBe(true);
    if (result.status === "completed") {
      expect(result.result.analytics.visitedCardIds.length).toBeLessThanOrEqual(80);
      expect(result.result.analyticsMd).not.toContain("SECRET_TEXT_DO_NOT_LEAK");
    }
    expect(warn).toHaveBeenCalled();
    client.dispose();
  });
});
