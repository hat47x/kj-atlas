import JSZip from "jszip";
import { expect, test, type Download, type Page } from "@playwright/test";
import { continueThroughPreShareGateIfPresent } from "./helpers/i18n";

// SOCIAL-DIFFUSION-01 (ADR-0038): multi-reviewer reproducibility — a review
// pack must be read consistently by independent reviewers. Foundation: the
// exported bundle preserves the work-state (確定/保留/未レビュー) of every card
// in its document.json, so a second reviewer re-importing the pack sees the
// same 確定/保留/根拠/未レビュー set.

function buildStateDocument() {
  const now = "2026-08-16T00:00:00.000Z";
  return {
    version: 1,
    id: "doc_e2e_state",
    title: "state preservation fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c-reviewed", text: "reviewed claim", x: 0, y: 0, textReviewed: true },
      { id: "c-held", text: "held observation", x: 200, y: 0, textReviewed: true, holdState: "held" },
      { id: "c-unreviewed", text: "unreviewed note", x: 400, y: 0, textReviewed: false },
    ],
    edges: [],
    islands: [{ id: "i1", cardIds: ["c-reviewed", "c-held", "c-unreviewed"] }],
    readingOrder: ["i1"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

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

test("the exported review pack preserves 確定/保留/未レビュー work-state", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Create new document" }).click();
  await expect(page.locator('[data-panel="start-document-entry"]')).toBeHidden();

  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const fileChooserPromise = page.waitForEvent("filechooser");
  await page.getByRole("button", { name: "Load document.json" }).click();
  const fileChooser = await fileChooserPromise;
  await fileChooser.setFiles({
    name: "state-preservation.json",
    mimeType: "application/json",
    buffer: Buffer.from(JSON.stringify(buildStateDocument()), "utf-8"),
  });
  await page.getByRole("button", { name: "Replace current document" }).click();
  await expect(page.getByText("Replaced the current document")).toBeVisible();
  await page.getByRole("button", { name: "Close panel" }).click();

  // Export the review pack and read its document.json.
  await page.getByRole("button", { name: "Share & Reproduce" }).click();
  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Export bundle (.zip)" }).click();
  await continueThroughPreShareGateIfPresent(page);
  const download = await downloadPromise;
  const zipBuffer = await readDownloadToBuffer(download);
  const zip = await JSZip.loadAsync(zipBuffer);

  const documentFile = Object.values(zip.files).find((file) => file.name.endsWith("document.json"));
  expect(documentFile).toBeDefined();
  const exported = JSON.parse(await documentFile!.async("string"));

  // 確定 / 保留 / 未レビュー are preserved verbatim.
  const reviewed = exported.cards.find((card: { id: string }) => card.id === "c-reviewed");
  const held = exported.cards.find((card: { id: string }) => card.id === "c-held");
  const unreviewed = exported.cards.find((card: { id: string }) => card.id === "c-unreviewed");
  expect(reviewed.textReviewed).toBe(true);
  expect(held.holdState).toBe("held");
  expect(unreviewed.textReviewed).toBe(false);
});
