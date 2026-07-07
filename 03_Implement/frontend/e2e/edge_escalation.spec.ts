import { expect, test, type Page } from "@playwright/test";

// UX-SCALE-01 (d) (ADR-0048 D2, Round 5 redline): at far LOD, relations
// whose both endpoints collapse into the SAME island are internalized
// (hidden); relations reaching a different island or a still-visible
// lone-wolf card are promoted (drawn island-placard <-> other endpoint).

const START_PANEL = '[data-panel="start-document-entry"]';

function buildDocument(zoom: number) {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Edge escalation fixture",
    createdAt: "2026-07-07T00:00:00.000Z",
    updatedAt: "2026-07-07T00:00:00.000Z",
    transform: { panX: 300, panY: 300, zoom },
    cards: [
      { id: "a1", text: "island A member 1", x: 0, y: 0 },
      { id: "a2", text: "island A member 2", x: 100, y: 0 },
      { id: "b1", text: "island B member 1", x: 500, y: 0 },
      { id: "lone", text: "lone wolf card", x: 250, y: 220 },
    ],
    edges: [
      // Both endpoints in island A: should internalize (never drawn).
      { id: "e-internal", fromId: "a1", toId: "a2", type: "related" },
      // Island A <-> island B: should promote to an island<->island edge.
      { id: "e-cross-island", fromId: "a1", toId: "b1", type: "related" },
      // Island A member <-> lone-wolf card: should promote to island<->card.
      { id: "e-to-lone-wolf", fromId: "a2", toId: "lone", type: "related" },
    ],
    islands: [
      { id: "islA", cardIds: ["a1", "a2"] },
      { id: "islB", cardIds: ["b1"] },
    ],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(page: Page, zoom: number): Promise<void> {
  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"edge-escalation"' },
      body: JSON.stringify(buildDocument(zoom)),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });
}

async function openSampleWithLodEnabled(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample/ }).click();
  await expect(startPanel).toBeHidden();

  await page.getByRole("button", { name: "View", exact: true }).click();
  await page.getByRole("checkbox", { name: "Auto detail by zoom (LOD)" }).check();
  await page.getByRole("button", { name: "View", exact: true }).click();
}

test("far LOD internalizes the same-island relation and promotes cross-island and lone-wolf relations", async ({ page }) => {
  await routeDocument(page, 0.3);
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto("/?locale=en");
  await openSampleWithLodEnabled(page);
  await page.waitForTimeout(300);

  // Two derived (dashed, isDerived) edges should exist: island<->island and
  // island<->lone-wolf-card. Derived edges render with stroke "#0f766e".
  const derivedLines = page.locator('svg line[stroke="#0f766e"]');
  await expect(derivedLines).toHaveCount(2);
});

test("zooming back in restores the plain card-card edges and removes the derived ones", async ({ page }) => {
  await routeDocument(page, 1);
  await page.setViewportSize({ width: 1200, height: 800 });
  await page.goto("/?locale=en");
  await openSampleWithLodEnabled(page);
  await page.waitForTimeout(300);

  await expect(page.locator('svg line[stroke="#0f766e"]')).toHaveCount(0);
});
