import { expect, test, type Page } from "@playwright/test";

const LEGACY_IMAGE_URL = "https://images.example.test/sensitive-island.png";

function buildDocument() {
  return {
    version: 1,
    id: "doc_legacy_island_image",
    title: "Legacy island image safety fixture",
    createdAt: "2026-07-18T00:00:00.000Z",
    updatedAt: "2026-07-18T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "External image boundary", x: 200, y: 180, textReviewed: true }],
    edges: [],
    islands: [{
      id: "island-image",
      title: "External image island",
      cardIds: ["c1"],
      imageUrl: LEGACY_IMAGE_URL,
      imageReviewed: true,
    }],
    readingOrder: ["island-image", "c1"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"legacy-island-image"' },
      body: JSON.stringify(buildDocument()),
    });
  });
}

test("SafeMode does not request a legacy island image from canvas or details", async ({ page }) => {
  let externalImageRequestCount = 0;
  await page.route("https://images.example.test/**", async (route) => {
    externalImageRequestCount += 1;
    await route.abort();
  });
  await routeDocument(page);

  await page.goto("/?locale=en");
  const startPanel = page.locator('[data-panel="start-document-entry"]');
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  await expect(page.getByRole("button", { name: "External image boundary", exact: true })).toBeVisible();
  const islandSelect = page.getByRole("button", { name: "Select island island-image" });
  await islandSelect.focus();
  await islandSelect.press("Enter");
  await expect(page.getByRole("status").filter({ hasText: "SafeMode is on" }))
    .toContainText("SafeMode is on, so the external image is not loaded.");
  await expect(page.locator(`img[src="${LEGACY_IMAGE_URL}"]`)).toHaveCount(0);

  const imageUrlInput = page.locator('input[type="url"]');
  const imageReviewedCheckbox = imageUrlInput.locator('xpath=following-sibling::label[1]//input[@type="checkbox"]');
  await expect(imageUrlInput).toHaveValue(LEGACY_IMAGE_URL);
  await expect(imageReviewedCheckbox).toBeChecked();
  await imageUrlInput.fill("https://images.example.test/replacement.png");
  await expect(imageReviewedCheckbox).not.toBeChecked();
  await page.waitForTimeout(250);

  expect(externalImageRequestCount).toBe(0);
});
