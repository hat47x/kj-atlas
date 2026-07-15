import type { DocumentV1 } from "../domain/types";
import type { MergeItem } from "../diff/merge_items";
import type { DiffViewSnapshot } from "../diff/view_diff";

export type DiffRequestPayload = {
  baseDoc: DocumentV1;
  baseView: DiffViewSnapshot;
  incomingDoc: DocumentV1;
  incomingView: DiffViewSnapshot;
  options?: { maxNodes?: number; maxMs?: number };
};

export type DiffWorkerRequestMessage =
  | { type: "diff.request"; requestId: string; payload: DiffRequestPayload }
  | { type: "diff.cancel"; requestId: string };

export type DiffProgressStage = "cards" | "islands" | "edges" | "evidence" | "view";

export const DIFF_WORKER_PROTOCOL_VERSION = 1 as const;
export type DiffWorkerProtocolVersion = typeof DIFF_WORKER_PROTOCOL_VERSION;

export type DiffWorkerResponseMessage =
  | { type: "diff.progress"; requestId: string; stage: DiffProgressStage; percent: number; protocolVersion: DiffWorkerProtocolVersion }
  | { type: "diff.result"; requestId: string; result: { documentDiff: MergeItem[]; viewDiff: MergeItem[] }; protocolVersion: DiffWorkerProtocolVersion }
  | { type: "diff.error"; requestId: string; error: { code: string; message: string; details?: unknown }; protocolVersion: DiffWorkerProtocolVersion }
  | { type: "diff.cancelled"; requestId: string; protocolVersion: DiffWorkerProtocolVersion };
