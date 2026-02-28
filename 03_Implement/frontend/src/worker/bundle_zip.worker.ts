/// <reference lib="webworker" />

import { buildBundleZipArrayBuffer } from "../export/bundle_zip";
import type { BundleZipWorkerRequestMessage, BundleZipWorkerResponseMessage } from "./bundle_zip_protocol";

const cancelledRequestIds = new Set<string>();
const activeRequestIds = new Set<string>();

function postMessageSafe(message: BundleZipWorkerResponseMessage): void {
  self.postMessage(message);
}

self.onmessage = (event: MessageEvent<BundleZipWorkerRequestMessage>) => {
  const message = event.data;

  if (message.type === "bundle.zip.cancel") {
    if (!activeRequestIds.has(message.requestId)) {
      return;
    }
    cancelledRequestIds.add(message.requestId);
    return;
  }

  const { requestId, payload } = message;
  activeRequestIds.add(requestId);
  cancelledRequestIds.delete(requestId);

  const isCancelled = () => cancelledRequestIds.has(requestId);

  void buildBundleZipArrayBuffer(payload.files, {
    onProgress: (percent) => {
      if (isCancelled()) {
        return;
      }
      postMessageSafe({ type: "bundle.zip.progress", requestId, percent });
    },
  }).then((zipBuffer) => {
    if (isCancelled()) {
      postMessageSafe({ type: "bundle.zip.cancelled", requestId });
      return;
    }

    postMessageSafe({ type: "bundle.zip.result", requestId, result: { zipBuffer } });
  }).catch((error) => {
    const messageText = error instanceof Error ? error.message : "Unknown bundle zip worker error";
    postMessageSafe({ type: "bundle.zip.error", requestId, error: { code: "BUNDLE_ZIP_WORKER_ERROR", message: messageText } });
  }).finally(() => {
    activeRequestIds.delete(requestId);
    cancelledRequestIds.delete(requestId);
  });
};

export {};
