import { expect, test, type Page } from "@playwright/test";

// UX-SHORTCUT-01 AC-3 (ADR-0048 D2): Escape closes the topmost focused
// overlay only, one stage at a time, without cascading to clear the
// underlying selection. Each overlay's own Escape handler calls
// preventDefault(), and the shared window-level hotkey listener
// (useHotkeys.ts) bails out on event.defaultPrevented — this is the existing,
// already-correct staging mechanism; this spec locks it in.

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const LEGEND = '[data-ui-region="canvas-legend"]';
const LEGEND_TRIGGER = '[data-focus-return-id="legend-trigger"]';
const PALETTE = '[role="dialog"][aria-label="Search commands"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Escape staging fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "selected card", x: 200, y: 180 }],
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
      headers: { ETag: '"esc-staging"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openSampleAndSelectCard(page: Page): Promise<import("@playwright/test").Locator> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  const card = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "selected card" });
  await card.click();
  await expect(card).toHaveAttribute("aria-pressed", "true");
  return card;
}

test("Escape closes the command palette without clearing the underlying card selection", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  const card = await openSampleAndSelectCard(page);

  await page.keyboard.press("Control+k");
  await expect(page.locator(PALETTE)).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.locator(PALETTE)).toHaveCount(0);
  // Stage 1 only: the palette closed, the card is still selected underneath.
  await expect(card).toHaveAttribute("aria-pressed", "true");
});

test("Escape closes the canvas legend without clearing the underlying card selection", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  const card = await openSampleAndSelectCard(page);

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.locator(LEGEND_TRIGGER).click();
  await expect(page.locator(LEGEND)).toBeVisible();

  await page.keyboard.press("Escape");
  await expect(page.locator(LEGEND)).toHaveCount(0);
  await expect(card).toHaveAttribute("aria-pressed", "true");
});

test("Escape with no overlay open clears the selection (existing baseline behavior)", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  const card = await openSampleAndSelectCard(page);

  await page.keyboard.press("Escape");
  await expect(card).not.toHaveAttribute("aria-pressed", "true");
});
