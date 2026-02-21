import type { DocumentV2 } from "../domain/types";
import type { ReadingMode } from "../domain/view/reading_path";
import type { ContradictionReport } from "../domain/view/contradiction_checks";
import type { DialecticBalanceReport } from "../domain/view/dialectic_balance";
import type { DistributionReport } from "../domain/view/distribution_checks";
import type { OutlineQualityReport } from "../domain/view/outline_quality";
import type { Recommendation } from "../domain/view/recommendations";

export type DiagnosticsRequestPayload = {
  doc: DocumentV2;
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
  outlineReport: OutlineQualityReport;
  recommendations: Recommendation[];
  contradictionReport: ContradictionReport;
  distributionReport: DistributionReport;
  dialecticBalanceReport: DialecticBalanceReport;
};

export type DiagnosticsWorkerRequestMessage =
  | { type: "diagnostics.request"; requestId: string; payload: DiagnosticsRequestPayload }
  | { type: "diagnostics.cancel"; requestId: string };

export type DiagnosticsProgressStage = "outline" | "recommendations" | "contradictions" | "distribution" | "dialectic" | "render";

export type DiagnosticsWorkerResponseMessage =
  | { type: "diagnostics.progress"; requestId: string; stage: DiagnosticsProgressStage; percent: number }
  | { type: "diagnostics.result"; requestId: string; result: { diagnosticsMd: string; diagnosticsData: DiagnosticsData } }
  | { type: "diagnostics.error"; requestId: string; error: { code: string; message: string; details?: unknown } }
  | { type: "diagnostics.cancelled"; requestId: string };
