import { expect, test, type Page } from "@playwright/test";
import { EXPORT_BUNDLE_BUTTON, SHARE_REPRODUCE_BUTTON } from "./helpers/i18n";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

// UX-SHARE-01 (ADR-0048 憲章・反スコアリング): pre-share summary gate.
// Covers: counts + back/continue shown before export (AC-1), no scoring
// language (AC-2), existing preflight non-regression (AC-3), focus
// contract (AC-4), and zero-count skip (AC-5).

const START_PANEL = '[data-panel="start-document-entry"]';

async function routeDomainExpressionFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/*", async (route) => {
    const document = shouldReturnSample
      ? buildDomainExpressionDocument()
      : withoutProductValueContent(buildDomainExpressionDocument());
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"pre-share-gate-loaded"' : '"pre-share-gate-empty"' },
      body: JSON.stringify(document),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

async function openSampleAndShare(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
}

test("shows unreviewed/critique/contradiction counts with back/continue, and never a score or percentage", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await openSampleAndShare(page);

  await page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();

  const gate = page.locator('[data-panel="pre-share-summary-gate"]');
  await expect(gate).toBeVisible();
  await expect(gate).toContainText(/unreviewed/i);
  await expect(gate).toContainText(/critique/i);
  await expect(gate).toContainText(/contradiction/i);
  await expect(gate).toContainText(/SafeMode/);

  const gateText = (await gate.textContent()) ?? "";
  expect(gateText).not.toMatch(/score|readiness|\d+%/i);

  await expect(page.getByRole("button", { name: "Go back and review" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Continue" })).toBeVisible();
});

test("Back closes the gate without exporting and returns focus to the export button (AC-4)", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await openSampleAndShare(page);

  const exportButton = page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON });
  await exportButton.click();

  const gate = page.locator('[data-panel="pre-share-summary-gate"]');
  await expect(gate).toBeVisible();
  await expect(gate).toBeFocused();

  const downloadEvents: string[] = [];
  page.on("download", (download) => downloadEvents.push(download.suggestedFilename()));

  await page.getByRole("button", { name: "Go back and review" }).click();
  await expect(gate).toBeHidden();
  await expect(exportButton).toBeFocused();
  expect(downloadEvents).toHaveLength(0);
});

test("Escape closes the gate the same way as Back (AC-4)", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await openSampleAndShare(page);

  const exportButton = page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON });
  await exportButton.click();

  const gate = page.locator('[data-panel="pre-share-summary-gate"]');
  await expect(gate).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(gate).toBeHidden();
  await expect(exportButton).toBeFocused();
});

test("Continue proceeds with the export exactly as before", async ({ page }) => {
  const fixture = await routeDomainExpressionFixture(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  fixture.enableSample();
  await openSampleAndShare(page);

  await page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();
  const gate = page.locator('[data-panel="pre-share-summary-gate"]');
  await expect(gate).toBeVisible();

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: "Continue" }).click();
  const download = await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/\.zip$/);
  await expect(gate).toBeHidden();
});

test("skips the gate entirely when the document has zero unreviewed/critique/contradiction items (AC-5)", async ({ page }) => {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"pre-share-gate-clean"' },
      body: JSON.stringify({
        version: 2,
        id: "doc_phase1_canvas",
        title: "clean fixture",
        createdAt: "2026-07-09T00:00:00.000Z",
        updatedAt: "2026-07-09T00:00:00.000Z",
        transform: { panX: 0, panY: 0, zoom: 1 },
        cards: [{ id: "c1", text: "a fully reviewed card", x: 0, y: 0, textReviewed: true }],
        edges: [],
        islands: [],
        readingOrder: [],
        narratives: [],
        evidenceLinks: [],
        mergeSuggestionDecisions: [],
      }),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSampleAndShare(page);

  const downloadPromise = page.waitForEvent("download");
  await page.getByRole("button", { name: EXPORT_BUNDLE_BUTTON }).click();
  await downloadPromise;

  await expect(page.locator('[data-panel="pre-share-summary-gate"]')).toHaveCount(0);
});
