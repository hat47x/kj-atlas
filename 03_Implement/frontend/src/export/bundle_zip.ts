import JSZip from "jszip";
import type { BundleFile } from "./bundle_export";

export async function buildBundleZipArrayBuffer(
  files: BundleFile[],
  options: { onProgress?: (percent: number) => void } = {},
): Promise<ArrayBuffer> {
  const zip = new JSZip();
  for (const file of [...files].sort((left, right) => left.path.localeCompare(right.path))) {
    zip.file(file.path, file.content);
  }

  return zip.generateAsync({ type: "arraybuffer" }, (metadata) => {
    options.onProgress?.(Math.max(0, Math.min(100, Math.round(metadata.percent))));
  });
}
