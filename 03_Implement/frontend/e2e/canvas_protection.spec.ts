import { expect, test, type Page } from "@playwright/test";

// UX-VISUAL-02 (ADR-0048 D3): lone-wolf cards and small islands carry a
// deterministic, non-scoring "protection" mark. Default ON, toggleable in the
// View panel, and explained in the legend.

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';
const LEGEND = '[data-ui-region="canvas-legend"]';
const LEGEND_TRIGGER = '[data-focus-return-id="legend-trigger"]';

// A 3-card island (NOT protected), a 2-card small island (protected), and one
// lone-wolf card (protected). Total protected marks = 2 (small island + lone).
function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Protection fixture",
    createdAt: "2026-07-06T00:00:00.000Z",
    updatedAt: "2026-07-06T00:00:00.000Z",
    transform: { panX: 0, panY: 0, zoom: 1 },
    cards: [
      { id: "m1", text: "island member one", x: 120, y: 140 },
      { id: "m2", text: "island member two", x: 360, y: 140 },
      { id: "m3", text: "island member three", x: 120, y: 300 },
      { id: "s1", text: "small island member one", x: 620, y: 140 },
      { id: "s2", text: "small island member two", x: 860, y: 140 },
      { id: "lone", text: "the lone wolf idea", x: 620, y: 360 },
    ],
    edges: [],
    islands: [
      { id: "isl1", title: "big island", cardIds: ["m1", "m2", "m3"] },
      { id: "isl2", title: "small island", cardIds: ["s1", "s2"] },
    ],
    readingOrder: ["m1", "m2", "m3", "s1", "s2", "lone"],
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
      headers: { ETag: '"canvas-protection"' },
      body: JSON.stringify(buildDocument()),
    });
  });
}

test("lone-wolf card shows a non-scoring protection mark that the View panel can hide", async ({ page }) => {
  await routeDocument(page);
  await page.goto("/?locale=en");

  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();

  const loneCard = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "the lone wolf idea" });
  await expect(loneCard).toBeVisible();
  // Island titles are rendered as a text node alongside sibling badges (not
  // their own element), so match by substring rather than exact text.
  await expect(page.getByText("small island").first()).toBeVisible();
  await expect(page.getByText("big island").first()).toBeVisible();

  const allProtectedMarks = page.locator(PRIMARY_FLOW).getByText("Protected", { exact: true });

  // Default ON: exactly 2 marks — the lone-wolf card and the small (2-member)
  // island. The 3-member island carries none.
  await expect(allProtectedMarks).toHaveCount(2);
  const mark = loneCard.getByText("Protected", { exact: true });
  await expect(mark).toBeVisible();
  const memberCard = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "island member one" });
  await expect(memberCard.getByText("Protected", { exact: true })).toHaveCount(0);

  // Non-scoring: no numeric rank/score/percentage next to the mark.
  await expect(mark).toHaveText("Protected");

  // Legend explains the mark.
  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.locator(LEGEND_TRIGGER).click();
  await expect(page.locator(LEGEND)).toContainText("Protected (do not force-classify; not inferior)");

  // Toggle OFF hides ALL marks (card and island alike) — reversible.
  await page.getByRole("button", { name: "Hide protection marks" }).click();
  await expect(allProtectedMarks).toHaveCount(0);

  // Toggle ON restores both.
  await page.getByRole("button", { name: "Show protection marks" }).click();
  await expect(allProtectedMarks).toHaveCount(2);
});
