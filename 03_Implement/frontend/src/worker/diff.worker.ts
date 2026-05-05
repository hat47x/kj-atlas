/// <reference lib="webworker" />

import { computeDocumentDiff } from "../diff/document_diff";
import { computeViewDiff } from "../diff/view_diff";
import { DIFF_WORKER_PROTOCOL_VERSION, type DiffWorkerRequestMessage, type DiffWorkerResponseMessage } from "./diff_protocol";

const cancelledRequestIds = new Set<string>();
const activeRequestIds = new Set<string>();

function postMessageSafe(message: Omit<DiffWorkerResponseMessage, "protocolVersion">): void {
  self.postMessage({ ...message, protocolVersion: DIFF_WORKER_PROTOCOL_VERSION } satisfies DiffWorkerResponseMessage);
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
        postMessageSafe({ type: "diff.cancelled", requestId });
        return;
      }
      postMessageSafe({ type: "diff.progress", requestId, stage: entry.stage, percent: entry.percent });
    }

    const viewDiff = computeViewDiff(payload.baseView, payload.incomingView);
    if (shouldCancel(requestId)) {
      postMessageSafe({ type: "diff.cancelled", requestId });
      return;
    }

    postMessageSafe({ type: "diff.progress", requestId, stage: "view", percent: 100 });
    postMessageSafe({ type: "diff.result", requestId, result: { documentDiff: [...diff.cards, ...diff.islands, ...diff.edges, ...diff.evidence], viewDiff } });
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Unknown worker error";
    postMessageSafe({ type: "diff.error", requestId, error: { code: "DIFF_WORKER_ERROR", message: messageText } });
  } finally {
    activeRequestIds.delete(requestId);
    cancelledRequestIds.delete(requestId);
  }
};

export {};
