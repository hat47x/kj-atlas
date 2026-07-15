import type { DocumentV1 } from "../domain/types";
import type { ReadingMode } from "../domain/view/reading_path";
import type { ContradictionReport } from "../domain/view/contradiction_checks";
import type { DialecticBalanceReport } from "../domain/view/dialectic_balance";
import type { DistributionReport } from "../domain/view/distribution_checks";
import type { OutlineQualityReport } from "../domain/view/outline_quality";
import type { Recommendation } from "../domain/view/recommendations";
import type { DiagramStructuralMetrics } from "../domain/view/structural_metrics";

export const DIAGNOSTICS_DATA_SCHEMA_VERSION = 1 as const;
export type DiagnosticsDataSchemaVersion = typeof DIAGNOSTICS_DATA_SCHEMA_VERSION;

export type DiagnosticsRequestPayload = {
  doc: DocumentV1;
  view: {
    readingMode: ReadingMode;
    reviewedOnly: boolean;
    collapsedIslandIds?: string[];
  };
  options?: {
    safeMode?: boolean;
    deterministicNowIso?: string;
  };
};

export type DiagnosticsData = {
  schemaVersion: DiagnosticsDataSchemaVersion;
  outlineReport: OutlineQualityReport;
  recommendations: Recommendation[];
  contradictionReport: ContradictionReport;
  distributionReport: DistributionReport;
  dialecticBalanceReport: DialecticBalanceReport;
  structuralMetrics: DiagramStructuralMetrics;
};

export const REQUIRED_DIAGNOSTICS_OBJECT_FIELDS = [
  "outlineReport",
  "contradictionReport",
  "distributionReport",
  "dialecticBalanceReport",
  "structuralMetrics",
] as const;

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

function assertDiagnosticsShape(data: Record<string, unknown>): void {
  for (const field of REQUIRED_DIAGNOSTICS_OBJECT_FIELDS) {
    if (!isObjectRecord(data[field])) {
      throw new Error(`Invalid diagnostics payload: missing ${field}`);
    }
  }

  if (!Array.isArray(data.recommendations)) {
    throw new Error("Invalid diagnostics payload: missing recommendations");
  }
}

export function normalizeDiagnosticsData(data: unknown): DiagnosticsData {
  if (!isObjectRecord(data)) {
    throw new Error("Invalid diagnostics payload: expected object");
  }

  assertDiagnosticsShape(data);

  const schemaVersion = data.schemaVersion;
  if (typeof schemaVersion !== "number" || !Number.isInteger(schemaVersion) || schemaVersion <= 0) {
    throw new Error(`Invalid diagnostics schema version: ${String(schemaVersion)}`);
  }

  if (schemaVersion !== DIAGNOSTICS_DATA_SCHEMA_VERSION) {
    throw new Error(`Unsupported diagnostics schema version: ${String(schemaVersion)}`);
  }

  return data as DiagnosticsData;
}

export type DiagnosticsWorkerRequestMessage =
  | { type: "diagnostics.request"; requestId: string; payload: DiagnosticsRequestPayload }
  | { type: "diagnostics.cancel"; requestId: string };

export type DiagnosticsProgressStage = "outline" | "recommendations" | "contradictions" | "distribution" | "dialectic" | "render";

export type DiagnosticsWorkerResponseMessage =
  | { type: "diagnostics.progress"; requestId: string; stage: DiagnosticsProgressStage; percent: number }
  | { type: "diagnostics.result"; requestId: string; result: { diagnosticsMd: string; diagnosticsData: DiagnosticsData } }
  | { type: "diagnostics.error"; requestId: string; error: { code: string; message: string; details?: unknown } }
  | { type: "diagnostics.cancelled"; requestId: string };
