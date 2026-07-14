import { expect, test, type Page } from "@playwright/test";

// UX-VISUAL-01 (ADR-0048 D1): card state badges must live in a normal-flow meta-row
// ABOVE the body so the body first line is never overlapped.

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const META_ROW = "[data-card-meta-row]";

const BODY = "検証中の主張。文頭が読めること。";

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Card meta-row fixture",
    createdAt: "2026-07-05T00:00:00.000Z",
    updatedAt: "2026-07-05T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      {
        id: "c-meta",
        text: BODY,
        x: 220,
        y: 200,
        claimType: "claim",
        holdState: "held",
        textReviewed: false,
        critique: "採用前に確認が必要",
        critiqueTags: ["feels_off"],
      },
    ],
    edges: [],
    islands: [],
    readingOrder: ["c-meta"],
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
      headers: { ETag: '"card-meta-row"' },
      body: JSON.stringify(buildDocument()),
    });
  });
}

test("card state badges render in a meta-row above the body, not overlapping the first line", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  const card = page.locator(`${PRIMARY_FLOW} [role="button"]`).first();
  await expect(card).toBeVisible();
  // Body text is fully present (not clipped/covered by badges).
  await expect(card).toContainText(BODY);

  const metaRow = card.locator(META_ROW);
  await expect(metaRow).toBeVisible();

  const cardBox = await card.boundingBox();
  const rowBox = await metaRow.boundingBox();
  expect(cardBox).not.toBeNull();
  expect(rowBox).not.toBeNull();
  if (cardBox && rowBox) {
    // The meta-row is a small band at the TOP of the card...
    expect(rowBox.y - cardBox.y).toBeLessThan(24);
    // ...occupying only a thin band (badges do not cover the whole body).
    expect(rowBox.height).toBeLessThan(40);
    // ...and the card is tall enough to hold the body below the meta-row.
    expect(cardBox.height).toBeGreaterThan(rowBox.height + 20);
  }
});
