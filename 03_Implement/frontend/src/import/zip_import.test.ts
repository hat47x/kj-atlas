import { describe, expect, test } from "vitest";
import JSZip from "jszip";
import {
  ZIP_MAX_COMPRESSION_RATIO,
  ZIP_MAX_FILE_COUNT,
  ZIP_MAX_FILE_UNCOMPRESSED_BYTES,
  ZIP_MAX_TEXT_FILE_BYTES,
  detectReviewPackFiles,
  normalizeZipPath,
  readZipFiles,
} from "./zip_import";

async function buildZipFile(files: Record<string, string | Uint8Array>, name = "pack.zip"): Promise<File> {
  const zip = new JSZip();
  for (const [path, content] of Object.entries(files)) {
    zip.file(path, content);
  }
  const blob = await zip.generateAsync({ type: "blob" });
  return new File([blob], name, { type: "application/zip" });
}

function buildPngWithDimensions(width: number, height: number): Uint8Array {
  const bytes = new Uint8Array(33);
  bytes.set([137, 80, 78, 71, 13, 10, 26, 10], 0);
  bytes.set([0, 0, 0, 13], 8);
  bytes.set([73, 72, 68, 82], 12);
  const view = new DataView(bytes.buffer);
  view.setUint32(16, width);
  view.setUint32(20, height);
  bytes.set([8, 2, 0, 0, 0], 24);
  bytes.set([0, 0, 0, 0], 29);
  return bytes;
}

describe("zip review pack import", () => {
  test("reads and normalizes supported files", async () => {
    const zipFile = await buildZipFile({
      "kj-atlas-review-pack-2026/document.json": '{"id":"doc","title":"t","cards":[],"edges":[],"islands":[],"narratives":[],"version":1,"updatedAt":"2025-01-01T00:00:00.000Z"}',
      "kj-atlas-review-pack-2026/view.json": '{"version":"1","generatedAt":"2025-01-01T00:00:00.000Z","docSignature":"doc","camera":{"panX":0,"panY":0,"zoom":1},"viewState":{"summaryView":false,"abstractMapView":false,"hideSourceCards":false,"maxDepth":"all","focusIslandId":null,"showReadingOrder":false},"export":{"mode":"viewport"}}',
      "kj-atlas-review-pack-2026/diagnostics.md": "# diag",
      "kj-atlas-review-pack-2026/snapshot.png": buildPngWithDimensions(100, 100),
      "kj-atlas-review-pack-2026/representative_visual_cue_assets.json": '{"version":"1","documentId":"doc","assets":[]}',
      "kj-atlas-review-pack-2026/ignored.txt": "ignored",
    });

    const imported = await readZipFiles(zipFile);
    const entries = imported.entries;
    expect(entries.has("document.json")).toBe(true);
    expect(entries.has("view.json")).toBe(true);
    expect(entries.has("diagnostics.md")).toBe(true);
    expect(entries.has("snapshot.png")).toBe(true);
    expect(entries.has("representative_visual_cue_assets.json")).toBe(true);
    expect(entries.has("ignored.txt")).toBe(false);
    expect(imported.skippedUnsupportedCount).toBe(1);

    const detection = detectReviewPackFiles(entries);
    expect(detection.documentPath).toBe("document.json");
    expect(detection.viewPath).toBe("view.json");
    expect(detection.snapshotPath).toBe("snapshot.png");
    expect(detection.diagnosticsPath).toBe("diagnostics.md");
    expect(detection.visualCueAssetsPath).toBe("representative_visual_cue_assets.json");
  });

  test("detects nested document/view paths", async () => {
    const zipFile = await buildZipFile({
      "nested/a/document.json": "{}",
      "nested/a/view.json": "{}",
    });

    const imported = await readZipFiles(zipFile);
    const detection = detectReviewPackFiles(imported.entries);
    expect(detection.documentPath).toBe("nested/a/document.json");
    expect(detection.viewPath).toBe("nested/a/view.json");
  });

  test("strips kj-atlas root directory prefix", async () => {
    const zipFile = await buildZipFile({
      "kj-atlas-review-pack-20260101/document.json": "{}",
      "kj-atlas-review-pack-20260101/view.json": "{}",
      "kj-atlas-review-pack-20260101/diagnostics.md": "ok",
    });

    const imported = await readZipFiles(zipFile);
    expect(imported.entries.has("document.json")).toBe(true);
    expect(imported.entries.has("view.json")).toBe(true);
    expect(imported.entries.has("diagnostics.md")).toBe(true);
  });

  test("rejects parent traversal paths", () => {
    expect(() => normalizeZipPath("../document.json", false)).toThrow(/Z002/);
    expect(() => normalizeZipPath("safe/../../document.json", false)).toThrow(/Z002/);
    expect(() => normalizeZipPath("/absolute/document.json", false)).toThrow(/Z002/);
    expect(() => normalizeZipPath("C:/absolute/document.json", false)).toThrow(/Z002/);
    expect(() => normalizeZipPath("\\\\network\\share\\document.json", false)).toThrow(/Z002/);
    expect(() => normalizeZipPath("safe/\u0000/document.json", false)).toThrow(/Z002/);
  });

  test("rejects zip bombs by file count", async () => {
    const files: Record<string, string> = {};
    for (let index = 0; index <= ZIP_MAX_FILE_COUNT; index += 1) {
      files[`f-${index}.json`] = "{}";
    }

    const zipFile = await buildZipFile(files);
    await expect(readZipFiles(zipFile)).rejects.toThrow(/Z001/);
  });

  test("rejects oversized text payloads", async () => {
    const zipFile = await buildZipFile({
      "document.json": "a".repeat(ZIP_MAX_TEXT_FILE_BYTES + 1),
      "view.json": "{}",
    });

    await expect(readZipFiles(zipFile)).rejects.toThrow(/Z001/);
  });

  test("rejects oversized per-file uncompressed payloads", async () => {
    const zipFile = await buildZipFile({
      "snapshot.png": new Uint8Array(ZIP_MAX_FILE_UNCOMPRESSED_BYTES + 1),
    });

    await expect(readZipFiles(zipFile)).rejects.toThrow(/Z001/);
  });

  test("rejects suspicious compression ratio", async () => {
    const zip = new JSZip();
    const content = "a".repeat(Math.min(1_000_000, ZIP_MAX_TEXT_FILE_BYTES - 10));
    zip.file("document.json", content);
    const blob = await zip.generateAsync({ type: "blob", compression: "DEFLATE", compressionOptions: { level: 9 } });
    const zipFile = new File([blob], "ratio.zip", { type: "application/zip" });
    const compressedBytes = zipFile.size;
    const expectedRatio = content.length / Math.max(compressedBytes, 1);
    expect(expectedRatio).toBeGreaterThan(ZIP_MAX_COMPRESSION_RATIO);

    await expect(readZipFiles(zipFile)).rejects.toThrow(/Z001/);
  });

  test("rejects unsupported executable extension", async () => {
    const zipFile = await buildZipFile({
      "document.json": "{}",
      "view.json": "{}",
      "payload.exe": "MZ",
    });

    const imported = await readZipFiles(zipFile);
    expect(imported.entries.has("payload.exe")).toBe(false);
    expect(imported.skippedUnsupportedCount).toBe(1);
  });

  test("rejects oversized png dimensions", async () => {
    const zipFile = await buildZipFile({
      "document.json": "{}",
      "view.json": "{}",
      "snapshot.png": buildPngWithDimensions(9000, 100),
    });

    await expect(readZipFiles(zipFile)).rejects.toThrow(/Z003/);
  });
});
