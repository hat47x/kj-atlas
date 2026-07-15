import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { DocumentV1 } from "../domain/types";
import { computeDiagnostics } from "./diagnostics_compute";
import { computeTrace } from "./trace_compute";
import { buildTraceAnalyticsMd, computeTraceAnalytics } from "./trace_analytics";

const fixturesDir = path.resolve(__dirname, "../../tests/fixtures/worker");
const fixtureDoc = JSON.parse(fs.readFileSync(path.join(fixturesDir, "doc.small.json"), "utf8")) as DocumentV1;
const readGolden = (filename: string): string => fs.readFileSync(path.join(fixturesDir, filename), "utf8").replace(/\r\n/g, "\n");

describe("worker compute goldens", () => {
  it("evidence trace matches golden fixture", () => {
    const expected = readGolden("evidence_trace_c1.md");
    const output = computeTrace({ doc: fixtureDoc, options: { kind: "evidence", startCardId: "c1", safeMode: true } });
    expect(output.traceMd).toBe(expected);
  });

  it("contradiction trace matches golden fixture", () => {
    const expected = readGolden("contradiction_trace_c1.md");
    const output = computeTrace({ doc: fixtureDoc, options: { kind: "contradiction", startCardId: "c1", safeMode: true } });
    expect(output.traceMd).toBe(expected);
  });


  it("trace analytics output matches golden fixture", () => {
    const expected = readGolden("trace_analytics_c1.md");
    const output = buildTraceAnalyticsMd(computeTraceAnalytics(fixtureDoc, "c1", { safeMode: true }));
    expect(output).toBe(expected);
  });

  it("diagnostics output matches golden fixture and is deterministic", () => {
    const expected = readGolden("diagnostics.md");
    const run1 = computeDiagnostics({ doc: fixtureDoc, view: { readingMode: "islands+cards", reviewedOnly: false } });
    const run2 = computeDiagnostics({ doc: fixtureDoc, view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(run1.diagnosticsMd).toBe(expected);
    expect(run1.diagnosticsMd).toBe(run2.diagnosticsMd);
    expect(run1.diagnosticsMd).not.toContain("SECRET");
  });


  it("diagnostics metrics flag disconnected and bottleneck structures", () => {
    const doc: DocumentV1 = {
      version: 1,
      id: "doc-bridge",
      createdAt: "2026-01-01T00:00:00.000Z",
      updatedAt: "2026-01-01T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "A", x: 0, y: 0 },
        { id: "c2", text: "B", x: 1, y: 0 },
        { id: "c3", text: "C", x: 2, y: 0 },
        { id: "c4", text: "D", x: 3, y: 0 },
      ],
      edges: [
        { id: "r1", fromId: "c1", toId: "c2", type: "related" },
        { id: "r2", fromId: "c2", toId: "c3", type: "related" },
      ],
      islands: [
        { id: "i1", cardIds: ["c1", "c2", "c3"], shape: { kind: "rect" } },
        { id: "i2", cardIds: ["c4"], shape: { kind: "rect" } },
      ],
    };

    const output = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false }, options: { safeMode: true } });
    expect(output.diagnosticsMd).toContain("| connectedComponentCount | 2 |");
    expect(output.diagnosticsMd).toContain("| largestComponentRatio | 0.75 |");
    expect(output.diagnosticsMd).toContain("| connectivityScore | 0.6667 |");
    expect(output.diagnosticsMd).toContain("| averageDegree | 1 |");
    expect(output.diagnosticsMd).toContain("| degreeP95 | 2 |");
    expect(output.diagnosticsMd).toContain("| degreeSkewRatio | 2 |");
    expect(output.diagnosticsMd).toContain("| isolationRate | 0.25 |");
    expect(output.diagnosticsMd).toContain("| bridgeEdgeCount | 2 |");
  });

  it("diagnostics metrics remain safe and omit unavailable optional rows", () => {
    const doc: DocumentV1 = {
      version: 1,
      id: "doc-safe",
      createdAt: "2026-01-01T00:00:00.000Z",
      updatedAt: "2026-01-01T00:00:00.000Z",
      transform: { panX: 0, panY: 0, zoom: 1 },
      cards: [
        { id: "c1", text: "SECRET-A", x: 0, y: 0 },
        { id: "c2", text: "SECRET-B", x: 1, y: 0 },
      ],
      edges: [],
      islands: [{ id: "i1", cardIds: ["c1", "c2"], shape: { kind: "rect" } }],
    };

    const output = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false }, options: { safeMode: true } });
    expect(output.diagnosticsMd).toContain("## Metrics");
    expect(output.diagnosticsMd).toContain("| evidenceLinkCount | 0 |");
    expect(output.diagnosticsMd).toContain("| connectedComponentCount | 2 |");
    expect(output.diagnosticsMd).toContain("| largestComponentRatio | 0.5 |");
    expect(output.diagnosticsMd).toContain("| connectivityScore | 0 |");
    expect(output.diagnosticsMd).toContain("| averageDegree | 0 |");
    expect(output.diagnosticsMd).toContain("| degreeP95 | 0 |");
    expect(output.diagnosticsMd).toContain("| degreeSkewRatio | 0 |");
    expect(output.diagnosticsMd).toContain("| isolationRate | 1 |");
    expect(output.diagnosticsMd).toContain("| bridgeEdgeCount | 0 |");
    expect(output.diagnosticsMd).not.toContain("reviewedCoverage");
    expect(output.diagnosticsMd).not.toContain("contradictionRatio");
    expect(output.diagnosticsMd).not.toContain("SECRET-A");
    expect(output.diagnosticsMd).not.toContain("SECRET-B");
  });
});
