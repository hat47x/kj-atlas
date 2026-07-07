import { expect, test, type Page } from "@playwright/test";

// UX-SHORTCUT-01 AC-4 (ADR-0048 D2, Round 5 redline): "?" opens the shortcut
// cheatsheet; Escape closes it and restores focus; OS notation is switchable.

const START_PANEL = '[data-panel="start-document-entry"]';
const CHEATSHEET = '[role="dialog"][aria-label="Keyboard shortcuts"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Cheatsheet fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "a card", x: 200, y: 180 }],
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
      headers: { ETag: '"cheatsheet"' },
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

test("opens with '?', closes with Escape, and returns focus to the pre-open element", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const viewButton = page.getByRole("button", { name: "View", exact: true });
  await viewButton.focus();

  await page.keyboard.press("?");
  const cheatsheet = page.locator(CHEATSHEET);
  await expect(cheatsheet).toBeVisible();
  await expect(cheatsheet).toContainText("Toggle hold");
  await expect(cheatsheet).toContainText("These keys are disabled while editing text.");

  await page.keyboard.press("Escape");
  await expect(cheatsheet).toHaveCount(0);
  await expect(viewButton).toBeFocused();
});

test("does not open while editing text elsewhere (defers to the OS/browser default)", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const searchInput = page.getByPlaceholder("Search cards");
  await searchInput.click();
  await searchInput.type("?");

  await expect(page.locator(CHEATSHEET)).toHaveCount(0);
  await expect(searchInput).toHaveValue("?");
});

test("the OS notation switch changes the displayed shortcut symbols", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.keyboard.press("?");
  const cheatsheet = page.locator(CHEATSHEET);
  await expect(cheatsheet).toBeVisible();

  await cheatsheet.getByRole("button", { name: "Mac", exact: true }).click();
  await expect(cheatsheet.getByText("⌘Z", { exact: true })).toBeVisible();

  await cheatsheet.getByRole("button", { name: "Windows/Linux", exact: true }).click();
  await expect(cheatsheet.getByText("Ctrl+Z", { exact: true })).toBeVisible();
});
