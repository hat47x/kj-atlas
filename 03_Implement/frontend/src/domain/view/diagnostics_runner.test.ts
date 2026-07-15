import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../types";
import { runDiagnosticsIncremental } from "./diagnostics_runner";
import { createCancelableTaskRunner } from "../../utils/compute_scheduler";

const doc: DocumentV1 = {
  version: 1,
  id: "d",
  title: "t",
  createdAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: Array.from({ length: 200 }, (_, i) => ({ id: `c${i}`, text: `card ${i}`, x: 0, y: 0 })),
  islands: [{ id: "i1", title: "is", cardIds: [] }],
  edges: [],
  updatedAt: "2026-01-01T00:00:00.000Z",
};

describe("runDiagnosticsIncremental", () => {
  it("yields and returns diagnostics", async () => {
    const runner = createCancelableTaskRunner();
    const outcome = await runner.run((ctx) => runDiagnosticsIncremental(doc, { readingMode: "islands", reviewedOnly: false, collapsedIslandIds: new Set() }, ctx));
    expect(outcome.status).toBe("completed");
    if (outcome.status === "completed") {
      expect(outcome.result.report.stats.totalIslands).toBeGreaterThan(0);
    }
  });

  it("sets truncated flag on guardrails", async () => {
    const runner = createCancelableTaskRunner();
    const outcome = await runner.run((ctx) => runDiagnosticsIncremental(doc, { readingMode: "islands", reviewedOnly: false, collapsedIslandIds: new Set() }, ctx, { maxNodes: 10, maxMs: 1 }));
    expect(outcome.status).toBe("completed");
    if (outcome.status === "completed") {
      expect(outcome.result.truncated).toBe(true);
      expect(outcome.result.notes.join(" ")).toContain("Truncated");
    }
  });
});
