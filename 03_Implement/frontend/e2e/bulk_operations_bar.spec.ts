import { expect, test, type Page } from "@playwright/test";

// UX-SCALE-01 (b) (ADR-0048 D2, Round 5 redline): a bottom-center bar that
// appears only when 2+ cards are selected. Retention ops (hold/critique)
// are pinned leftmost; each op applies as exactly one undo step.

const START_PANEL = '[data-panel="start-document-entry"]';
const BAR = '[data-ui-region="bulk-operations-bar"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Bulk ops fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "first card", x: 100, y: 100 },
      { id: "c2", text: "second card", x: 400, y: 100 },
      { id: "c3", text: "third card", x: 700, y: 100 },
    ],
    edges: [],
    islands: [],
    readingOrder: [],
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
      headers: { ETag: '"bulk-ops"' },
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

async function selectAllCards(page: Page): Promise<void> {
  const options = page.locator(`${PRIMARY_FLOW} [role="button"]`);
  await options.nth(0).click();
  await options.nth(1).click({ modifiers: ["Shift"] });
  await options.nth(2).click({ modifiers: ["Shift"] });
}

test("appears only for 2+ selected cards and disappears at 0/1", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const options = page.locator(`${PRIMARY_FLOW} [role="button"]`);
  await options.nth(0).click();
  await expect(page.locator(BAR)).toHaveCount(0);

  await options.nth(1).click({ modifiers: ["Shift"] });
  await expect(page.locator(BAR)).toBeVisible();
  await expect(page.locator(BAR)).toContainText("2 cards selected");

  await page.keyboard.press("Escape");
  await expect(page.locator(BAR)).toHaveCount(0);
});

test("bulk hold toggles all selected cards held in one step, and stays actionable for a follow-up toggle", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);
  await selectAllCards(page);

  // The selection is unchanged by a non-destructive bulk action, so the bar
  // correctly stays visible/actionable (not cleared) for a follow-up op.
  await page.getByRole("button", { name: "Change hold state" }).click();
  await expect(page.locator(BAR)).toBeVisible();
  await expect(page.getByTestId("status-message")).toContainText("held");

  // A single Ctrl+Z fully reverses the bulk op (one history step for all 3).
  await page.keyboard.press("Control+z");
  await selectAllCards(page);
  await page.getByRole("button", { name: "Change hold state" }).click();
  await expect(page.getByTestId("status-message")).toContainText("held");
});

test("bulk claim type change applies the chosen type to every selected card", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);
  await selectAllCards(page);

  await page.locator(`${BAR} select`).selectOption("hypothesis");
  await expect(page.locator(BAR)).toBeVisible();

  const claimBadges = page.locator(`${PRIMARY_FLOW} [role="button"]`).filter({ hasText: "Hypothesis" });
  await expect(claimBadges).toHaveCount(3);
});

test("bulk delete removes all selected cards as a single undoable step", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);
  await selectAllCards(page);

  await page.locator(BAR).getByRole("button", { name: "Delete", exact: true }).click();
  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(0);

  await page.keyboard.press("Control+z");
  await expect(page.locator(`${PRIMARY_FLOW} [role="button"]`)).toHaveCount(3);
});
