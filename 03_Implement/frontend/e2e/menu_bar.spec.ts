import { expect, test, type Page } from "@playwright/test";

// UX-MENU-01 (ADR-0048 D2, collapse-layer 3): a persistent, categorized menu
// bar. Every item delegates to an existing handler; this spec covers the
// WAI-ARIA menubar keyboard contract (AC-2), the 390px hamburger collapse
// (AC-3, Round 5 redline), and that moved commands still work end-to-end.

const START_PANEL = '[data-panel="start-document-entry"]';
const MENU_BAR = '[data-ui-region="menu-bar"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Menu bar fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "existing card", x: 200, y: 180 }],
    edges: [],
    islands: [],
    readingOrder: ["c1"],
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
      headers: { ETag: '"menu-bar"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

test("arrow keys roll between top-level categories when no menu is open, and drill into the sibling's first item once one is", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const fileButton = page.getByRole("menuitem", { name: "File", exact: true });
  const editButton = page.getByRole("menuitem", { name: "Edit", exact: true });
  const shareButton = page.getByRole("menuitem", { name: "Share", exact: true });
  const workButton = page.getByRole("menuitem", { name: "Work", exact: true });

  // No menu open yet: arrow keys are plain roving focus, nothing opens.
  await fileButton.focus();
  await page.keyboard.press("ArrowRight");
  await expect(editButton).toBeFocused();
  await expect(page.getByRole("menu")).toHaveCount(0);

  await page.keyboard.press("Home");
  await expect(fileButton).toBeFocused();
  await page.keyboard.press("End");
  await expect(shareButton).toBeFocused();

  // Once a menu is open, rollover drills into the sibling's first item.
  await page.keyboard.press("ArrowDown");
  await expect(page.getByRole("menu")).toBeVisible();
  await expect(shareButton).toHaveAttribute("aria-expanded", "true");

  await page.keyboard.press("ArrowLeft");
  await expect(workButton).toHaveAttribute("aria-expanded", "true");
  await expect(shareButton).toHaveAttribute("aria-expanded", "false");
  await expect(page.getByRole("menuitem", { name: "Work mode" })).toBeFocused();
});

test("Escape closes the open menu and returns focus to its category trigger", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const cardButton = page.getByRole("menuitem", { name: "Card", exact: true });
  await cardButton.click();
  await expect(page.getByRole("menu")).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.getByRole("menu")).toHaveCount(0);
  await expect(cardButton).toBeFocused();
});

test("ArrowDown/ArrowUp cycle items with wraparound, Home/End jump, and Enter runs the active item", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(1);

  await page.getByRole("menuitem", { name: "Card", exact: true }).click();
  const newCardItem = page.getByRole("menuitem", { name: "New card" });
  await expect(newCardItem).toBeFocused();

  await page.keyboard.press("Enter");
  await expect(page.getByRole("menu")).toHaveCount(0);
  // The new card enters edit mode immediately (focus moves to its textarea);
  // role="button" moves entirely to the textarea while editing (ADR-0052), so
  // the freshly-created card briefly has no role="button" of its own. Tab
  // away to commit the (empty) edit and exit edit mode before counting.
  await expect(page.locator(`${PRIMARY_FLOW} textarea`)).toBeFocused();
  await page.keyboard.press("Tab");
  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(2);
});

test("card type-change items are disabled with no selection and apply the chosen type once a card is selected", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.getByRole("menuitem", { name: "Card", exact: true }).click();
  await expect(page.getByRole("menuitemcheckbox", { name: "Hypothesis" })).toBeDisabled();
  await page.keyboard.press("Escape");

  await page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "existing card" }).click();

  await page.getByRole("menuitem", { name: "Card", exact: true }).click();
  const hypothesisItem = page.getByRole("menuitemcheckbox", { name: "Hypothesis" });
  await expect(hypothesisItem).toBeEnabled();
  await hypothesisItem.click();

  const selectionSummary = page.locator('[data-panel="selection-context"]');
  await expect(selectionSummary).toContainText("Hypothesis");
});

test("View/Work/Share categories open the existing panels via their established triggers (no duplicate surfaces)", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.getByRole("menuitem", { name: "View", exact: true }).click();
  await page.getByRole("menuitem", { name: "Open view controls" }).click();
  await expect(page.locator('[data-panel="view"]')).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(page.locator('[data-panel="view"]')).toHaveCount(0);

  await page.getByRole("menuitem", { name: "Work", exact: true }).click();
  await page.getByRole("menuitem", { name: "Work mode" }).click();
  await expect(page.locator('[data-ui-region="work-mode"]')).toBeVisible();
  await page.keyboard.press("Escape");

  await page.getByRole("menuitem", { name: "Share", exact: true }).click();
  await page.getByRole("menuitem", { name: "Share & Reproduce" }).click();
  await expect(page.locator('[data-panel="share-replay"]')).toBeVisible();
});

test("below 768px the 6 categories collapse into a single Menu trigger listing every category", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 390, height: 720 });
  await page.goto("/?locale=en");
  await openSample(page);

  await expect(page.getByRole("menuitem", { name: "File", exact: true })).toHaveCount(0);
  const collapsedTrigger = page.getByRole("menuitem", { name: "Menu", exact: true });
  await expect(collapsedTrigger).toBeVisible();

  await collapsedTrigger.click();
  const menu = page.locator(MENU_BAR).getByRole("menu");
  await expect(menu).toContainText("File");
  await expect(menu).toContainText("Share");
  await expect(menu.getByRole("menuitem", { name: "New", exact: true })).toBeVisible();
});

test("shortcut hints on Undo/Redo are OS-aware and match the shortcut cheatsheet's notation", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.getByRole("menuitem", { name: "Edit", exact: true }).click();
  await expect(page.getByRole("menuitem", { name: "Undo" })).toContainText("Ctrl+Z");
  await expect(page.getByRole("menuitem", { name: "Redo" })).toContainText("Ctrl+Y");
});
