import { afterEach, describe, expect, it, vi } from "vitest";

import { createRepresentativeInquiryBundle } from "../domain/inquiry_journey.fixture";
import { serializeInquiryBundle } from "../domain/inquiry_bundle_io";
import { InquiryBundleWorkerClient } from "./inquiry_bundle_client";

const originalWorker = globalThis.Worker;

afterEach(() => {
  globalThis.Worker = originalWorker;
  vi.restoreAllMocks();
});

describe("InquiryBundleWorkerClient", () => {
  it("returns a strict worker result", async () => {
    const serialized = await serializeInquiryBundle(createRepresentativeInquiryBundle());
    expect(serialized.ok).toBe(true);
    if (!serialized.ok) return;
    const exportedBundle = serialized.bundle;

    class FakeWorker {
      private readonly messageListeners = new Set<(event: MessageEvent) => void>();
      addEventListener(type: string, listener: (event: MessageEvent) => void) {
        if (type === "message") this.messageListeners.add(listener);
      }
      removeEventListener(type: string, listener: (event: MessageEvent) => void) {
        if (type === "message") this.messageListeners.delete(listener);
      }
      postMessage(message: { requestId: string }) {
        for (const listener of this.messageListeners) {
          listener({ data: {
            type: "inquiry-bundle.result",
            requestId: message.requestId,
            protocolVersion: 1,
            result: { ok: true },
          } } as MessageEvent);
        }
      }
      terminate() {}
    }

    globalThis.Worker = FakeWorker as unknown as typeof Worker;
    const result = await new InquiryBundleWorkerClient().parse(serialized.json);
    expect(result).toEqual({
      status: "completed",
      result: { ok: true, bundle: exportedBundle },
      usedFallback: false,
    });
  });

  it("falls back to the same strict parser when Worker is unavailable", async () => {
    globalThis.Worker = class {
      constructor() { throw new Error("worker unavailable"); }
    } as unknown as typeof Worker;
    vi.spyOn(console, "warn").mockImplementation(() => {});

    const result = await new InquiryBundleWorkerClient().parse("{not-json");
    expect(result).toEqual({
      status: "completed",
      result: { ok: false, errors: [{ code: "invalid_json", path: "$", message: "Invalid JSON." }] },
      usedFallback: true,
    });
  });

  it("terminates the worker and ignores a delayed result after cancellation", async () => {
    let terminated = false;
    class FakeWorker {
      addEventListener() {}
      removeEventListener() {}
      postMessage() {}
      terminate() { terminated = true; }
    }
    globalThis.Worker = FakeWorker as unknown as typeof Worker;

    const controller = new AbortController();
    const promise = new InquiryBundleWorkerClient().parse("{}", { signal: controller.signal });
    controller.abort();

    await expect(promise).resolves.toEqual({ status: "cancelled", usedFallback: false });
    expect(terminated).toBe(true);
  });
});
