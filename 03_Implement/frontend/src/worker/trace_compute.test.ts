import { describe, expect, test } from "vitest";
import type { DocumentV1 } from "../domain/types";
import type { TraceRequestPayload } from "./trace_protocol";
import { computeTrace } from "./trace_compute";

function doc(overrides: Partial<DocumentV1> = {}): DocumentV1 {
  return {
    version: 1,
    id: "doc-1",
    createdAt: "2026-01-01T00:00:00.000Z",
    updatedAt: "2026-01-01T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "a", text: "A", x: 0, y: 0 },
      { id: "b", text: "B", x: 10, y: 0 },
      { id: "c", text: "C", x: 20, y: 0 },
      { id: "d", text: "D", x: 30, y: 0 },
    ],
    edges: [],
    islands: [],
    evidenceLinks: [
      { id: "e1", fromCardId: "a", toCardId: "b", type: "supports" },
      { id: "e2", fromCardId: "b", toCardId: "c", type: "supports" },
      { id: "e3", fromCardId: "c", toCardId: "d", type: "contradicts" },
    ],
    ...overrides,
  };
}

function payload(overrides: Partial<TraceRequestPayload> = {}): TraceRequestPayload {
  return {
    doc: doc(),
    options: { kind: "evidence", startCardId: "a" },
    ...overrides,
  };
}

describe("computeTrace", () => {
  test("returns an error result when the start card does not exist", () => {
    const result = computeTrace(payload({ options: { kind: "evidence", startCardId: "missing" } }));
    expect(result.traceMd).toContain("start card not found");
    expect(result.traceData.visitedCardIds).toEqual([]);
  });

  test("traverses evidence supports links from the start card", () => {
    const result = computeTrace(payload());
    expect(result.traceData.visitedCardIds).toContain("a");
    expect(result.traceData.visitedCardIds).toContain("b");
    expect(result.traceData.visitedCardIds).toContain("c");
    // contradicts link (c->d) is filtered out for kind=evidence
    expect(result.traceData.visitedCardIds).not.toContain("d");
  });

  test("filters by contradiction kind", () => {
    const result = computeTrace(payload({ options: { kind: "contradiction", startCardId: "a" } }));
    expect(result.traceData.visitedCardIds).toContain("a");
    expect(result.traceData.visitedCardIds).not.toContain("b"); // e1 is supports
  });

  test("respects maxHops", () => {
    const result = computeTrace(payload({ options: { kind: "evidence", startCardId: "a", maxHops: 1 } }));
    expect(result.traceData.visitedCardIds).toContain("b");
    expect(result.traceData.visitedCardIds).not.toContain("c");
  });

  test("respects maxNodes and reports truncation", () => {
    const result = computeTrace(payload({ options: { kind: "evidence", startCardId: "a", maxNodes: 2 } }));
    expect(result.traceData.visitedCardIds.length).toBeLessThanOrEqual(2);
    expect(result.traceData.truncated).toBe(true);
    expect(result.traceData.notes).toContain("Truncated to 2 nodes.");
  });

  test("adds a safe-mode note when safeMode is on", () => {
    const result = computeTrace(payload({ options: { kind: "evidence", startCardId: "a", safeMode: true } }));
    expect(result.traceData.notes).toContain("Safe mode enforced: no raw card text included.");
  });

  test("does not add a safe-mode note when safeMode is off", () => {
    const result = computeTrace(payload({ options: { kind: "evidence", startCardId: "a", safeMode: false } }));
    expect(result.traceData.notes).not.toContain("Safe mode enforced: no raw card text included.");
  });

  test("renders markdown with visited cards and relations", () => {
    const result = computeTrace(payload());
    expect(result.traceMd).toContain("# Evidence Trace");
    expect(result.traceMd).toContain("card:a");
    expect(result.traceMd).toContain("relation:e1");
  });

  test("handles an empty document", () => {
    const result = computeTrace(payload({ doc: doc({ cards: [], evidenceLinks: [] }) }));
    expect(result.traceData.visitedCardIds).toEqual([]);
    expect(result.traceMd).toContain("start card not found");
  });
});
