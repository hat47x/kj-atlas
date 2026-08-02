import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

const DOCUMENT = {
  version: 1,
  id: "doc_unreviewed_card_accessibility",
  title: "Unreviewed card accessibility fixture",
  createdAt: "2026-08-02T00:00:00.000Z",
  updatedAt: "2026-08-02T00:00:00.000Z",
  transform: { panX: 0, panY: 0, zoom: 1 },
  cards: [
    {
      id: "unreviewed-card",
      text: "unreviewed card body",
      x: 180,
      y: 160,
      textReviewed: false,
    },
  ],
  edges: [],
  islands: [],
  narratives: [],
  evidenceLinks: [],
  readingOrder: [],
};

async function routeFixture(page: Page): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"unreviewed-card-accessibility"' },
      body: JSON.stringify(DOCUMENT),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

test("unreviewed state is a stable description, not part of the card or editor name", async ({ page }) => {
  await routeFixture(page);
  await page.goto("/?locale=en");
  await page.getByRole("button", { name: "Open sample" }).click();

  const card = page.getByRole("button", { name: "unreviewed card body", exact: true });
  await expect(card).toBeVisible();
  await expect(card).toHaveAccessibleName("unreviewed card body");
  await expect(card).toHaveAccessibleDescription("Card text is unreviewed");

  await card.dblclick();
  const editor = page.getByRole("textbox", { name: "Edit card text", exact: true });
  await expect(editor).toHaveAccessibleName("Edit card text");
  await expect(editor).toHaveAccessibleDescription("Card text is unreviewed");

  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
