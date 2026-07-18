import { parseInquiryBundleJson, type InquiryBundleIoResult } from "../domain/inquiry_bundle_io";
import type { InquiryBundleV1 } from "../domain/inquiry_journey";
import {
  INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION,
  type InquiryBundleWorkerRequestMessage,
  type InquiryBundleWorkerResponseMessage,
} from "./inquiry_bundle_protocol";

export type InquiryBundleParseResult =
  | { status: "completed"; result: InquiryBundleIoResult; usedFallback: boolean }
  | { status: "cancelled"; usedFallback: boolean };

let requestCounter = 0;

export class InquiryBundleWorkerClient {
  private worker: Worker | null = null;

  private ensureWorker(): Worker {
    if (this.worker) return this.worker;
    this.worker = new Worker(new URL("./inquiry_bundle.worker.ts", import.meta.url), { type: "module" });
    return this.worker;
  }

  async parse(rawText: string, options: { signal?: AbortSignal } = {}): Promise<InquiryBundleParseResult> {
    if (options.signal?.aborted) return { status: "cancelled", usedFallback: false };
    try {
      return await this.parseViaWorker(rawText, options.signal);
    } catch (error) {
      if (options.signal?.aborted) return { status: "cancelled", usedFallback: false };
      console.warn("Inquiry bundle worker unavailable. Falling back to main-thread validation.", error);
      const result = await parseInquiryBundleJson(rawText);
      return options.signal?.aborted
        ? { status: "cancelled", usedFallback: true }
        : { status: "completed", result, usedFallback: true };
    }
  }

  private parseViaWorker(rawText: string, signal?: AbortSignal): Promise<InquiryBundleParseResult> {
    const worker = this.ensureWorker();
    requestCounter += 1;
    const requestId = `inquiry-bundle-${requestCounter}`;

    return new Promise((resolve, reject) => {
      const cleanup = () => {
        worker.removeEventListener("message", onMessage);
        worker.removeEventListener("error", onError);
        signal?.removeEventListener("abort", onAbort);
      };
      const onMessage = (event: MessageEvent<InquiryBundleWorkerResponseMessage>) => {
        const message = event.data;
        if (message.requestId !== requestId) return;
        cleanup();
        if (message.protocolVersion !== INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION) {
          reject(new Error(`Unsupported inquiry bundle worker protocol: ${String(message.protocolVersion)}`));
          return;
        }
        if (message.type === "inquiry-bundle.error") {
          reject(new Error(message.error.message));
          return;
        }
        const result: InquiryBundleIoResult = message.result.ok
          ? { ok: true, bundle: JSON.parse(rawText) as InquiryBundleV1 }
          : message.result;
        resolve({ status: "completed", result, usedFallback: false });
      };
      const onError = (event: ErrorEvent) => {
        cleanup();
        reject(new Error(event.message || "Inquiry bundle worker failed"));
      };
      const onAbort = () => {
        cleanup();
        this.dispose();
        resolve({ status: "cancelled", usedFallback: false });
      };

      worker.addEventListener("message", onMessage);
      worker.addEventListener("error", onError);
      signal?.addEventListener("abort", onAbort, { once: true });
      worker.postMessage({
        type: "inquiry-bundle.parse",
        requestId,
        protocolVersion: INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION,
        rawText,
      } satisfies InquiryBundleWorkerRequestMessage);
    });
  }

  dispose(): void {
    this.worker?.terminate();
    this.worker = null;
  }
}
