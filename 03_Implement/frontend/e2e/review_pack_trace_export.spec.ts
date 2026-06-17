import JSZip from "jszip";
import { expect, test, type Download, type Page } from "@playwright/test";
import { buildReviewPackTraceDocument } from "./helpers/product_value_fixtures";

async function readDownloadToBuffer(download: Download): Promise<Buffer> {
  const stream = await download.createReadStream();
  if (!stream) {
    throw new Error("Failed to open download stream");
  }

  const chunks: Buffer[] = [];
  await new Promise<void>((resolve, reject) => {
    stream.on("data", (chunk: Buffer | string) => {
      chunks.push(Buffer.isBuffer(chunk) ? chunk : Buffer.from(chunk));
    });
    stream.on("end", () => resolve());
    stream.on("error", reject);
  });

  return Buffer.concat(chunks);
}

async function exportBundleFileNames(page: Page): Promise<string[]> {
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export bundle (.zip)" }).click();
  const download = await downloadPromise;
  const zipBuffer = await readDownloadToBuffer(download);
  const zip = await JSZip.loadAsync(zipBuffer);
  return Object.keys(zip.files).sort();
}

test("review pack export keeps trace controls consistent with actual zip contents", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();

  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "review-pack-trace-export.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildReviewPackTraceDocument()), "utf-8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced current document")).toBeVisible();

  await page.getByRole("button", { name: "Close panel" }).click();
  await expect(page.locator('[data-panel="share-replay"]')).toBeHidden();

  await page.getByRole("option", { name: "trace target claim" }).click();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();

  await page.getByLabel("Include reading outline").uncheck();
  await page.getByLabel("Include diagnostics").uncheck();

  const traceCheckbox = page.getByLabel("Include traces for selected card");
  await expect(traceCheckbox).toBeEnabled();
  await expect(traceCheckbox).toBeChecked();
  await expect(page.getByText("Evidence, contradiction, and analytics traces for the selected card will be included.")).toBeVisible();

  await page.getByLabel("Overview (high-level summary)").check();
  await expect(traceCheckbox).toBeDisabled();
  await expect(traceCheckbox).not.toBeChecked();
  await expect(page.getByText("Overview exports do not include trace files. Select Detail when trace files are needed.")).toBeVisible();

  const overviewFileNames = await exportBundleFileNames(page);
  expect(overviewFileNames.some((name) => name.includes("evidence_trace_"))).toBe(false);
  expect(overviewFileNames.some((name) => name.includes("contradiction_trace_"))).toBe(false);
  expect(overviewFileNames.some((name) => name.includes("trace_analytics_"))).toBe(false);

  await expect(page.getByRole("button", { name: "Export bundle (.zip)" })).toBeEnabled();
  await page.getByLabel("Detail (full trace exports)").check();
  await expect(traceCheckbox).toBeEnabled();
  await expect(traceCheckbox).toBeChecked();

  const detailFileNames = await exportBundleFileNames(page);
  expect(detailFileNames.some((name) => name.endsWith("evidence_trace_c-target.md"))).toBe(true);
  expect(detailFileNames.some((name) => name.endsWith("contradiction_trace_c-target.md"))).toBe(true);
  expect(detailFileNames.some((name) => name.endsWith("trace_analytics_c-target.md"))).toBe(true);
});
