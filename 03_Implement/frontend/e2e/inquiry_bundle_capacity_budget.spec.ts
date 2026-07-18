import { expect, test, type Page } from "@playwright/test";
import { parseInquiryBundleJson, serializeInquiryBundle } from "../src/domain/inquiry_bundle_io";
import {
  buildRepresentativeInquiryBundle,
  buildRepresentativePerformanceDocument,
  REPRESENTATIVE_CARD_COUNT,
  REPRESENTATIVE_ISLAND_COUNT,
  REPRESENTATIVE_ROUND_COUNT,
} from "./helpers/representative_inquiry_fixture";

const MAX_REPRESENTATIVE_ARTIFACT_BYTES = 512 * 1024;
const MAX_REPRESENTATIVE_JOURNEY_MANIFEST_BYTES = 64 * 1024;
const MAX_REPRESENTATIVE_BUNDLE_BYTES = 5 * 1024 * 1024;
const MAX_IO_WALL_TIME_MS = 2_500;
const MAX_MAIN_THREAD_TASK_MS = 100;
const MAX_KNOWN_IMPORT_LONG_TASK_MS = 500;

async function installLongTaskProbe(page: Page) {
  await page.evaluate(() => {
    const records: number[] = [];
    (window as unknown as { __kjAtlasInquiryLongTasks: number[] }).__kjAtlasInquiryLongTasks = records;
    if (!("PerformanceObserver" in window)) return;
    try {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) records.push(entry.duration);
      });
      observer.observe({ entryTypes: ["longtask"] });
    } catch {
      // Wall-time assertions remain available when this browser omits long-task entries.
    }
  });
}

test("DOMAIN-W-ITERATION-01 measures a representative six-round bundle and guards its current ceiling", async ({ page }, testInfo) => {
  test.slow();
  const bundle = await buildRepresentativeInquiryBundle();
  const serializeStartedAt = performance.now();
  const serialized = await serializeInquiryBundle(bundle);
  const serializeMs = performance.now() - serializeStartedAt;
  expect(serialized.ok).toBe(true);
  if (!serialized.ok) return;

  const artifactBytes = Buffer.byteLength(JSON.stringify(bundle.snapshots[0]), "utf8");
  const journeyManifestBytes = Buffer.byteLength(JSON.stringify(bundle.journey), "utf8");
  const bundleBytes = Buffer.byteLength(serialized.json, "utf8");
  const parseStartedAt = performance.now();
  const parsed = await parseInquiryBundleJson(serialized.json);
  const parseMs = performance.now() - parseStartedAt;

  expect(parsed.ok).toBe(true);
  expect(bundle.snapshots).toHaveLength(REPRESENTATIVE_ROUND_COUNT + 1);
  expect(bundle.journey.roundRecords).toHaveLength(REPRESENTATIVE_ROUND_COUNT);
  expect(bundle.cardLineage).toHaveLength(REPRESENTATIVE_CARD_COUNT * REPRESENTATIVE_ROUND_COUNT);
  expect(artifactBytes).toBeLessThanOrEqual(MAX_REPRESENTATIVE_ARTIFACT_BYTES);
  expect(journeyManifestBytes).toBeLessThanOrEqual(MAX_REPRESENTATIVE_JOURNEY_MANIFEST_BYTES);
  expect(bundleBytes).toBeLessThanOrEqual(MAX_REPRESENTATIVE_BUNDLE_BYTES);
  expect(serializeMs).toBeLessThan(MAX_IO_WALL_TIME_MS);
  expect(parseMs).toBeLessThan(MAX_IO_WALL_TIME_MS);

  await testInfo.attach("inquiry-capacity-measurement.json", {
    contentType: "application/json",
    body: Buffer.from(JSON.stringify({
      cardsPerSnapshot: REPRESENTATIVE_CARD_COUNT,
      islandsPerSnapshot: REPRESENTATIVE_ISLAND_COUNT,
      rounds: REPRESENTATIVE_ROUND_COUNT,
      snapshots: bundle.snapshots.length,
      lineageEdges: bundle.cardLineage.length,
      artifactBytes,
      journeyManifestBytes,
      bundleBytes,
      serializeMs: Number(serializeMs.toFixed(2)),
      parseMs: Number(parseMs.toFixed(2)),
    }, null, 2)),
  });

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const documentChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const documentChooser = await documentChooserPromise;
  await documentChooser.setFiles({
    name: "representative-document.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildRepresentativePerformanceDocument()), "utf8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible({ timeout: 10_000 });
  await page.getByRole("button", { name: "Close panel" }).click();

  await page.getByRole("button", { name: "Advanced" }).click();
  await page.getByRole("button", { name: "Work mode" }).click();
  await page.getByRole("tab", { name: "Inquiry" }).click();
  const inquiryPanel = page.locator('[data-panel="inquiry-journey-prototype"]');
  await expect(inquiryPanel).toBeVisible();
  await installLongTaskProbe(page);

  const uiImportStartedAt = performance.now();
  await inquiryPanel.locator('input[type="file"]').setInputFiles({
    name: "representative-inquiry.kj-atlas-inquiry.json",
    mimeType: "application/json",
    buffer: Buffer.from(serialized.json, "utf8"),
  });
  await expect(inquiryPanel.getByRole("status").last()).toContainText("Inquiry file imported", {
    timeout: MAX_IO_WALL_TIME_MS,
  });
  const uiImportMs = performance.now() - uiImportStartedAt;
  const maxLongTaskMs = await page.evaluate(() => {
    const records = (window as unknown as { __kjAtlasInquiryLongTasks?: number[] }).__kjAtlasInquiryLongTasks ?? [];
    return records.reduce((maximum, duration) => Math.max(maximum, duration), 0);
  });

  const metrics = {
    artifactBytes,
    journeyManifestBytes,
    bundleBytes,
    serializeMs: Number(serializeMs.toFixed(2)),
    parseMs: Number(parseMs.toFixed(2)),
    uiImportMs: Number(uiImportMs.toFixed(2)),
    maxLongTaskMs: Number(maxLongTaskMs.toFixed(2)),
  };
  console.info(`DOMAIN-W-ITERATION-01 capacity: ${JSON.stringify(metrics)}`);
  await testInfo.attach("inquiry-ui-import-measurement.json", {
    contentType: "application/json",
    body: Buffer.from(JSON.stringify(metrics, null, 2)),
  });
  if (maxLongTaskMs > MAX_MAIN_THREAD_TASK_MS) {
    testInfo.annotations.push({
      type: "issue",
      description: "PERF-INQUIRY-01: move representative inquiry import off the main thread",
    });
  }
  expect(uiImportMs).toBeLessThan(MAX_IO_WALL_TIME_MS);
  expect(maxLongTaskMs).toBeLessThanOrEqual(MAX_KNOWN_IMPORT_LONG_TASK_MS);
});
