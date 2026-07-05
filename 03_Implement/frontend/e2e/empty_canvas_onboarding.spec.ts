import { expect, test, type Page } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';
const EMPTY_CANVAS_HINT = '[data-ui-region="empty-canvas-hint"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildEmptyDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Empty canvas fixture",
    createdAt: "2026-07-04T00:00:00.000Z",
    updatedAt: "2026-07-04T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeEmptyStartupDocument(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"empty-canvas-onboarding"' },
      body: JSON.stringify(buildEmptyDocument()),
    });
  });
}

test("empty canvas hint appears after creating a new document and disappears after the first card", async ({ page }) => {
  await routeEmptyStartupDocument(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: "Create new document" }).click();
  await expect(startPanel).toBeHidden();

  const hint = page.locator(EMPTY_CANVAS_HINT);
  await expect(hint).toBeVisible();
  await expect(hint).toContainText("Start with one card");
  await expect(hint).toContainText("Correctness can wait");
  await expect(hint).toContainText("It is fine to keep it ambiguous");
  await expect(page.locator(PRIMARY_FLOW).getByRole("option")).toHaveCount(0);

  const focusInsideHint = await page.evaluate(() => {
    return Boolean(document.activeElement?.closest('[data-ui-region="empty-canvas-hint"]'));
  });
  expect(focusInsideHint).toBe(false);

  await hint.getByRole("button", { name: "Write first card" }).click();

  await expect(hint).toHaveCount(0);
  await expect(page.locator(PRIMARY_FLOW).getByRole("option")).toHaveCount(1);

  await page.getByRole("button", { name: "New", exact: true }).click();
  await expect(page.locator(PRIMARY_FLOW).getByRole("option")).toHaveCount(0);
  await expect(hint).toHaveCount(0);

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.getByRole("button", { name: "Show empty canvas tips again" }).click();

  await expect(hint).toBeVisible();
  await expect(page.getByTestId("status-message")).toContainText("Empty canvas tips will appear again");
});
