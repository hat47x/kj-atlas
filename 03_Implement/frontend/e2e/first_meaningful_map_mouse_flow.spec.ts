import { expect, test, type Page } from "@playwright/test";

const START_PANEL = '[data-panel="start-document-entry"]';

function buildDocument(cardTexts: string[]) {
  const now = "2026-06-04T00:00:00.000Z";
  return {
    version: 2,
    id: "doc_first_meaningful_map_mouse",
    title: "First meaningful map mouse fixture",
    createdAt: now,
    updatedAt: now,
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: cardTexts.map((text, index) => ({
      id: `mouse-value-card-${index + 1}`,
      text,
      x: 140 + index * 270,
      y: 150 + (index % 2) * 150,
      textReviewed: index === 0,
    })),
    edges: [],
    islands: [],
    readingOrder: ["mouse-value-card-1", "mouse-value-card-2", "mouse-value-card-3"],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeFirstValueFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const document = shouldReturnSample
      ? buildDocument(["first value user problem", "first value observation memo", "first value decision anchor"])
      : buildDocument([]);

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"first-value-sample-loaded"' : '"first-value-sample-empty"' },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

test("mouse first-value flow creates a visible first island from the sample", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  const fixture = await routeFirstValueFixture(page);

  await page.goto("/?locale=ja");
  await expect(page.locator(START_PANEL)).toBeVisible();

  fixture.enableSample();
  await page.getByRole("button", { name: /サンプルを開く|Open sample/ }).click();
  await expect(page.locator(START_PANEL)).toBeHidden();

  const firstCard = page.getByRole("option", { name: "first value user problem" });
  const secondCard = page.getByRole("option", { name: "first value observation memo" });
  await expect(firstCard).toBeVisible();
  await expect(secondCard).toBeVisible();

  await firstCard.click();
  await expect(firstCard).toHaveAttribute("aria-selected", "true");
  await secondCard.click({ modifiers: ["Shift"] });
  await expect(firstCard).toHaveAttribute("aria-selected", "true");
  await expect(secondCard).toHaveAttribute("aria-selected", "true");

  const createIslandButton = page.getByRole("button", { name: /島を作成|Create Island/ });
  await expect(createIslandButton).toBeEnabled();
  await createIslandButton.click();

  const islandSelect = page.getByRole("button", { name: /島 .* を選択|Select island/ });
  await expect(islandSelect).toBeVisible();

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toBeVisible();
  await expect(selectionPanel).toContainText(/島を選択中|Island selected/);
  await expect(selectionPanel).toContainText("Island 1");
  await expect(selectionPanel).toContainText("first value user problem");
  await expect(selectionPanel).toContainText("first value observation memo");
  await expect(selectionPanel).toContainText(/選択: 2 件のカードを選択中|Selection: 2 cards selected/);
});
