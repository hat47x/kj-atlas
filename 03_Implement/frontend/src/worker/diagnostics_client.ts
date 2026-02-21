import { createCancelableTaskRunner } from "../utils/compute_scheduler";
import { computeDiagnostics } from "./diagnostics_compute";
import type { DiagnosticsProgressStage, DiagnosticsRequestPayload, DiagnosticsWorkerRequestMessage, DiagnosticsWorkerResponseMessage } from "./diagnostics_protocol";

export type DiagnosticsComputeProgress = { stage: DiagnosticsProgressStage; percent: number };

export type DiagnosticsComputeResult =
  | { status: "completed"; result: { diagnosticsMd: string; diagnosticsData: ReturnType<typeof computeDiagnostics>["diagnosticsData"] }; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;

export class DiagnosticsWorkerClient {
  private worker: Worker | null = null;
  private readonly fallbackRunner = createCancelableTaskRunner();

  private ensureWorker(): Worker {
    if (this.worker) return this.worker;
    this.worker = new Worker(new URL("./diagnostics.worker.ts", import.meta.url), { type: "module" });
    return this.worker;
  }

  async computeDiagnostics(payload: DiagnosticsRequestPayload, options: { onProgress?: (progress: DiagnosticsComputeProgress) => void; signal?: AbortSignal } = {}): Promise<DiagnosticsComputeResult> {
    try {
      return await this.computeViaWorker(payload, options);
    } catch (error) {
      console.warn("Diagnostics worker unavailable. Falling back to main-thread scheduler.", error);
      return this.computeViaFallback(payload, options);
    }
  }

  private computeViaWorker(payload: DiagnosticsRequestPayload, options: { onProgress?: (progress: DiagnosticsComputeProgress) => void; signal?: AbortSignal }): Promise<DiagnosticsComputeResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `diagnostics-${requestCounter}`;

    return new Promise<DiagnosticsComputeResult>((resolve, reject) => {
      const onMessage = (event: MessageEvent<DiagnosticsWorkerResponseMessage>) => {
        const message = event.data;
        if (message.requestId !== requestId) return;
        if (message.type === "diagnostics.progress") {
          options.onProgress?.({ stage: message.stage, percent: message.percent });
          return;
        }
        cleanup();
        if (message.type === "diagnostics.result") {
          resolve({ status: "completed", result: message.result, usedFallback: false });
          return;
        }
        if (message.type === "diagnostics.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (message.type === "diagnostics.error") {
          reject(new Error(message.error.message));
        }
      };

      const onAbort = () => {
        this.cancel(requestId);
        cleanup();
        resolve({ status: "cancelled", usedFallback: false });
      };

      const cleanup = () => {
        worker.removeEventListener("message", onMessage);
        options.signal?.removeEventListener("abort", onAbort);
      };

      worker.addEventListener("message", onMessage);
      options.signal?.addEventListener("abort", onAbort, { once: true });
      worker.postMessage({ type: "diagnostics.request", requestId, payload } as DiagnosticsWorkerRequestMessage);
    });
  }

  private async computeViaFallback(payload: DiagnosticsRequestPayload, options: { onProgress?: (progress: DiagnosticsComputeProgress) => void; signal?: AbortSignal }): Promise<DiagnosticsComputeResult> {
    const stages: DiagnosticsProgressStage[] = ["outline", "recommendations", "contradictions", "distribution", "dialectic", "render"];
    const unsubscribe = this.fallbackRunner.onProgress((progress) => {
      const stage = stages[Math.max(0, Math.min(stages.length - 1, progress.completed - 1))] ?? "render";
      options.onProgress?.({ stage, percent: Math.round((progress.completed / progress.total) * 100) });
    });
    const abortListener = () => this.fallbackRunner.cancel();
    options.signal?.addEventListener("abort", abortListener, { once: true });
    const outcome = await this.fallbackRunner.run(async (ctx) => {
      const marks = [10, 30, 50, 70, 85, 100];
      for (let i = 0; i < marks.length; i += 1) {
        ctx.reportProgress({ message: stages[i] ?? "render", completed: i + 1, total: marks.length });
        await ctx.yieldToMainThread();
        if (ctx.isCancelled()) {
          return null;
        }
      }
      return computeDiagnostics({ ...payload, options: { ...payload.options, safeMode: payload.options?.safeMode ?? true } });
    });
    unsubscribe();
    options.signal?.removeEventListener("abort", abortListener);

    if (outcome.status === "cancelled" || outcome.result === null) {
      return { status: "cancelled", usedFallback: true };
    }
    return { status: "completed", usedFallback: true, result: outcome.result };
  }

  cancel(requestId: string): void {
    this.worker?.postMessage({ type: "diagnostics.cancel", requestId } as DiagnosticsWorkerRequestMessage);
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
