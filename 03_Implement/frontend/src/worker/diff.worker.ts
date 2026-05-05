/// <reference lib="webworker" />

import { computeDocumentDiff } from "../diff/document_diff";
import { computeViewDiff } from "../diff/view_diff";
import { DIFF_WORKER_PROTOCOL_VERSION, type DiffWorkerRequestMessage, type DiffWorkerResponseMessage } from "./diff_protocol";

const cancelledRequestIds = new Set<string>();
const activeRequestIds = new Set<string>();

function postMessageSafe(message: DiffWorkerResponseMessage): void {
  self.postMessage(message);
}

function postProgress(requestId: string, stage: "cards" | "islands" | "edges" | "evidence" | "view", percent: number): void {
  postMessageSafe({ type: "diff.progress", requestId, stage, percent, protocolVersion: DIFF_WORKER_PROTOCOL_VERSION });
}

function postResult(requestId: string, result: Extract<DiffWorkerResponseMessage, { type: "diff.result" }>["result"]): void {
  postMessageSafe({ type: "diff.result", requestId, result, protocolVersion: DIFF_WORKER_PROTOCOL_VERSION });
}

function postError(requestId: string, error: Extract<DiffWorkerResponseMessage, { type: "diff.error" }>["error"]): void {
  postMessageSafe({ type: "diff.error", requestId, error, protocolVersion: DIFF_WORKER_PROTOCOL_VERSION });
}

function postCancelled(requestId: string): void {
  postMessageSafe({ type: "diff.cancelled", requestId, protocolVersion: DIFF_WORKER_PROTOCOL_VERSION });
}

function shouldCancel(requestId: string): boolean {
  return cancelledRequestIds.has(requestId);
}

self.onmessage = (event: MessageEvent<DiffWorkerRequestMessage>) => {
  const message = event.data;

  if (message.type === "diff.cancel") {
    if (!activeRequestIds.has(message.requestId)) {
      return;
    }
    cancelledRequestIds.add(message.requestId);
    return;
  }

  const { requestId, payload } = message;
  activeRequestIds.add(requestId);
  cancelledRequestIds.delete(requestId);

  try {
    const diff = computeDocumentDiff(payload.baseDoc, payload.incomingDoc);
    const stages: Array<{ stage: "cards" | "islands" | "edges" | "evidence" | "view"; percent: number }> = [
      { stage: "cards", percent: 20 },
      { stage: "islands", percent: 40 },
      { stage: "edges", percent: 60 },
      { stage: "evidence", percent: 80 },
      { stage: "view", percent: 100 },
    ];

    for (const entry of stages.slice(0, 4)) {
      if (shouldCancel(requestId)) {
        postCancelled(requestId);
        return;
      }
      postProgress(requestId, entry.stage, entry.percent);
    }

    const viewDiff = computeViewDiff(payload.baseView, payload.incomingView);
    if (shouldCancel(requestId)) {
      postCancelled(requestId);
      return;
    }

    postProgress(requestId, "view", 100);
    postResult(requestId, { documentDiff: [...diff.cards, ...diff.islands, ...diff.edges, ...diff.evidence], viewDiff });
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Unknown worker error";
    postError(requestId, { code: "DIFF_WORKER_ERROR", message: messageText });
  } finally {
    activeRequestIds.delete(requestId);
    cancelledRequestIds.delete(requestId);
  }
};

export {};
