import { expect, test, type Page } from "@playwright/test";
import { buildDomainExpressionDocument, withoutProductValueContent } from "./helpers/product_value_fixtures";

async function routeDomainExpressionFixture(page: Page): Promise<{ enableSample: () => void }> {
  let shouldReturnSample = false;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });

  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    const document = shouldReturnSample
      ? buildDomainExpressionDocument()
      : withoutProductValueContent(buildDomainExpressionDocument());
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: shouldReturnSample ? '"advanced-panel-loaded"' : '"advanced-panel-empty"' },
      body: JSON.stringify(document),
    });
  });

  return {
    enableSample: () => {
      shouldReturnSample = true;
    },
  };
}

test("default workspace foregrounds core actions and keeps advanced content reversible", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  await page.goto("/?locale=en");

  const closeStartPanel = page.getByRole("button", { name: "Close start panel" });
  if (await closeStartPanel.isVisible()) {
    await closeStartPanel.click();
  }

  await expect(page.locator('[data-ui-complexity-tier^="core-"]')).toHaveCount(4);
  await expect(page.locator('[data-ui-core-action="create-card"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="create-island"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="delete-selection"]')).toBeVisible();
  await expect(page.locator('[data-ui-core-action="save"]')).toBeVisible();
  await expect(page.getByRole("button", { name: "New card" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Create Island" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Delete" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Save" })).toBeVisible();

  const advancedToggle = page.getByRole("button", { name: "Advanced" });
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toBeVisible();

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);
});

test("selection context keeps advanced panel extracted behind explicit disclosure", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  const fixture = await routeDomainExpressionFixture(page);

  await page.goto("/?locale=en");
  fixture.enableSample();
  await page.getByRole("button", { name: "Open sample" }).click();
  await page.getByRole("option", { name: "ambiguous target claim" }).click();

  const selectionContext = page.locator('[data-panel="selection-context"]');
  await expect(selectionContext).toBeVisible();
  await expect(selectionContext).toContainText("Card selected");
  await expect(selectionContext).toContainText("Review state: Unreviewed");
  await expect(page.locator('[data-panel-group="advanced"]')).toHaveCount(0);

  const advancedToggle = page.getByRole("button", { name: "Advanced" });
  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "true");

  const advancedPanel = page.locator('[data-panel-group="advanced"]');
  await expect(advancedPanel).toBeVisible();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "false");
  await expect(selectionContext).toContainText("Critique:");

  await advancedPanel.locator("summary").click();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "true");
  await expect(selectionContext).toBeVisible();

  await advancedPanel.locator("summary").click();
  await expect(advancedPanel).toHaveAttribute("aria-expanded", "false");
});
