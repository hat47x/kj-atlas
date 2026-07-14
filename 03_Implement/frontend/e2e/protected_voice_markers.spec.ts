import { expect, test, type Page } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_protected_voice_markers",
    title: "Protected voice marker fixture",
    createdAt: "2026-07-08T00:00:00.000Z",
    updatedAt: "2026-07-08T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "lone", text: "Lone wolf card", x: 160, y: 160, textReviewed: true },
      { id: "small-a", text: "Small island A", x: 480, y: 160, textReviewed: true },
      { id: "small-b", text: "Small island B", x: 740, y: 160, textReviewed: true },
      { id: "critique", text: "Singleton critique card", x: 160, y: 360, textReviewed: true, critiqueTags: ["feels_off"] },
    ],
    edges: [],
    islands: [
      { id: "small-island", title: "Small island", cardIds: ["small-a", "small-b"] },
    ],
    readingOrder: ["lone", "small-a", "small-b", "critique"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"protected-voice-markers"' },
      body: JSON.stringify(buildDocument()),
    });
  });
}

test("protected voice markers are visible by default and can be hidden from View controls", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  await expect(page.getByText("Protected", { exact: true })).toHaveCount(3);
  await expect(page.getByText(/score|rank|ratio/i)).toHaveCount(0);

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.getByRole("button", { name: "Hide protection marks" }).click();

  await expect(page.getByText("Protected", { exact: true })).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Show protection marks" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Lone wolf card" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Small island A" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Small island B" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Singleton critique card" })).toBeVisible();
});
