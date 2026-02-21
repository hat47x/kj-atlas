/// <reference lib="webworker" />

import { computeTrace } from "./trace_compute";
import type { TraceWorkerRequestMessage, TraceWorkerResponseMessage } from "./trace_protocol";

const cancelledRequestIds = new Set<string>();
const activeRequestIds = new Set<string>();

function postMessageSafe(message: TraceWorkerResponseMessage): void {
  self.postMessage(message);
}

function shouldCancel(requestId: string): boolean {
  return cancelledRequestIds.has(requestId);
}

self.onmessage = (event: MessageEvent<TraceWorkerRequestMessage>) => {
  const message = event.data;
  if (message.type === "trace.cancel") {
    if (activeRequestIds.has(message.requestId)) {
      cancelledRequestIds.add(message.requestId);
    }
    return;
  }

  const { requestId, payload } = message;
  activeRequestIds.add(requestId);
  cancelledRequestIds.delete(requestId);

  try {
    const stages = [
      { stage: "collect" as const, percent: 25 },
      { stage: "traverse" as const, percent: 70 },
      { stage: "render" as const, percent: 100 },
    ];

    for (const stage of stages.slice(0, 2)) {
      if (shouldCancel(requestId)) {
        postMessageSafe({ type: "trace.cancelled", requestId });
        return;
      }
      postMessageSafe({ type: "trace.progress", requestId, stage: stage.stage, percent: stage.percent });
    }

    const result = computeTrace({ ...payload, options: { ...payload.options, safeMode: payload.options.safeMode ?? true } });
    if (shouldCancel(requestId)) {
      postMessageSafe({ type: "trace.cancelled", requestId });
      return;
    }
    postMessageSafe({ type: "trace.progress", requestId, stage: "render", percent: 100 });
    postMessageSafe({ type: "trace.result", requestId, result });
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Unknown trace worker error";
    postMessageSafe({ type: "trace.error", requestId, error: { code: "TRACE_WORKER_ERROR", message: messageText } });
  } finally {
    activeRequestIds.delete(requestId);
    cancelledRequestIds.delete(requestId);
  }
};

export {};
