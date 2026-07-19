import { readFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { parseInquiryBundleJson } from "../src/domain/inquiry_bundle_io";

const CREATED_AT = "2026-07-19T00:00:00.000Z";

function createDocument(): DocumentV1 {
  return {
    version: 1,
    id: "doc-inquiry-handoff",
    title: "Entrance observation",
    createdAt: CREATED_AT,
    updatedAt: CREATED_AT,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "card-carry", text: "Visitors pause after reading the sign", x: 100, y: 100 },
      { id: "card-hold", text: "Rain may have affected the observation", x: 300, y: 100 },
    ],
    edges: [],
    islands: [],
  };
}

test("DOMAIN-W-ITERATION-01 reviews one handoff candidate at a time and saves with an unanswered item", async ({ page }, testInfo) => {
  const document = createDocument();
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Close start panel" }).click();
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const chooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const chooser = await chooserPromise;
  await chooser.setFiles({
    name: "handoff-document.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(document), "utf8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible();
  await page.getByRole("button", { name: "Close panel" }).click();

  await page.getByRole("button", { name: "Advanced" }).click();
  await page.getByRole("button", { name: "Work mode" }).click();
  await page.getByRole("tab", { name: "Inquiry" }).click();
  const panel = page.locator('[data-panel="inquiry-journey-prototype"]');
  await panel.getByRole("button", { name: "Start from the current document" }).click();
  await panel.getByRole("button", { name: "Record R1 Problem setting, iteration 1" }).click();

  const summary = panel.getByText("Review handoff", { exact: true });
  await summary.focus();
  await summary.press("Enter");
  const review = panel.getByRole("group", { name: "Review handoff" });
  await expect(review.getByText("Review one candidate at a time. You can save with unanswered candidates.")).toBeVisible();
  await expect(review.getByText("Candidate 1 of 5")).toBeVisible();

  let candidate = review.getByRole("region", { name: "Carry this card forward?" });
  await expect(candidate).toContainText("Visitors pause after reading the sign");
  const adopt = candidate.getByRole("button", { name: "Adopt as is" });
  await adopt.focus();
  await adopt.press("Enter");

  candidate = review.getByRole("region", { name: "Carry this card forward?" });
  await expect(candidate).toBeFocused();
  await expect(candidate).toContainText("Rain may have affected the observation");
  await candidate.getByRole("button", { name: "Hold" }).click();

  candidate = review.getByRole("region", {
    name: "How did the question or understanding change this time?",
  });
  const understanding = candidate.getByLabel("Change in understanding");
  await understanding.fill("The pause appears to begin after the sign is read.");
  await candidate.getByRole("button", { name: "Adopt edited text" }).click();

  candidate = review.getByRole("region", {
    name: "What question or contradiction remains unanswered?",
  });
  await candidate.getByLabel("Unresolved question or contradiction").fill("Does this also happen in fine weather?");
  await candidate.getByRole("button", { name: "Skip" }).click();

  candidate = review.getByRole("region", {
    name: "What should be checked next in the field, sources, interviews, or experiments?",
  });
  await expect(candidate).toBeFocused();
  await expect(candidate.getByRole("status")).toHaveText("Unanswered");
  expect(await review.evaluate((element) => element.getBoundingClientRect().right)).toBeLessThanOrEqual(390);
  await page.screenshot({ path: testInfo.outputPath("handoff-review-390px.png"), fullPage: true });

  await review.getByRole("button", { name: "Save current handoff" }).click();
  await expect(panel.getByText("Answered handoff items were saved.", { exact: false })).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await panel.getByRole("button", { name: "Save inquiry file" }).click();
  const download = await downloadPromise;
  const savedPath = testInfo.outputPath("handoff-partial.kj-atlas-inquiry.json");
  await download.saveAs(savedPath);
  const parsed = await parseInquiryBundleJson(await readFile(savedPath, "utf8"));
  expect(parsed.ok).toBe(true);
  if (!parsed.ok) return;

  const round = parsed.bundle.journey.roundRecords[0];
  expect(round.status).toBe("paused");
  expect(round.handoff).toEqual({
    carryoverRefs: [{
      snapshotId: round.outputSnapshotId,
      kind: "card",
      entityId: "card-carry",
    }],
    heldRefs: [{
      snapshotId: round.outputSnapshotId,
      kind: "card",
      entityId: "card-hold",
    }],
    unresolvedQuestions: [],
    fieldworkRequests: [],
    understandingDelta: "The pause appears to begin after the sign is read.",
  });
  const snapshot = parsed.bundle.snapshots.find((candidateSnapshot) => candidateSnapshot.snapshotId === round.outputSnapshotId);
  expect(snapshot?.document).toMatchObject(document);
});
