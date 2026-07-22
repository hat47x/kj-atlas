import { buildBundleZipArrayBuffer } from "../export/bundle_zip";
import { createCancelableTaskRunner } from "../utils/compute_scheduler";
import type { BundleZipRequestPayload, BundleZipWorkerRequestMessage, BundleZipWorkerResponseMessage } from "./bundle_zip_protocol";

export type BundleZipComputeResult =
  | { status: "completed"; result: { zipBuffer: ArrayBuffer }; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;

export class BundleZipWorkerClient {
  private worker: Worker | null = null;
  private readonly fallbackRunner = createCancelableTaskRunner();
  private runtimeFallbackNotified = false;

  private canUseWorkerRuntime(): boolean {
    return typeof Worker !== "undefined";
  }

  private ensureWorker(): Worker {
    if (this.worker) return this.worker;
    if (!this.canUseWorkerRuntime()) {
      throw new Error("Worker runtime unavailable");
    }
    this.worker = new Worker(new URL("./bundle_zip.worker.ts", import.meta.url), { type: "module" });
    return this.worker;
  }

  async buildZip(
    payload: BundleZipRequestPayload,
    options: { onProgress?: (percent: number) => void; signal?: AbortSignal } = {},
  ): Promise<BundleZipComputeResult> {
    if (options.signal?.aborted) {
      return { status: "cancelled", usedFallback: false };
    }

    try {
      return await this.buildZipViaWorker(payload, options);
    } catch (error) {
      if (this.canUseWorkerRuntime()) {
        console.warn("Bundle zip worker unavailable. Falling back to main-thread scheduler.", error);
      } else if (!this.runtimeFallbackNotified) {
        this.runtimeFallbackNotified = true;
        console.info("Bundle zip worker runtime unavailable. Using main-thread scheduler.");
      }
      return this.buildZipViaFallback(payload, options);
    }
  }

  private buildZipViaWorker(
    payload: BundleZipRequestPayload,
    options: { onProgress?: (percent: number) => void; signal?: AbortSignal },
  ): Promise<BundleZipComputeResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `bundle-zip-${requestCounter}`;

    return new Promise<BundleZipComputeResult>((resolve, reject) => {
      const onMessage = (event: MessageEvent<BundleZipWorkerResponseMessage>) => {
        const message = event.data;
        if (!message || typeof message !== "object" || !("requestId" in message) || message.requestId !== requestId) {
          return;
        }

        if (message.type === "bundle.zip.progress") {
          options.onProgress?.(message.percent);
          return;
        }

        cleanup();
        if (message.type === "bundle.zip.result") {
          resolve({ status: "completed", result: message.result, usedFallback: false });
          return;
        }
        if (message.type === "bundle.zip.cancelled") {
          resolve({ status: "cancelled", usedFallback: false });
          return;
        }
        if (message.type === "bundle.zip.error") {
          reject(new Error(message.error.message));
        }
      };

      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Bundle zip worker failed"));
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
      worker.postMessage({ type: "bundle.zip.request", requestId, payload } as BundleZipWorkerRequestMessage);
    });
  }

  private async buildZipViaFallback(
    payload: BundleZipRequestPayload,
    options: { onProgress?: (percent: number) => void; signal?: AbortSignal },
  ): Promise<BundleZipComputeResult> {
    const unsubscribe = this.fallbackRunner.onProgress((progress) => {
      options.onProgress?.(Math.round((progress.completed / progress.total) * 100));
    });
    const abortListener = () => this.fallbackRunner.cancel();
    options.signal?.addEventListener("abort", abortListener, { once: true });

    try {
      const outcome = await this.fallbackRunner.run(async (ctx) => {
        ctx.reportProgress({ message: "collect", completed: 1, total: 2 });
        await ctx.yieldToMainThread();
        if (ctx.isCancelled()) {
          return null;
        }
        const zipBuffer = await buildBundleZipArrayBuffer(payload.files, {
          onProgress: (percent) => {
            options.onProgress?.(percent);
          },
        });
        ctx.reportProgress({ message: "zip", completed: 2, total: 2 });
        return { zipBuffer };
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
    this.worker?.postMessage({ type: "bundle.zip.cancel", requestId } as BundleZipWorkerRequestMessage);
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
