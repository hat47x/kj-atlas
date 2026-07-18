import type { InquiryBundleIoError } from "../domain/inquiry_bundle_io";

export const INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION = 1 as const;

export type InquiryBundleWorkerRequestMessage = {
  type: "inquiry-bundle.parse";
  requestId: string;
  protocolVersion: typeof INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION;
  rawText: string;
};

export type InquiryBundleWorkerResponseMessage =
  | {
      type: "inquiry-bundle.result";
      requestId: string;
      protocolVersion: typeof INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION;
      result: { ok: true } | { ok: false; errors: InquiryBundleIoError[] };
    }
  | {
      type: "inquiry-bundle.error";
      requestId: string;
      protocolVersion: typeof INQUIRY_BUNDLE_WORKER_PROTOCOL_VERSION;
      error: { message: string };
    };
