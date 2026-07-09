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

test("selected cards can be held and given a shared reason without AI", async ({ page }) => {
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
  await bulkBar.getByRole("button", { name: "Change hold state" }).click();

  await bulkBar.getByRole("button", { name: "Add critique reason" }).click();
  const reasonEditor = page.locator('[data-ui-region="bulk-critique-reason"]');
  await expect(reasonEditor).toBeVisible();
  const reasonInput = reasonEditor.getByRole("textbox", { name: "Reason" });
  await reasonInput.fill("Keep both observations together for review.");
  await reasonInput.press("Control+Enter");
  await expect(reasonEditor).toBeHidden();

  await firstCard.click();
  await expect(page.locator("#selected-card-hold-state")).toHaveValue("held");
  await expect(page.locator('textarea[placeholder="Optional feedback about this card"]')).toHaveValue(
    "Keep both observations together for review."
  );
});
