import type { DocumentV1 } from "../domain/types";
import type { TraceAnalyticsOptions, TraceAnalytics } from "./trace_analytics";

export type TraceRequestPayload = {
  doc: DocumentV1;
  options: {
    kind: "evidence" | "contradiction";
    startCardId: string;
    maxHops?: number;
    maxNodes?: number;
    safeMode?: boolean;
    includeRationale?: boolean;
  };
};

export type TraceAnalyticsRequestPayload = {
  doc: DocumentV1;
  options: TraceAnalyticsOptions & {
    startCardId: string;
  };
};

export type TraceData = {
  visitedCardIds: string[];
  visitedRelationIds?: string[];
  truncated: boolean;
  notes: string[];
};

export type TraceWorkerRequestMessage =
  | { type: "trace.request"; requestId: string; payload: TraceRequestPayload }
  | { type: "trace.analytics.request"; requestId: string; payload: TraceAnalyticsRequestPayload }
  | { type: "trace.cancel"; requestId: string };

export type TraceWorkerResponseMessage =
  | { type: "trace.progress"; requestId: string; stage: "collect" | "traverse" | "render"; percent: number }
  | { type: "trace.result"; requestId: string; result: { traceMd: string; traceData: TraceData } }
  | { type: "trace.analytics.result"; requestId: string; result: { analyticsMd: string; analytics: TraceAnalytics } }
  | { type: "trace.error"; requestId: string; error: { code: string; message: string; details?: unknown } }
  | { type: "trace.cancelled"; requestId: string };
