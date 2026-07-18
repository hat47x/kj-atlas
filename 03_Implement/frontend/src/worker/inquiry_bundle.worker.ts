/// <reference lib="webworker" />

import { parseInquiryBundleJson } from "../domain/inquiry_bundle_io";
import {
  INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION,
  type InquiryBundleWorkerRequestMessage,
  type InquiryBundleWorkerResponseMessage,
} from "./inquiry_bundle_protocol";

self.onmessage = async (event: MessageEvent<InquiryBundleWorkerRequestMessage>) => {
  const message = event.data;
  if (
    message.type !== "inquiry-bundle.parse"
    || message.protocolVersion !== INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION
  ) return;

  try {
    const parsed = await parseInquiryBundleJson(message.rawText);
    self.postMessage({
      type: "inquiry-bundle.result",
      requestId: message.requestId,
      protocolVersion: INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION,
      result: parsed.ok ? { ok: true } : { ok: false, errors: parsed.errors },
    } satisfies InquiryBundleWorkerResponseMessage);
  } catch (error) {
    self.postMessage({
      type: "inquiry-bundle.error",
      requestId: message.requestId,
      protocolVersion: INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION,
      error: { message: error instanceof Error ? error.message : "Unknown inquiry bundle worker error" },
    } satisfies InquiryBundleWorkerResponseMessage);
  }
};

export {};
