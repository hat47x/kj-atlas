import { expect, test, type Page } from "@playwright/test";

// UX-SCALE-01 (a) (ADR-0048 D2, Round 5 redline): a small, corner, collapsible
// overview of the whole document with a draggable current-viewport frame.

const START_PANEL = '[data-panel="start-document-entry"]';
const MINIMAP = '[data-ui-region="minimap"]';

function buildDocument() {
  const cards = [];
  const islands = [];
  for (let i = 0; i < 3; i += 1) {
    const cardIds: string[] = [];
    for (let j = 0; j < 3; j += 1) {
      const id = `c${i}-${j}`;
      cards.push({ id, text: `card ${id}`, x: i * 400 + j * 50, y: i * 200 + j * 30 });
      cardIds.push(id);
    }
    islands.push({ id: `isl${i}`, cardIds });
  }

  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Minimap fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards,
    edges: [],
    islands,
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
      headers: { ETag: '"minimap"' },
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

test("shows a viewport frame and dragging it pans the canvas", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto("/?locale=en");
  await openSample(page);

  const minimap = page.locator(MINIMAP);
  await expect(minimap).toBeVisible();
  await expect(page.locator('[data-testid="minimap-viewport-rect"]')).toBeVisible();

  const box = await minimap.boundingBox();
  if (!box) {
    throw new Error("minimap bounding box not found");
  }

  const firstCard = page.locator('[data-ui-region="primary-flow"] [role="button"]').first();
  const beforeBox = await firstCard.boundingBox();

  await page.mouse.move(box.x + 20, box.y + 20);
  await page.mouse.down();
  await page.mouse.move(box.x + 100, box.y + 80);
  await page.mouse.up();

  const afterBox = await firstCard.boundingBox();
  expect(beforeBox).not.toBeNull();
  expect(afterBox).not.toBeNull();
  expect(afterBox!.x).not.toBeCloseTo(beforeBox!.x, 0);
});

test("collapses and re-expands, and the collapse preference persists across reload", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto("/?locale=en");
  await openSample(page);

  await expect(page.locator(MINIMAP)).toBeVisible();
  await page.getByRole("button", { name: "Collapse minimap" }).click();
  await expect(page.locator(MINIMAP)).toHaveCount(0);
  const expandTrigger = page.getByRole("button", { name: "Expand minimap" });
  await expect(expandTrigger).toBeVisible();

  await page.reload();
  await openSample(page);
  await expect(page.locator(MINIMAP)).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Expand minimap" })).toBeVisible();

  await page.getByRole("button", { name: "Expand minimap" }).click();
  await expect(page.locator(MINIMAP)).toBeVisible();
});

test("collapses automatically below 640px width regardless of the saved preference", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 600, height: 800 });
  await page.goto("/?locale=en");
  await openSample(page);

  await expect(page.locator(MINIMAP)).toHaveCount(0);
  await expect(page.getByRole("button", { name: "Expand minimap" })).toBeVisible();
});
