import { readFile, writeFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";

import { parseInquiryBundleJson, serializeInquiryBundle } from "../src/domain/inquiry_bundle_io";
import { createRepresentativeInquiryBundle } from "../src/domain/inquiry_journey.fixture";
import { openAdvancedWorkMode, selectWorkModeTab } from "./helpers/i18n";

test("DOMAIN-W-ITERATION-01 saves a selected round as an immutable self-contained bundle", async ({ page }, testInfo) => {
  const source = createRepresentativeInquiryBundle();
  const serialized = await serializeInquiryBundle(source);
  expect(serialized.ok).toBe(true);
  if (!serialized.ok) return;

  const inquiryPath = testInfo.outputPath("source-inquiry.kj-atlas-inquiry.json");
  await writeFile(inquiryPath, serialized.json, "utf8");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Close start panel" }).click();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const chooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const chooser = await chooserPromise;
  await chooser.setFiles({
    name: "inquiry-origin.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(source.snapshots[0].document), "utf8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible();
  await page.getByRole("button", { name: "Close panel" }).click();

  await openAdvancedWorkMode(page);
  await selectWorkModeTab(page, "inquiry");
  const panel = page.locator('[data-panel="inquiry-journey-prototype"]');
  await panel.locator('input[type="file"]').setInputFiles(inquiryPath);
  await expect(panel.getByText("Inquiry file imported. You can continue the inquiry.")).toBeVisible();

  const scope = panel.getByTestId("inquiry-export-scope");
  const scopeSelect = scope.getByRole("combobox", { name: "Include in the inquiry file" });
  await expect(scope).toContainText("SafeMode text masking is not applied");
  await scopeSelect.selectOption("round-r3-1");
  await expect(scope).toContainText("The source inquiry is unchanged.");

  const partialDownloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save inquiry file" }).click();
  const partialDownload = await partialDownloadPromise;
  expect(partialDownload.suggestedFilename()).toMatch(/-round-r3-1\.kj-atlas-inquiry\.json$/);
  const partialPath = testInfo.outputPath("partial-inquiry.kj-atlas-inquiry.json");
  await partialDownload.saveAs(partialPath);
  const partial = await parseInquiryBundleJson(await readFile(partialPath, "utf8"));
  expect(partial.ok).toBe(true);
  if (!partial.ok) return;
  expect(partial.bundle.journey.roundRecords.map((round) => round.roundId)).toEqual([
    "round-r2-1",
    "round-r3-1",
  ]);
  expect(partial.bundle.snapshots.map((snapshot) => snapshot.snapshotId)).toEqual([
    "snapshot-origin",
    "snapshot-r2-1",
    "snapshot-r3-1",
  ]);
  await expect(panel.getByText("A derived file through the selected round was saved.", { exact: false })).toBeVisible();

  await scopeSelect.selectOption("");
  const fullDownloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save inquiry file" }).click();
  const fullPath = testInfo.outputPath("full-inquiry.kj-atlas-inquiry.json");
  await (await fullDownloadPromise).saveAs(fullPath);
  const full = await parseInquiryBundleJson(await readFile(fullPath, "utf8"));
  expect(full.ok).toBe(true);
  if (!full.ok) return;
  expect(full.bundle.journey.roundRecords).toHaveLength(3);

  await scopeSelect.selectOption("round-r3-1");
  const shareDownloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save SafeMode share copy" }).click();
  const shareDownload = await shareDownloadPromise;
  expect(shareDownload.suggestedFilename()).toMatch(
    /-round-r3-1\.safe-share\.kj-atlas-inquiry\.json$/,
  );
  const sharePath = testInfo.outputPath("safe-share-inquiry.kj-atlas-inquiry.json");
  await shareDownload.saveAs(sharePath);
  const shareRaw = await readFile(sharePath, "utf8");
  const shared = await parseInquiryBundleJson(shareRaw);
  expect(shared.ok).toBe(true);
  if (!shared.ok) return;
  expect(shared.bundle.exportInfo).toEqual({
    scope: "round",
    selectedRoundId: "round-r3-1",
    safeModeApplied: true,
  });
  expect(shareRaw).toContain("[REDACTED]");
  expect(shareRaw).not.toContain("受付開始直後に来庁者が同じ質問を三度尋ねた");
  await panel.locator('input[type="file"]').setInputFiles(sharePath);
  await expect(panel.getByTestId("inquiry-export-info")).toContainText(
    "SafeMode applied; scope ends at round-r3-1",
  );
  expect(await scope.evaluate((element) => element.scrollWidth <= element.clientWidth)).toBe(true);
});
