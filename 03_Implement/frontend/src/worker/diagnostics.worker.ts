/// <reference lib="webworker" />

import { computeDiagnostics } from "./diagnostics_compute";
import type { DiagnosticsProgressStage, DiagnosticsWorkerRequestMessage, DiagnosticsWorkerResponseMessage } from "./diagnostics_protocol";

const cancelledRequestIds = new Set<string>();
const activeRequestIds = new Set<string>();

function postMessageSafe(message: DiagnosticsWorkerResponseMessage): void {
  self.postMessage(message);
}

function shouldCancel(requestId: string): boolean {
  return cancelledRequestIds.has(requestId);
}

self.onmessage = (event: MessageEvent<DiagnosticsWorkerRequestMessage>) => {
  const message = event.data;
  if (message.type === "diagnostics.cancel") {
    if (activeRequestIds.has(message.requestId)) {
      cancelledRequestIds.add(message.requestId);
    }
    return;
  }

  const { requestId, payload } = message;
  activeRequestIds.add(requestId);
  cancelledRequestIds.delete(requestId);

  try {
    const stages: Array<{ stage: DiagnosticsProgressStage; percent: number }> = [
      { stage: "outline", percent: 10 },
      { stage: "recommendations", percent: 30 },
      { stage: "contradictions", percent: 50 },
      { stage: "distribution", percent: 70 },
      { stage: "dialectic", percent: 85 },
      { stage: "render", percent: 100 },
    ];

    for (const stage of stages.slice(0, stages.length - 1)) {
      if (shouldCancel(requestId)) {
        postMessageSafe({ type: "diagnostics.cancelled", requestId });
        return;
      }
      postMessageSafe({ type: "diagnostics.progress", requestId, stage: stage.stage, percent: stage.percent });
    }

    if (shouldCancel(requestId)) {
      postMessageSafe({ type: "diagnostics.cancelled", requestId });
      return;
    }
    const result = computeDiagnostics({ ...payload, options: { ...payload.options, safeMode: payload.options?.safeMode ?? true } });
    if (shouldCancel(requestId)) {
      postMessageSafe({ type: "diagnostics.cancelled", requestId });
      return;
    }

    postMessageSafe({ type: "diagnostics.progress", requestId, stage: "render", percent: 100 });
    postMessageSafe({ type: "diagnostics.result", requestId, result });
  } catch (error) {
    const messageText = error instanceof Error ? error.message : "Unknown diagnostics worker error";
    postMessageSafe({ type: "diagnostics.error", requestId, error: { code: "DIAGNOSTICS_WORKER_ERROR", message: messageText } });
  } finally {
    activeRequestIds.delete(requestId);
    cancelledRequestIds.delete(requestId);
  }
};

export {};
