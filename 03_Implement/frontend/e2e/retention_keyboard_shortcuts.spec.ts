import { expect, test, type Page } from "@playwright/test";

// UX-SHORTCUT-01 (ADR-0048 D2): retention-system shortcuts (H=hold, U=critique
// quick-flag, R=reviewed) are modifier-less single keys, active only when
// exactly one card is selected, and never fire while editing text.

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Retention shortcuts fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "c1", text: "plain card", x: 200, y: 140, textReviewed: true },
      { id: "c2", text: "card with authored critique", x: 200, y: 320, critique: "This needs more evidence" },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c1", "c2"],
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
      headers: { ETag: '"retention-shortcuts"' },
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

test("H toggles hold, is reversible with Ctrl+Z, and does nothing without a selection", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const card = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "plain card" });

  // No selection: H does nothing (no hold pill appears).
  await page.keyboard.press("h");
  await expect(card.getByText("Held", { exact: true })).toHaveCount(0);

  await card.click();
  await page.keyboard.press("h");
  await expect(card.getByText("Held", { exact: true })).toBeVisible();

  // Toggling again clears it.
  await page.keyboard.press("h");
  await expect(card.getByText("Held", { exact: true })).toHaveCount(0);

  // Reversible via Ctrl+Z.
  await page.keyboard.press("h");
  await expect(card.getByText("Held", { exact: true })).toBeVisible();
  await page.keyboard.press("Control+z");
  await expect(card.getByText("Held", { exact: true })).toHaveCount(0);
});

test("U flags a card with no critique, toggles it off, and never destroys an authored critique", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const plainCard = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "plain card" });
  await plainCard.click();
  await page.keyboard.press("u");
  await expect(plainCard.getByTitle("Card has critique note")).toBeVisible();

  await page.keyboard.press("u");
  await expect(plainCard.getByTitle("Card has critique note")).toHaveCount(0);

  const authoredCard = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "card with authored critique" });
  await authoredCard.click();
  await expect(authoredCard.getByTitle("Card has critique note")).toBeVisible();
  // Safety: U must be a no-op on a card whose critique the user already wrote.
  await page.keyboard.press("u");
  await expect(authoredCard.getByTitle("Card has critique note")).toBeVisible();
});

test("R toggles the reviewed state on the selected card", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const authoredCard = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "card with authored critique" });
  await authoredCard.click();
  await expect(authoredCard.getByTitle("Card text is unreviewed")).toBeVisible();

  await page.keyboard.press("r");
  await expect(authoredCard.getByTitle("Card text is unreviewed")).toHaveCount(0);

  await page.keyboard.press("r");
  await expect(authoredCard.getByTitle("Card text is unreviewed")).toBeVisible();
});

test("retention keys do not fire while editing card text", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  const card = page.locator(`${PRIMARY_FLOW} [role="option"]`, { hasText: "plain card" });
  await card.click();
  await card.dblclick();

  const editor = card.locator("textarea");
  await expect(editor).toBeFocused();
  await editor.press("Control+a");
  await page.keyboard.type("hur");

  await expect(editor).toHaveValue("hur");
  await expect(card.getByText("Held", { exact: true })).toHaveCount(0);
});
