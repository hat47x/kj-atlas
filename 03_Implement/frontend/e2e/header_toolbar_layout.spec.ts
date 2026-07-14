import { expect, test, type Page } from "@playwright/test";
import { SHARE_REPRODUCE_BUTTON, VIEW_BUTTON } from "./helpers/i18n";

const SHORTCUT_HELP_BUTTON = /Keyboard shortcuts|ショートカット一覧/;
const SHORTCUT_HELP_DIALOG = '[data-ui-region="shortcut-cheatsheet-backdrop"] [role="dialog"]';

type Box = {
  bottom: number;
  height: number;
  right: number;
  text: string;
  width: number;
  x: number;
  y: number;
};

const checkedViewports = [
  { width: 1440, height: 900 },
  { width: 1280, height: 720 },
  { width: 920, height: 720 },
  { width: 768, height: 720 },
  { width: 390, height: 720 },
] as const;

const keyboardViewports = [
  { width: 1440, height: 900 },
  { width: 768, height: 720 },
  { width: 390, height: 720 },
] as const;

async function collectHeaderButtons(page: Page): Promise<Box[]> {
  return page.locator("header button").evaluateAll((nodes) =>
    nodes.map((node) => {
      const rect = node.getBoundingClientRect();
      return {
        text: (node.textContent ?? "").replace(/\s+/g, " ").trim(),
        x: rect.x,
        y: rect.y,
        right: rect.right,
        bottom: rect.bottom,
        width: rect.width,
        height: rect.height,
      };
    })
  );
}

async function collectFixedPanels(page: Page): Promise<Box[]> {
  return page.locator("body *").evaluateAll((nodes) =>
    nodes
      .map((node) => {
        const rect = node.getBoundingClientRect();
        const style = getComputedStyle(node);
        return {
          text: (node.textContent ?? "").replace(/\s+/g, " ").trim(),
          x: rect.x,
          y: rect.y,
          right: rect.right,
          bottom: rect.bottom,
          width: rect.width,
          height: rect.height,
          position: style.position,
        };
      })
      .filter((entry) => entry.position === "fixed" && entry.width > 0 && entry.height > 0)
  );
}

