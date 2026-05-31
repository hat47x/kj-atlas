import { expect, test, type Locator, type Page } from "@playwright/test";
import {
  START_PANEL_IMPORT_PACK,
  START_PANEL_LOAD_DOCUMENT,
  START_PANEL_NEW_DOCUMENT,
  START_PANEL_SAMPLE,
  START_PANEL_TITLE,
} from "./helpers/i18n";

async function activeElementSummary(page: Page): Promise<string> {
  return page.evaluate(() => {
    const active = document.activeElement;
    if (!active) {
      return "(none)";
    }

    const text = (active.textContent ?? "").replace(/\s+/g, " ").trim();
    const label = active.getAttribute("aria-label") ?? "";
    return `${active.tagName.toLowerCase()} ${label} ${text}`.trim();
  });
}

async function pressTabUntilFocused(page: Page, target: Locator, maxTabs = 50): Promise<void> {
  for (let index = 0; index < maxTabs; index += 1) {
    if (await target.evaluate((node) => document.activeElement === node).catch(() => false)) {
      return;
    }
    await page.keyboard.press("Tab");
  }

  throw new Error(`Target was not reachable with Tab. Active element: ${await activeElementSummary(page)}`);
}

const viewports = [
  { width: 960, height: 720 },
  { width: 390, height: 720 },
] as const;

for (const viewport of viewports) {
  test(`first-run start panel exposes core document entry actions at ${viewport.width}px`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/?locale=ja");

    const panel = page.locator('[data-ui-region="start-panel"]');
    await expect(panel).toBeVisible();
    await expect(panel.getByRole("heading", { name: START_PANEL_TITLE })).toBeVisible();
    await expect(panel.getByRole("button", { name: START_PANEL_NEW_DOCUMENT })).toBeVisible();
    await expect(panel.getByRole("button", { name: START_PANEL_SAMPLE })).toBeVisible();
    await expect(panel.getByRole("button", { name: START_PANEL_LOAD_DOCUMENT })).toBeVisible();
    await expect(panel.getByRole("button", { name: START_PANEL_IMPORT_PACK })).toBeVisible();
    await expect(panel.getByText(/安全状態: セーフモード: ON|Safety state: SafeMode: ON/)).toBeVisible();

    const metrics = await page.evaluate(() => ({
      scrollWidth: document.documentElement.scrollWidth,
      viewportWidth: window.innerWidth,
    }));
    expect(metrics.scrollWidth).toBe(metrics.viewportWidth);

    const newDocumentButton = panel.getByRole("button", { name: START_PANEL_NEW_DOCUMENT });
    await pressTabUntilFocused(page, newDocumentButton);
    await expect(newDocumentButton).toBeFocused();

    await panel.getByRole("button", { name: /閉じる|Close/ }).click();
    await expect(panel).toBeHidden();
  });
}
