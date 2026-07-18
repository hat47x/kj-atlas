import { writeFile } from "node:fs/promises";
import { expect, test } from "@playwright/test";

import type { DocumentV1 } from "../src/domain/types";
import { serializeInquiryBundle } from "../src/domain/inquiry_bundle_io";
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
    cards: [{ id: "card-1", text: cardText, x: 100, y: 100 }],
    edges: [],
    islands: [],
    readingOrder: ["card-1"],
  };
}

function sequentialIds(): () => string {
  let value = 0;
  return () => String(++value);
}

test("DOMAIN-W-ITERATION-01 compares repeated rounds with keyboard-operable selectors", async ({ page }, testInfo) => {
  const origin = createDocument("The sign was visible");
  const ids = sequentialIds();
  let bundle = await startInquiryJourney(origin, { idFactory: ids, now: () => CREATED_AT });
  const first = await recordInquiryRound(bundle, origin, "r2_situation_grasp", {
    idFactory: ids,
    now: () => "2026-07-18T00:01:00.000Z",
  });
  expect(first.ok).toBe(true);
  if (!first.ok) return;
  bundle = first.bundle;
  const second = await recordInquiryRound(bundle, createDocument("The sign was visible but the next action was unclear"), "r2_situation_grasp", {
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
});
