import { expect, test } from "@playwright/test";

test("default workspace foregrounds core actions and keeps advanced content reversible", async ({ page }) => {
  await page.addInitScript(() => {
    window.localStorage.removeItem("kj-atlas.advanced-ui-enabled");
  });
  await page.goto("/");

  const closeStartPanel = page.getByRole("button", { name: /開始パネルを閉じる|Close start panel/ });
  if (await closeStartPanel.isVisible()) {
    await closeStartPanel.click();
  }

  await expect(page.locator('[data-ui-complexity-tier^="core-"]')).toHaveCount(4);
  await expect(page.locator("[data-ui-core-action]")).toHaveCount(4);
  await expect(page.getByRole("button", { name: /新規カード|New card/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /島を作成|Create island/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /削除|Delete/ })).toBeVisible();
  await expect(page.getByRole("button", { name: /保存|Save/ })).toBeVisible();

  const advancedToggle = page.locator('[data-ui-complexity-tier="advanced-disclosure"]');
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toBeVisible();

  await advancedToggle.click();
  await expect(advancedToggle).toHaveAttribute("aria-pressed", "false");
  await expect(page.locator('[data-ui-complexity-tier="advanced-content"]')).toHaveCount(0);
});
