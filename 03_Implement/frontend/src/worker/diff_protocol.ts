import type { DocumentV2 } from "../domain/types";
import type { MergeItem } from "../diff/merge_items";
import type { DiffViewSnapshot } from "../diff/view_diff";

export type DiffRequestPayload = {
  baseDoc: DocumentV2;
  baseView: DiffViewSnapshot;
  incomingDoc: DocumentV2;
  incomingView: DiffViewSnapshot;
  options?: { maxNodes?: number; maxMs?: number };
};

export type DiffWorkerRequestMessage =
  | { type: "diff.request"; requestId: string; payload: DiffRequestPayload }
  | { type: "diff.cancel"; requestId: string };

export type DiffProgressStage = "cards" | "islands" | "edges" | "evidence" | "view";

export type DiffWorkerResponseMessage =
  | { type: "diff.progress"; requestId: string; stage: DiffProgressStage; percent: number }
  | { type: "diff.result"; requestId: string; result: { documentDiff: MergeItem[]; viewDiff: MergeItem[] } }
  | { type: "diff.error"; requestId: string; error: { code: string; message: string; details?: unknown } }
  | { type: "diff.cancelled"; requestId: string };
