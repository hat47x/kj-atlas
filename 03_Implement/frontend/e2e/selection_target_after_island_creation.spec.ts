import { expect, test, type Page } from "@playwright/test";
import { buildFirstMeaningfulMapDocument } from "./helpers/product_value_fixtures";

const START_PANEL = '[data-panel="start-document-entry"]';

async function routeSampleDocument(page: Page): Promise<() => void> {
  let sampleEnabled = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(sampleEnabled ? buildFirstMeaningfulMapDocument() : buildFirstMeaningfulMapDocument([])),
    });
  });

  return () => {
    sampleEnabled = true;
  };
}

test("grouping cards makes the new island the only active selection target", async ({ page }) => {
  const enableSample = await routeSampleDocument(page);

  await page.goto("/?locale=en");
  await expect(page.locator(START_PANEL)).toBeVisible();
  enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();

  const firstCard = page.getByRole("option", { name: "first value user problem" });
  const secondCard = page.getByRole("option", { name: "first value observation memo" });
  await firstCard.click();
  await secondCard.click({ modifiers: ["Shift"] });

  const bulkBar = page.locator('[data-ui-region="bulk-operations-bar"]');
  await expect(bulkBar).toBeVisible();
  await bulkBar.getByRole("button", { name: "Create Island" }).click();

  const selectionPanel = page.locator('[data-ui-region="selection-context"]');
  await expect(selectionPanel).toContainText("Island selected");
  await expect(selectionPanel).not.toContainText("Selection: 2 cards selected");
  await expect(selectionPanel).not.toContainText("Selection: 0 cards selected");
  await expect(bulkBar).toBeHidden();
});
