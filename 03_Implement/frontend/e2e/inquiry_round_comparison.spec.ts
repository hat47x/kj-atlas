import { readFile, writeFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { parseInquiryBundleJson, serializeInquiryBundle } from "../src/domain/inquiry_bundle_io";
import { recordInquiryRound, startInquiryJourney } from "../src/domain/inquiry_journey_session";

const CREATED_AT = "2026-07-18T00:00:00.000Z";

function createDocument(cardText: string): DocumentV1 {
  return {
    version: 1,
    id: "doc-inquiry-comparison",
    title: "Round comparison fixture",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "card-1", text: cardText, x: 100, y: 100, meta: { source: "Field note A-17" } }],
    edges: [],
    islands: [],
    readingOrder: ["card-1"],
  };
}

function sequentialIds(): () => string {
  let value = 0;
  return () => String(++value);
}

test("DOMAIN-W-ITERATION-01 compares rounds and branches from a past result with the keyboard", async ({ page }, testInfo) => {
  const origin = createDocument("Initial observation");
  const situationDocument = createDocument("The sign was visible");
  const ids = sequentialIds();
  let bundle = await startInquiryJourney(origin, { idFactory: ids, now: () => CREATED_AT });
  const first = await recordInquiryRound(bundle, situationDocument, "r2_situation_grasp", {
    idFactory: ids,
    now: () => "2026-07-18T00:01:00.000Z",
  });
  expect(first.ok).toBe(true);
  if (!first.ok) return;
  bundle = first.bundle;
  const second = await recordInquiryRound(bundle, createDocument("The sign was visible but the next action was unclear"), "r3_essence_pursuit", {
    idFactory: ids,
    now: () => "2026-07-18T00:02:00.000Z",
  });
  expect(second.ok).toBe(true);
  if (!second.ok) return;

  const serialized = await serializeInquiryBundle(second.bundle);
  expect(serialized.ok).toBe(true);
  if (!serialized.ok) return;
  const inquiryPath = testInfo.outputPath("round-comparison.kj-atlas-inquiry.json");
  await writeFile(inquiryPath, serialized.json, "utf8");

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const chooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const chooser = await chooserPromise;
  await chooser.setFiles({
    name: "round-comparison-document.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(origin), "utf8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible();
  await page.getByRole("button", { name: "Close panel" }).click();

  await page.getByRole("button", { name: "Advanced" }).click();
  await page.getByRole("button", { name: "Work mode" }).click();
  await page.getByRole("tab", { name: "Inquiry" }).click();
  const panel = page.locator('[data-panel="inquiry-journey-prototype"]');
  await panel.locator('input[type="file"]').setInputFiles(inquiryPath);
  await expect(panel.getByText("Inquiry file imported. You can continue the inquiry.")).toBeVisible();

  const lineageSummary = panel.getByText("Trace a card's sources", { exact: true });
  await lineageSummary.focus();
  await lineageSummary.press("Enter");
  const lineage = panel.getByRole("group", { name: "Trace a card's sources" });
  await expect(lineage.getByLabel("Card to trace")).toHaveValue("card-1");
  await expect(lineage.getByRole("list", { name: "Source cards" }).getByRole("listitem")).toHaveCount(2);
  await expect(lineage.getByText("Source: Field note A-17").first()).toBeVisible();
  await expect(lineage).toContainText("Result from R2 Situation grasp, iteration 1");
  await expect(lineage).toContainText("Inquiry origin");
  await page.screenshot({ path: testInfo.outputPath("lineage-trace-390px.png"), fullPage: true });

  const comparison = panel.getByRole("group", { name: "Compare rounds" });
  const from = comparison.getByLabel("Compare from");
  const to = comparison.getByLabel("Compare to");
  await expect(from).toHaveValue(second.bundle.journey.roundRecords[0].roundId);
  await expect(to).toHaveValue(second.bundle.journey.roundRecords[1].roundId);
  await expect(comparison.getByRole("status")).toContainText("Card changes: 1");
  expect(await comparison.evaluate((element) => element.getBoundingClientRect().right)).toBeLessThanOrEqual(390);

  await from.focus();
  await from.press("End");
  await expect(comparison.getByRole("status")).toContainText("Card changes: 0");
  await from.press("Home");
  await expect(comparison.getByRole("status")).toContainText("Card changes: 1");

  const parent = panel.getByLabel("Start the next record from");
  await expect(parent).toHaveValue(second.bundle.journey.roundRecords[1].roundId);
  await parent.focus();
  await parent.press("Home");
  await expect(parent).toHaveValue(second.bundle.journey.roundRecords[0].roundId);
  await expect(panel.getByText("The original result and current branch will stay unchanged.")).toBeVisible();

  const stage = panel.getByLabel("Stage to explore next");
  await stage.focus();
  await stage.press("Home");
  await stage.press("ArrowDown");
  await expect(stage).toHaveValue("r2_situation_grasp");
  const branchButton = panel.getByRole("button", {
    name: "Restore the selected result and branch as R2 Situation grasp, iteration 2",
  });
  await branchButton.focus();
  await branchButton.press("Enter");
  await expect(panel.getByRole("list", { name: "Inquiry records" }).getByRole("listitem")).toHaveCount(3);
  await expect(panel.getByText("The original result and current branch will stay unchanged.")).toHaveCount(0);
  await expect(panel.getByText("The selected result was restored to the canvas")).toBeVisible();
  await page.screenshot({ path: testInfo.outputPath("branch-created-390px.png"), fullPage: true });

  const downloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save inquiry file" }).click();
  const download = await downloadPromise;
  const savedPath = testInfo.outputPath("branched-inquiry.kj-atlas-inquiry.json");
  await download.saveAs(savedPath);
  const parsed = await parseInquiryBundleJson(await readFile(savedPath, "utf8"));
  expect(parsed.ok).toBe(true);
  if (!parsed.ok) return;

  const branchRound = parsed.bundle.journey.roundRecords[2];
  expect(branchRound.parentRoundIds).toEqual([second.bundle.journey.roundRecords[0].roundId]);
  expect(branchRound.iteration).toBe(2);
  const branchSnapshot = parsed.bundle.snapshots.find(
    (snapshot) => snapshot.snapshotId === branchRound.outputSnapshotId
  );
  expect(branchSnapshot?.document.cards[0].text).toBe("The sign was visible");
  expect(parsed.bundle.journey.headRoundIds).toContain(second.bundle.journey.roundRecords[1].roundId);
  expect(parsed.bundle.journey.headRoundIds).toContain(branchRound.roundId);
  expect(parsed.bundle.journey.defaultHeadRoundId).toBe(branchRound.roundId);

  const undoBranchButton = panel.getByRole("button", { name: "Undo this branch" });
  await undoBranchButton.evaluate((button) => button.focus());
  await page.keyboard.press("Enter");
  await expect(page.getByRole("button", { name: "Work mode", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(panel.getByText("The branch was undone, including the restored canvas and inquiry record.")).toBeVisible();
  await expect(panel.getByRole("list", { name: "Inquiry records" }).getByRole("listitem")).toHaveCount(2);
  await expect(page.getByRole("button", { name: "Redo" })).toBeDisabled();
  await page.screenshot({ path: testInfo.outputPath("branch-undone-390px.png"), fullPage: true });

  const undoneDownloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save inquiry file" }).click();
  const undoneDownload = await undoneDownloadPromise;
  const undonePath = testInfo.outputPath("branch-undone.kj-atlas-inquiry.json");
  await undoneDownload.saveAs(undonePath);
  const undone = await parseInquiryBundleJson(await readFile(undonePath, "utf8"));
  expect(undone.ok).toBe(true);
  if (!undone.ok) return;
  expect(undone.bundle.journey.roundRecords).toHaveLength(2);
  expect(undone.bundle.journey.headRoundIds).toEqual(second.bundle.journey.headRoundIds);
  expect(undone.bundle.journey.defaultHeadRoundId).toBe(second.bundle.journey.defaultHeadRoundId);
});