for (const viewport of checkedViewports) {
  test(`header toolbar stays readable at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await page.waitForSelector("header");

    const headerBox = await page.locator("header").boundingBox();
    expect(headerBox).not.toBeNull();
    const headerBottom = headerBox!.y + headerBox!.height;

    const viewportMetrics = await page.evaluate(() => ({
      bodyMargin: getComputedStyle(document.body).margin,
      scrollWidth: document.documentElement.scrollWidth,
    }));
    expect(viewportMetrics.bodyMargin).toBe("0px");
    expect(viewportMetrics.scrollWidth).toBe(viewport.width);

    const buttons = await collectHeaderButtons(page);
    const offscreen = buttons.filter((entry) => entry.x < 0 || entry.right > viewport.width).map((entry) => entry.text);
    const verticalish = buttons.filter((entry) => entry.height > 44 || (entry.width > 0 && entry.height / entry.width > 1.2)).map((entry) => entry.text);
    expect(offscreen).toEqual([]);
    expect(verticalish).toEqual([]);

    await page.getByRole("button", { name: VIEW_BUTTON }).click();
    const viewPanels = await collectFixedPanels(page);
    expect(viewPanels.length).toBeGreaterThan(0);
    expect(viewPanels.some((panel) => panel.y < headerBottom)).toBe(false);
    await page.getByRole("button", { name: VIEW_BUTTON }).click();

    await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
    const shareDialog = page.locator('[data-panel="share-replay"]');
    await expect(shareDialog).toContainText(/共有前チェック|Preflight check/);
    await expect(shareDialog).toContainText(/未レビュー情報|Unreviewed content/);
    await expect(shareDialog).toContainText(/出力形式|Output formats/);
    const sharePanels = await collectFixedPanels(page);
    expect(sharePanels.length).toBeGreaterThan(0);
    expect(sharePanels.some((panel) => panel.y < headerBottom)).toBe(false);
    expect(sharePanels.some((panel) => panel.bottom > viewport.height || panel.right > viewport.width)).toBe(false);
  });
}

for (const viewport of keyboardViewports) {
  test(`header panels support keyboard focus and Escape return at ${viewport.width}x${viewport.height}`, async ({ page }) => {
    await page.setViewportSize(viewport);
    await page.goto("/");
    await page.waitForSelector("header");

    const viewButton = page.getByRole("button", { name: VIEW_BUTTON });
    await viewButton.focus();
    await expect(viewButton).toBeFocused();
    await page.keyboard.press("Enter");

    const viewDialog = page.locator('[data-panel="view"]');
    await expect(viewDialog).toBeVisible();
    await expect(viewDialog).toBeFocused();
    let panels = await collectFixedPanels(page);
    expect(panels.some((panel) => panel.bottom > viewport.height || panel.right > viewport.width)).toBe(false);

    await page.keyboard.press("Tab");
    await page.keyboard.press("Escape");
    await expect(viewDialog).toBeHidden();
    await expect(viewButton).toBeFocused();

    const shareButton = page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON });
    await shareButton.focus();
    await expect(shareButton).toBeFocused();
    await page.keyboard.press("Enter");

    const shareDialog = page.locator('[data-panel="share-replay"]');
    await expect(shareDialog).toBeVisible();
    await expect(shareDialog).toBeFocused();
    panels = await collectFixedPanels(page);
    expect(panels.some((panel) => panel.bottom > viewport.height || panel.right > viewport.width)).toBe(false);

    await page.keyboard.press("Tab");
    await page.keyboard.press("Escape");
    await expect(shareDialog).toBeHidden();
    await expect(shareButton).toBeFocused();

    // UX-MENU-01: "Keyboard shortcuts" moved from a standalone header button
    // into the MenuBar's View category (menuitem "view-shortcut-cheatsheet",
    // App.tsx). Below 768px the 6 categories collapse into a single "Menu"
    // trigger whose dropdown flattens every category's items into one list
    // (no separate "View" entry to open first); at 768px and up, "View" is
    // its own top-level category with its own dropdown.
    const isCollapsed = viewport.width < 768;
    const menuTrigger = isCollapsed
      ? page.getByRole("menuitem", { name: /^Menu$|^メニュー$/ })
      : page.getByRole("menuitem", { name: VIEW_BUTTON });
    await menuTrigger.focus();
    await expect(menuTrigger).toBeFocused();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("menu")).toBeVisible();
    await page.getByRole("menuitem", { name: SHORTCUT_HELP_BUTTON }).click();

    const shortcutHelpDialog = page.locator(SHORTCUT_HELP_DIALOG);
    await expect(shortcutHelpDialog).toBeVisible();
    await expect(shortcutHelpDialog).toContainText(SHORTCUT_HELP_BUTTON);
    panels = await collectFixedPanels(page);
    expect(panels.some((panel) => panel.bottom > viewport.height || panel.right > viewport.width)).toBe(false);

    await page.keyboard.press("Escape");
    await expect(shortcutHelpDialog).toBeHidden();
    await expect(menuTrigger).toBeFocused();
  });
}

test("modifier shortcuts update visible view and hierarchy state", async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto("/");
  await page.waitForSelector("header");

  const reviewModeButton = page.locator('header button[title*="Ctrl+2"]');
  const summaryModeButton = page.locator('header button[title*="Ctrl+3"]');

  await page.keyboard.press("Control+2");
  await expect(reviewModeButton).toHaveAttribute("aria-pressed", "true");

  await page.keyboard.press("Control+3");
  await expect(summaryModeButton).toHaveAttribute("aria-pressed", "true");

  await page.getByRole("button", { name: VIEW_BUTTON }).click();
  const viewDialog = page.locator('[data-panel="view"]');
  await expect(viewDialog).toBeVisible();
  const hierarchySelect = viewDialog.locator("select").first();

  await page.keyboard.down("Alt");
  await page.keyboard.down("Shift");
  await page.keyboard.press("1");
  await page.keyboard.up("Shift");
  await page.keyboard.up("Alt");
  await expect(hierarchySelect).toHaveValue("overview");

  await page.keyboard.down("Alt");
  await page.keyboard.down("Shift");
  await page.keyboard.press("2");
  await page.keyboard.up("Shift");
  await page.keyboard.up("Alt");
  await expect(hierarchySelect).toHaveValue("mid");

  await page.keyboard.down("Alt");
  await page.keyboard.down("Shift");
  await page.keyboard.press("3");
  await page.keyboard.up("Shift");
  await page.keyboard.up("Alt");
  await expect(hierarchySelect).toHaveValue("detail");
});
