import type { DocumentV2 } from "../domain/types";

export type TraceRequestPayload = {
  doc: DocumentV2;
  options: {
    kind: "evidence" | "contradiction";
    startCardId: string;
    maxHops?: number;
    maxNodes?: number;
    safeMode?: boolean;
    includeRationale?: boolean;
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
  | { type: "trace.cancel"; requestId: string };

export type TraceWorkerResponseMessage =
  | { type: "trace.progress"; requestId: string; stage: "collect" | "traverse" | "render"; percent: number }
  | { type: "trace.result"; requestId: string; result: { traceMd: string; traceData: TraceData } }
  | { type: "trace.error"; requestId: string; error: { code: string; message: string; details?: unknown } }
  | { type: "trace.cancelled"; requestId: string };
