import { createCancelableTaskRunner } from "../utils/compute_scheduler";
import { computeTrace } from "./trace_compute";
import { buildTraceAnalyticsMd, computeTraceAnalytics } from "./trace_analytics";
import type { TraceAnalyticsRequestPayload, TraceRequestPayload, TraceWorkerRequestMessage, TraceWorkerResponseMessage } from "./trace_protocol";

export type TraceComputeResult =
  | { status: "completed"; result: ReturnType<typeof computeTrace>; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

export type TraceAnalyticsComputeResult =
  | { status: "completed"; result: { analyticsMd: string; analytics: ReturnType<typeof computeTraceAnalytics> }; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;

export class TraceWorkerClient {
  private worker: Worker | null = null;
  private readonly fallbackRunner = createCancelableTaskRunner();

  private ensureWorker(): Worker {
    if (this.worker) return this.worker;
    this.worker = new Worker(new URL("./trace.worker.ts", import.meta.url), { type: "module" });
    return this.worker;
  }

  async computeTrace(payload: TraceRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal } = {}): Promise<TraceComputeResult> {
    try {
      return await this.computeViaWorker(payload, options);
    } catch (error) {
      console.warn("Trace worker unavailable. Falling back to main-thread scheduler.", error);
      return this.computeViaFallback(payload, options);
    }
  }

  async computeTraceAnalytics(payload: TraceAnalyticsRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal } = {}): Promise<TraceAnalyticsComputeResult> {
    try {
      return await this.computeAnalyticsViaWorker(payload, options);
    } catch (error) {
      console.warn("Trace analytics worker unavailable. Falling back to main-thread scheduler.", error);
      return this.computeAnalyticsViaFallback(payload, options);
    }
  }

  private computeViaWorker(payload: TraceRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal }): Promise<TraceComputeResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `trace-${requestCounter}`;

    return new Promise<TraceComputeResult>((resolve, reject) => {
      const onMessage = (event: MessageEvent<TraceWorkerResponseMessage>) => {
        const message = event.data;
        if (message.requestId !== requestId) return;
        if (message.type === "trace.progress") {
          options.onProgress?.({ stage: message.stage, percent: message.percent });
          return;
        }
        cleanup();
        if (message.type === "trace.result") {
          resolve({ status: "completed", result: message.result, usedFallback: false });
          return;
        }
        if (message.type === "trace.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (message.type === "trace.error") {
          reject(new Error(message.error.message));
        }
      };

      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Trace worker failed"));
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
      worker.postMessage({ type: "trace.request", requestId, payload } as TraceWorkerRequestMessage);
    });
  }

  private async computeViaFallback(payload: TraceRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal }): Promise<TraceComputeResult> {
    const stages = ["collect", "traverse", "render"];
    const unsubscribe = this.fallbackRunner.onProgress((progress) => {
      options.onProgress?.({ stage: stages[progress.completed - 1] ?? "render", percent: Math.round((progress.completed / progress.total) * 100) });
    });
    const abortListener = () => this.fallbackRunner.cancel();
    options.signal?.addEventListener("abort", abortListener, { once: true });

    try {
      const outcome = await this.fallbackRunner.run(async (ctx) => {
        for (let i = 0; i < stages.length; i += 1) {
          ctx.reportProgress({ message: stages[i] ?? "render", completed: i + 1, total: stages.length });
          await ctx.yieldToMainThread();
          if (ctx.isCancelled()) {
            return null;
          }
        }
        return computeTrace({ ...payload, options: { ...payload.options, safeMode: payload.options.safeMode ?? true } });
      });

      if (outcome.status === "cancelled" || outcome.result === null) {
        return { status: "cancelled", usedFallback: true };
      }
      return { status: "completed", result: outcome.result, usedFallback: true };
    } finally {
      unsubscribe();
      options.signal?.removeEventListener("abort", abortListener);
    }
  }

  private computeAnalyticsViaWorker(payload: TraceAnalyticsRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal }): Promise<TraceAnalyticsComputeResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `trace-analytics-${requestCounter}`;

    return new Promise<TraceAnalyticsComputeResult>((resolve, reject) => {
      const onMessage = (event: MessageEvent<TraceWorkerResponseMessage>) => {
        const message = event.data;
        if (message.requestId !== requestId) return;
        if (message.type === "trace.progress") {
          options.onProgress?.({ stage: message.stage, percent: message.percent });
          return;
        }
        cleanup();
        if (message.type === "trace.analytics.result") {
          resolve({ status: "completed", result: message.result, usedFallback: false });
          return;
        }
        if (message.type === "trace.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (message.type === "trace.error") {
          reject(new Error(message.error.message));
        }
      };

      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Trace worker failed"));
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
      worker.postMessage({ type: "trace.analytics.request", requestId, payload } as TraceWorkerRequestMessage);
    });
  }

  private async computeAnalyticsViaFallback(payload: TraceAnalyticsRequestPayload, options: { onProgress?: (progress: { stage: string; percent: number }) => void; signal?: AbortSignal }): Promise<TraceAnalyticsComputeResult> {
    const stages = ["collect", "traverse", "render"];
    const unsubscribe = this.fallbackRunner.onProgress((progress) => {
      options.onProgress?.({ stage: stages[progress.completed - 1] ?? "render", percent: Math.round((progress.completed / progress.total) * 100) });
    });
    const abortListener = () => this.fallbackRunner.cancel();
    options.signal?.addEventListener("abort", abortListener, { once: true });

    try {
      const outcome = await this.fallbackRunner.run(async (ctx) => {
        for (let i = 0; i < stages.length; i += 1) {
          ctx.reportProgress({ message: stages[i] ?? "render", completed: i + 1, total: stages.length });
          await ctx.yieldToMainThread();
          if (ctx.isCancelled()) {
            return null;
          }
        }
        const analytics = computeTraceAnalytics(payload.doc, payload.options.startCardId, {
          ...payload.options,
          safeMode: payload.options.safeMode ?? true,
        });
        return { analyticsMd: buildTraceAnalyticsMd(analytics), analytics };
      });

      if (outcome.status === "cancelled" || outcome.result === null) {
        return { status: "cancelled", usedFallback: true };
      }
      return { status: "completed", result: outcome.result, usedFallback: true };
    } finally {
      unsubscribe();
      options.signal?.removeEventListener("abort", abortListener);
    }
  }

  cancel(requestId: string): void {
    this.worker?.postMessage({ type: "trace.cancel", requestId } as TraceWorkerRequestMessage);
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
