import { expect, test, type Page } from "@playwright/test";

// UX-VISUAL-01 AC-2 (ADR-0048 D1): the in-canvas state legend is default OFF,
// opens from the View panel, and Escape closes it with focus returning to the
// trigger (ADR-0030 contract).

const START_PANEL = '[data-panel="start-document-entry"]';
const LEGEND = '[data-ui-region="canvas-legend"]';
const LEGEND_TRIGGER = '[data-focus-return-id="legend-trigger"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Canvas legend fixture",
    createdAt: "2026-07-06T00:00:00.000Z",
    updatedAt: "2026-07-06T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [{ id: "c1", text: "legend fixture card", x: 200, y: 180 }],
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
      headers: { ETag: '"canvas-legend"' },
      body: JSON.stringify(buildDocument()),
    });
  });
}

test("state legend is default hidden, opens from View panel, closes on Escape with focus return", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  // Default OFF (CB-1).
  await expect(page.locator(LEGEND)).toHaveCount(0);

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.locator(LEGEND_TRIGGER).click();

  const legend = page.locator(LEGEND);
  await expect(legend).toBeVisible();
  await expect(legend).toContainText("State legend");
  await expect(legend).toContainText("Fact");
  await expect(legend).toContainText("Unreviewed (top-right dot)");
  await expect(legend).toContainText("Contradicts (dashed)");

  // Escape closes the legend and returns focus to the trigger.
  await legend.getByRole("button", { name: "Close legend" }).press("Escape");
  await expect(legend).toHaveCount(0);
  await expect(page.locator(LEGEND_TRIGGER)).toBeFocused();

  // The trigger reopens it (toggle) and the close button also works.
  await page.locator(LEGEND_TRIGGER).click();
  await expect(legend).toBeVisible();
  await legend.getByRole("button", { name: "Close legend" }).click();
  await expect(legend).toHaveCount(0);
});
