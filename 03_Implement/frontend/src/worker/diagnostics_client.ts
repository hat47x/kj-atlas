import { createCancelableTaskRunner } from "../utils/compute_scheduler";
import { computeDiagnostics } from "./diagnostics_compute";
import { normalizeDiagnosticsData } from "./diagnostics_protocol";
import type { DiagnosticsProgressStage, DiagnosticsRequestPayload, DiagnosticsWorkerRequestMessage, DiagnosticsWorkerResponseMessage } from "./diagnostics_protocol";

export type DiagnosticsComputeProgress = { stage: DiagnosticsProgressStage; percent: number };

export type DiagnosticsComputeResult =
  | { status: "completed"; result: { diagnosticsMd: string; diagnosticsData: ReturnType<typeof computeDiagnostics>["diagnosticsData"] }; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;
const VALID_PROGRESS_STAGES: DiagnosticsProgressStage[] = ["outline", "recommendations", "contradictions", "distribution", "dialectic", "render"];

function isObjectRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}

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
        if (!isObjectRecord(message)) return;
        if (message.requestId !== requestId) return;

        if (typeof message.type !== "string") {
          cleanup();
          reject(new Error("Invalid diagnostics payload: message type must be a string"));
          return;
        }
        const messageType = message.type;

        if (messageType === "diagnostics.progress") {
          if (!VALID_PROGRESS_STAGES.includes(message.stage) || typeof message.percent !== "number" || !Number.isFinite(message.percent) || message.percent < 0 || message.percent > 100) {
            cleanup();
            reject(new Error("Invalid diagnostics payload: progress message is malformed"));
            return;
          }
          options.onProgress?.({ stage: message.stage, percent: message.percent });
          return;
        }
        cleanup();
        if (messageType === "diagnostics.result") {
          if (!isObjectRecord(message.result)) {
            reject(new Error("Invalid diagnostics payload: result envelope must be an object"));
            return;
          }

          const diagnosticsMd = message.result.diagnosticsMd;
          if (typeof diagnosticsMd !== "string") {
            reject(new Error("Invalid diagnostics payload: diagnosticsMd must be a string"));
            return;
          }

          let diagnosticsData;
          try {
            diagnosticsData = normalizeDiagnosticsData(message.result.diagnosticsData);
          } catch (error) {
            reject(error);
            return;
          }

          resolve({
            status: "completed",
            result: {
              diagnosticsMd,
              diagnosticsData,
            },
            usedFallback: false,
          });
          return;
        }
        if (messageType === "diagnostics.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (messageType === "diagnostics.error") {
          if (!isObjectRecord(message.error) || typeof message.error.message !== "string") {
            reject(new Error("Invalid diagnostics payload: diagnostics.error must include a string message"));
            return;
          }
          reject(new Error(message.error.message));
          return;
        }

        reject(new Error(`Invalid diagnostics payload: unknown message type ${String(messageType)}`));
      };

      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Diagnostics worker failed"));
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
    try {
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

      if (outcome.status === "cancelled" || outcome.result === null) {
        return { status: "cancelled", usedFallback: true };
      }
      return {
        status: "completed",
        usedFallback: true,
        result: {
          diagnosticsMd: outcome.result.diagnosticsMd,
          diagnosticsData: normalizeDiagnosticsData(outcome.result.diagnosticsData),
        },
      };
    } finally {
      unsubscribe();
      options.signal?.removeEventListener("abort", abortListener);
    }
  }

  cancel(requestId: string): void {
    this.worker?.postMessage({ type: "diagnostics.cancel", requestId } as DiagnosticsWorkerRequestMessage);
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
