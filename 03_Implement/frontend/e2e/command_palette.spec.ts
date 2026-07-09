import { expect, test, type Page } from "@playwright/test";

// UX-CMDK-01 (ADR-0048 D2, collapse-layer 5): Cmd/Ctrl+K command palette.
// Delegates to existing handlers; no persistent trigger element (CB-1).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const PALETTE = '[role="dialog"][aria-label="Search commands"]';
const PALETTE_INPUT = '[data-command-palette-input="true"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Command palette fixture",
    createdAt: "2026-07-06T00:00:00.000Z",
    updatedAt: "2026-07-06T00:00:00.000Z",
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
      headers: { ETag: '"command-palette"' },
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

test("opens with Ctrl+K, closes with Escape, and returns focus to the pre-open element", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const viewButton = page.getByRole("button", { name: "View", exact: true });
  await viewButton.focus();
  await expect(viewButton).toBeFocused();

  await page.keyboard.press("Control+k");
  const palette = page.locator(PALETTE);
  await expect(palette).toBeVisible();
  await expect(page.locator(PALETTE_INPUT)).toBeFocused();

  await page.keyboard.press("Escape");
  await expect(palette).toHaveCount(0);
  await expect(viewButton).toBeFocused();
});

test("search -> Enter executes New card without leaving the palette's own trigger stuck", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await expect(page.locator(`${PRIMARY_FLOW} [role="option"]`)).toHaveCount(1);

  await page.keyboard.press("Control+k");
  await page.locator(PALETTE_INPUT).fill("New card");
  await page.keyboard.press("Enter");

  await expect(page.locator(PALETTE)).toHaveCount(0);
  await expect(page.locator(`${PRIMARY_FLOW} [role="option"]`)).toHaveCount(2);
});

test("does not open while editing text elsewhere (defers to the OS/browser default)", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const searchInput = page.getByPlaceholder("Search cards");
  await searchInput.click();
  await expect(searchInput).toBeFocused();

  await page.keyboard.press("Control+k");
  await expect(page.locator(PALETTE)).toHaveCount(0);
  // The keystroke was not consumed by the app: it still reached the input's
  // own default handling (no palette, and focus remains in the input).
  await expect(searchInput).toBeFocused();
});

test("shows 'no results' for a query with no matches", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.keyboard.press("Control+k");
  await page.locator(PALETTE_INPUT).fill("zzz-no-such-command-zzz");
  await expect(page.locator(PALETTE)).toContainText("No matching commands");
});

test("pins the retention (hold) command above other commands when a card is selected", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  await page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "existing card" }).click();

  await page.keyboard.press("Control+k");
  const firstOption = page.locator(PALETTE).locator('[role="option"]').first();
  await expect(firstOption).toHaveText(/Change hold state/);
});
