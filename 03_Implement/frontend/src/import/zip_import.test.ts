import { describe, expect, test } from "vitest";
import JSZip from "jszip";
import { detectReviewPackFiles, readZipFiles } from "./zip_import";

async function buildZipFile(files: Record<string, string | Uint8Array>, name = "pack.zip"): Promise<File> {
  const zip = new JSZip();
  for (const [path, content] of Object.entries(files)) {
    zip.file(path, content);
  }
  const blob = await zip.generateAsync({ type: "blob" });
  return new File([blob], name, { type: "application/zip" });
}

describe("zip review pack import", () => {
  test("reads and normalizes supported files", async () => {
    const zipFile = await buildZipFile({
      "kj-atlas-review-pack-2026/document.json": '{"id":"doc","title":"t","cards":[],"edges":[],"islands":[],"narratives":[],"version":2,"updatedAt":"2025-01-01T00:00:00.000Z"}',
      "kj-atlas-review-pack-2026/view.json": '{"version":"1","generatedAt":"2025-01-01T00:00:00.000Z","docSignature":"doc","camera":{"panX":0,"panY":0,"zoom":1},"viewState":{"summaryView":false,"abstractMapView":false,"hideSourceCards":false,"maxDepth":"all","focusIslandId":null,"showReadingOrder":false},"export":{"mode":"viewport"}}',
      "kj-atlas-review-pack-2026/diagnostics.md": "# diag",
      "kj-atlas-review-pack-2026/snapshot.png": new Uint8Array([137, 80, 78, 71]),
      "kj-atlas-review-pack-2026/ignored.txt": "ignored",
    });

    const entries = await readZipFiles(zipFile);
    expect(entries.has("document.json")).toBe(true);
    expect(entries.has("view.json")).toBe(true);
    expect(entries.has("diagnostics.md")).toBe(true);
    expect(entries.has("snapshot.png")).toBe(true);
    expect(entries.has("ignored.txt")).toBe(false);

    const detection = detectReviewPackFiles(entries);
    expect(detection.documentPath).toBe("document.json");
    expect(detection.viewPath).toBe("view.json");
    expect(detection.snapshotPath).toBe("snapshot.png");
    expect(detection.diagnosticsPath).toBe("diagnostics.md");
  });

  test("detects nested document/view paths", async () => {
    const zipFile = await buildZipFile({
      "nested/a/document.json": "{}",
      "nested/a/view.json": "{}",
    });

    const entries = await readZipFiles(zipFile);
    const detection = detectReviewPackFiles(entries);
    expect(detection.documentPath).toBe("a/document.json");
    expect(detection.viewPath).toBe("a/view.json");
  });

  test("strips a shared root directory in generic zip exports", async () => {
    const zipFile = await buildZipFile({
      "review-pack/document.json": "{}",
      "review-pack/view.json": "{}",
      "review-pack/diagnostics.md": "ok",
    });

    const entries = await readZipFiles(zipFile);
    expect(entries.has("document.json")).toBe(true);
    expect(entries.has("view.json")).toBe(true);
    expect(entries.has("diagnostics.md")).toBe(true);
  });

  test("ignores unsafe parent traversal paths", async () => {
    const zipFile = await buildZipFile({
      "../document.json": "{}",
      "view.json": "{}",
    });

    const entries = await readZipFiles(zipFile);
    expect(entries.has("../document.json")).toBe(false);
    expect(entries.has("view.json")).toBe(true);
  });
});
