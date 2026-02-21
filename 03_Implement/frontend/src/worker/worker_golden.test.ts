import fs from "node:fs";
import path from "node:path";
import { describe, expect, it } from "vitest";
import type { DocumentV2 } from "../domain/types";
import { computeDiagnostics } from "./diagnostics_compute";
import { computeTrace } from "./trace_compute";

const fixturesDir = path.resolve(__dirname, "../../tests/fixtures/worker");
const fixtureDoc = JSON.parse(fs.readFileSync(path.join(fixturesDir, "doc.small.json"), "utf8")) as DocumentV2;

describe("worker compute goldens", () => {
  it("evidence trace matches golden fixture", () => {
    const expected = fs.readFileSync(path.join(fixturesDir, "evidence_trace_c1.md"), "utf8");
    const output = computeTrace({ doc: fixtureDoc, options: { kind: "evidence", startCardId: "c1", safeMode: true } });
    expect(output.traceMd).toBe(expected);
  });

  it("contradiction trace matches golden fixture", () => {
    const expected = fs.readFileSync(path.join(fixturesDir, "contradiction_trace_c1.md"), "utf8");
    const output = computeTrace({ doc: fixtureDoc, options: { kind: "contradiction", startCardId: "c1", safeMode: true } });
    expect(output.traceMd).toBe(expected);
  });

  it("diagnostics output matches golden fixture and is deterministic", () => {
    const expected = fs.readFileSync(path.join(fixturesDir, "diagnostics.md"), "utf8");
    const run1 = computeDiagnostics({ doc: fixtureDoc, view: { readingMode: "islands+cards", reviewedOnly: false } });
    const run2 = computeDiagnostics({ doc: fixtureDoc, view: { readingMode: "islands+cards", reviewedOnly: false } });
    expect(run1.diagnosticsMd).toBe(expected);
    expect(run1.diagnosticsMd).toBe(run2.diagnosticsMd);
    expect(run1.diagnosticsMd).not.toContain("SECRET");
  });
});
