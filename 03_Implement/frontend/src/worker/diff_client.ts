import { buildMergeItemsIncremental, type MergeItem } from "../diff/merge_items";
import { createCancelableTaskRunner } from "../utils/compute_scheduler";
import { DIFF_WORKER_PROTOCOL_VERSION, type DiffProgressStage, type DiffRequestPayload, type DiffWorkerRequestMessage, type DiffWorkerResponseMessage } from "./diff_protocol";

export type DiffComputeProgress = {
  stage: DiffProgressStage;
  percent: number;
};

export type DiffComputeResult =
  | { status: "completed"; result: { documentDiff: MergeItem[]; viewDiff: MergeItem[] }; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;

function assertDiffWorkerProtocolVersion(message: DiffWorkerResponseMessage): void {
  if (message.protocolVersion !== DIFF_WORKER_PROTOCOL_VERSION) {
    throw new Error(`Unsupported diff worker protocol version: ${String(message.protocolVersion)}`);
  }
}


export class DiffWorkerClient {
  private worker: Worker | null = null;
  private readonly fallbackRunner = createCancelableTaskRunner();

  private ensureWorker(): Worker {
    if (this.worker) {
      return this.worker;
    }

    this.worker = new Worker(new URL("./diff.worker.ts", import.meta.url), { type: "module" });
    return this.worker;
  }

  async computeDiff(payload: DiffRequestPayload, options: { onProgress?: (progress: DiffComputeProgress) => void; signal?: AbortSignal } = {}): Promise<DiffComputeResult> {
    try {
      return await this.computeViaWorker(payload, options);
    } catch (error) {
      console.warn("Diff worker unavailable. Falling back to main-thread scheduler.", error);
      return this.computeViaFallback(payload, options);
    }
  }

  private computeViaWorker(payload: DiffRequestPayload, options: { onProgress?: (progress: DiffComputeProgress) => void; signal?: AbortSignal }): Promise<DiffComputeResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `diff-${requestCounter}`;

    return new Promise<DiffComputeResult>((resolve, reject) => {
      const onMessage = (event: MessageEvent<DiffWorkerResponseMessage>) => {
        const message = event.data;
        if (message.requestId !== requestId) {
          return;
        }

        assertDiffWorkerProtocolVersion(message);

        if (message.type === "diff.progress") {
          options.onProgress?.({ stage: message.stage, percent: message.percent });
          return;
        }

        cleanup();
        if (message.type === "diff.result") {
          resolve({ status: "completed", result: message.result, usedFallback: false });
          return;
        }
        if (message.type === "diff.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (message.type === "diff.error") {
          reject(new Error(message.error.message));
        }
      };

      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Diff worker failed"));
      };

      const onAbort = () => {
        this.cancel(requestId);
        cleanup();
        resolve({ status: "cancelled", usedFallback: false });
      };

      const cleanup = () => {
        worker.removeEventListener("message", onMessage);
        worker.removeEventListener("error", onError);
        options.signal?.removeEventListener("abort", onAbort);
      };

      worker.addEventListener("message", onMessage);
      worker.addEventListener("error", onError);
      options.signal?.addEventListener("abort", onAbort, { once: true });
      worker.postMessage({ type: "diff.request", requestId, payload } as DiffWorkerRequestMessage);
    });
  }

  private async computeViaFallback(payload: DiffRequestPayload, options: { onProgress?: (progress: DiffComputeProgress) => void; signal?: AbortSignal }): Promise<DiffComputeResult> {
    const unsubscribe = this.fallbackRunner.onProgress((progress) => {
      const stageMap: DiffProgressStage[] = ["cards", "islands", "edges", "evidence", "view"];
      const stage = stageMap[Math.max(0, Math.min(stageMap.length - 1, progress.completed - 1))] ?? "view";
      const percent = Math.round((progress.completed / progress.total) * 100);
      options.onProgress?.({ stage, percent });
    });

    const abortListener = () => this.fallbackRunner.cancel();
    options.signal?.addEventListener("abort", abortListener, { once: true });
    const outcome = await this.fallbackRunner.run(async (ctx) => buildMergeItemsIncremental(payload.baseDoc, payload.incomingDoc, ctx, payload.options));
    unsubscribe();
    options.signal?.removeEventListener("abort", abortListener);

    if (outcome.status === "cancelled") {
      return { status: "cancelled", usedFallback: true };
    }

    const items = outcome.result.items;
    return {
      status: "completed",
      usedFallback: true,
      result: {
        documentDiff: items.filter((item) => item.kind !== "view.field"),
        viewDiff: items.filter((item) => item.kind === "view.field"),
      },
    };
  }

  cancel(requestId: string): void {
    if (!this.worker) {
      return;
    }

    this.worker.postMessage({ type: "diff.cancel", requestId } as DiffWorkerRequestMessage);
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
