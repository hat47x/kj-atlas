import { expect, test, type Page } from "@playwright/test";

// DOMAIN-KJ-01 (ADR-0048 D3, schemas.md §3.3): KJ relation vocabulary.
// Covers: type-distinct rendering (AC-4), in-place type change + undo (AC-2),
// and unknown-type round-trip preservation through save (AC-3).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 1,
    id: "doc_phase1_canvas",
    title: "Edge vocabulary fixture",
    createdAt: "2026-07-08T00:00:00.000Z",
    updatedAt: "2026-07-08T00:00:00.000Z",
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [
      { id: "c1", text: "cause card", x: 0, y: 0 },
      { id: "c2", text: "effect card", x: 400, y: 0 },
      { id: "c3", text: "mutual a", x: 0, y: 250 },
      { id: "c4", text: "mutual b", x: 400, y: 250 },
      { id: "c5", text: "same thing a", x: 0, y: 500 },
      { id: "c6", text: "same thing b", x: 400, y: 500 },
    ],
    edges: [
      { id: "e-causal", fromId: "c1", toId: "c2", type: "causal" },
      { id: "e-mutual", fromId: "c3", toId: "c4", type: "mutual" },
      { id: "e-equivalence", fromId: "c5", toId: "c6", type: "equivalence" },
      { id: "e-unknown", fromId: "c1", toId: "c3", type: "future-vocab-2030" },
    ],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

async function routeDocument(page: Page): Promise<{ readSavedEdgeTypes: () => string[] | null }> {
  let savedEdgeTypes: string[] | null = null;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      const body = route.request().postDataJSON() as { edges?: Array<{ type?: string }> };
      savedEdgeTypes = (body.edges ?? []).map((edge) => edge.type ?? "");
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"edge-vocab-2"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"edge-vocab"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return { readSavedEdgeTypes: () => savedEdgeTypes };
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

test("renders type-distinct symbols: causal arrow, mutual double arrow, equivalence '=' (unknown renders plain)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  // causal: exactly one to-end arrowhead; mutual adds one more to-end AND one
  // from-end; equivalence adds the "=" midpoint symbol. The unknown-type edge
  // contributes NO symbol (resolved to plain related).
  await expect(page.locator('[data-edge-symbol="arrow-to"]')).toHaveCount(2);
  await expect(page.locator('[data-edge-symbol="arrow-from"]')).toHaveCount(1);
  await expect(page.locator('[data-edge-symbol="equivalence"]')).toHaveCount(1);
  // All 4 edges (including the preserved unknown one) are drawn.
  await expect(page.locator(`${PRIMARY_FLOW} svg line[stroke="#64748b"]`)).toHaveCount(4);
});

test("changes a persisted edge's type from the inspector as one undoable step", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  // Select the causal edge via its transparent hit line. Coordinate-based
  // clicking is not viable here: the edge SVG spans the ±100000 world
  // coordinate system, so boundingBox() returns off-viewport numbers.
  // dispatchEvent("click") triggers the React onClick handler directly.
  const hitLine = page.locator(`${PRIMARY_FLOW} svg line[stroke="transparent"]`).first();
  await hitLine.dispatchEvent("click");

  // The inspector shows the type select for a persisted edge.
  const inspectorSelect = page.getByTestId("edge-type-select");
  await expect(inspectorSelect).toBeVisible();
  await expect(inspectorSelect).toHaveValue("causal");
  await inspectorSelect.selectOption("mutual");
  await expect(page.getByTestId("status-message")).toContainText('Changed the relation type to "mutual"');

  // One Ctrl+Z reverses it.
  await page.keyboard.press("Control+z");
  await expect(page.getByTestId("status-message")).toContainText(/Undid the last operation/);
});

test("an unknown edge type survives import -> save round-trip verbatim (AC-3)", async ({ page }) => {
  const { readSavedEdgeTypes } = await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  // Make any trivial change to enable save, then save.
  await page.getByRole("button", { name: "New card" }).click();
  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByTestId("status-message")).toContainText(/Saved|保存/);

  const savedTypes = readSavedEdgeTypes();
  expect(savedTypes).not.toBeNull();
  expect(savedTypes).toContain("future-vocab-2030");
  expect(savedTypes).toContain("causal");
  expect(savedTypes).toContain("mutual");
  expect(savedTypes).toContain("equivalence");
});
