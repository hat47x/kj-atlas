import { describe, expect, it } from "vitest";
import {
  DIAGNOSTICS_DATA_SCHEMA_VERSION,
  normalizeDiagnosticsData,
  REQUIRED_DIAGNOSTICS_OBJECT_FIELDS,
} from "./diagnostics_protocol";
import { computeDiagnostics } from "./diagnostics_compute";
import type { DocumentV1 } from "../domain/types";

const doc: DocumentV1 = {
  version: 1,
  id: "doc-1",
  createdAt: "2026-01-01T00:00:00.000Z",
  updatedAt: "2026-01-01T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [{ id: "c1", text: "hello", x: 0, y: 0 }],
  islands: [{ id: "i1", cardIds: ["c1"] }],
  edges: [],
  relationSummaries: [],
  evidenceLinks: [],
};

describe("normalizeDiagnosticsData", () => {
  it("accepts current schema payload", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    const normalized = normalizeDiagnosticsData(computed);
    expect(normalized.schemaVersion).toBe(DIAGNOSTICS_DATA_SCHEMA_VERSION);
    expect(normalized.outlineReport).toEqual(computed.outlineReport);
  });

  it("throws when schemaVersion is missing", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    const { schemaVersion: _, ...withoutVersion } = computed;
    expect(() => normalizeDiagnosticsData(withoutVersion)).toThrow("Invalid diagnostics schema version");
  });

  it("throws for unsupported schemaVersion", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    expect(() => normalizeDiagnosticsData({ ...computed, schemaVersion: 999 })).toThrow("Unsupported diagnostics schema version");
  });

  it("throws for invalid schemaVersion", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    expect(() => normalizeDiagnosticsData({ ...computed, schemaVersion: 1.5 as unknown as number })).toThrow("Invalid diagnostics schema version");
  });

  it("throws when payload is not an object", () => {
    expect(() => normalizeDiagnosticsData(null)).toThrow("Invalid diagnostics payload: expected object");
    expect(() => normalizeDiagnosticsData([])).toThrow("Invalid diagnostics payload: expected object");
  });

  it("throws when required diagnostics object fields are missing", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    for (const field of REQUIRED_DIAGNOSTICS_OBJECT_FIELDS) {
      const candidate = { ...computed } as Record<string, unknown>;
      delete candidate[field];
      expect(() => normalizeDiagnosticsData(candidate)).toThrow(`Invalid diagnostics payload: missing ${field}`);
    }
  });

  it("throws when recommendations is missing or non-array", () => {
    const computed = computeDiagnostics({ doc, view: { readingMode: "islands+cards", reviewedOnly: false } }).diagnosticsData;
    const { recommendations: _, ...rest } = computed;
    expect(() => normalizeDiagnosticsData(rest)).toThrow("Invalid diagnostics payload: missing recommendations");
    expect(() => normalizeDiagnosticsData({ ...computed, recommendations: {} as unknown as [] })).toThrow("Invalid diagnostics payload: missing recommendations");
  });
});
