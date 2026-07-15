import { expect, test, type Page } from "@playwright/test";

// UX-SCALE-01 (c) (ADR-0048 D2, Round 5 redline): island outlines are
// orthogonal, complexity is shown only when non-zero, and "tidy" is a
// human-triggered, one-undo-step re-arrangement (never automatic).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

const CARD_WIDTH = 220;
const CARD_HEIGHT = 80;
const CELL_GAP = 24;
const CELL_W = CARD_WIDTH + CELL_GAP;
const CELL_H = CARD_HEIGHT + CELL_GAP;

function buildDocument() {
  // An L-shaped cluster: row0 has 3 cards (col0..col2), row1 has 1 card
  // (col0) -> exactly one reflex corner (complexity 1).
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Island tidy fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [
      { id: "a", text: "card a", x: 0, y: 0 },
      { id: "b", text: "card b", x: CELL_W, y: 0 },
      { id: "c", text: "card c", x: CELL_W * 2, y: 0 },
      { id: "d", text: "card d", x: 0, y: CELL_H },
    ],
    edges: [],
    islands: [{ id: "isl1", cardIds: ["a", "b", "c", "d"], shape: { kind: "rect" as const } }],
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
      headers: { ETag: '"island-tidy"' },
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

test("shows a non-zero complexity badge for an L-shaped island, and Tidy layout reduces it to 0 as one undo step", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  // The island body is fully covered by its 4 member cards, and the header
  // strip's own background div sits on top of the island's own hit-target
  // element (same z-index, later in DOM order) — but the app's context-menu
  // hit-test is world-coordinate based (App.tsx resolves which island a
  // right-click landed in independently of which DOM node received it), so
  // force the click through Playwright's strict top-element check.
  const island = page.locator(`${PRIMARY_FLOW} [aria-label^="Select island"]`).first();
  const headerPoint = { position: { x: 10, y: 10 }, force: true };

  // Switch the island to a polygon so the orthogonal generator runs (rect
  // shapes have no vertex-count complexity signal by definition).
  await island.click({ button: "right", ...headerPoint });
  await page.getByRole("menuitem", { name: "Resize / edit shape" }).click();
  await page.keyboard.press("Escape");

  const complexityBadge = page.getByTitle(/Outline complexity: 1/);
  await expect(complexityBadge).toBeVisible();
  await expect(complexityBadge).toContainText("Shape: 1");

  await island.click({ button: "right", ...headerPoint });
  await page.getByRole("menuitem", { name: "Tidy layout" }).click();

  await expect(page.getByTestId("status-message")).toContainText("Tidied the island into a denser layout");
  await expect(page.getByTitle(/Outline complexity/)).toHaveCount(0);

  await page.keyboard.press("Control+z");
  await expect(page.getByTitle(/Outline complexity: 1/)).toBeVisible();
});

test("Tidy layout is reachable from the command palette when an island is selected", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");
  await openSample(page);

  // Select the island via the context menu's "Edit island" action (reuses
  // the same reliable world-coordinate-based right-click path as the first
  // test above) rather than a plain click, since the island body is fully
  // covered by its 4 member cards.
  const island = page.locator(`${PRIMARY_FLOW} [aria-label^="Select island"]`).first();
  await island.click({ button: "right", position: { x: 10, y: 10 }, force: true });
  await page.getByRole("menuitem", { name: "Edit island (rename)" }).click();

  await page.keyboard.press("Control+k");
  await page.locator('[data-command-palette-input="true"]').fill("Tidy");
  await expect(page.locator('[role="dialog"][aria-label="Search commands"]')).toContainText("Tidy layout");
  await page.keyboard.press("Enter");

  await expect(page.getByTestId("status-message")).toContainText(/Tidied the island|already arranged/);
});
