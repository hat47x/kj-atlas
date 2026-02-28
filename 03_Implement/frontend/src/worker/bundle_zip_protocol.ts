import type { BundleFile } from "../export/bundle_export";

export type BundleZipRequestPayload = {
  files: BundleFile[];
};

export type BundleZipWorkerRequestMessage =
  | { type: "bundle.zip.request"; requestId: string; payload: BundleZipRequestPayload }
  | { type: "bundle.zip.cancel"; requestId: string };

export type BundleZipWorkerResponseMessage =
  | { type: "bundle.zip.progress"; requestId: string; percent: number }
  | { type: "bundle.zip.result"; requestId: string; result: { zipBuffer: ArrayBuffer } }
  | { type: "bundle.zip.cancelled"; requestId: string }
  | { type: "bundle.zip.error"; requestId: string; error: { code: string; message: string; details?: unknown } };
