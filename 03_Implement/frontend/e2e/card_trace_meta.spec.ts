import { expect, test, type Page } from "@playwright/test";
import { SHARE_REPRODUCE_BUTTON, VIEW_BUTTON } from "./helpers/i18n";

// DOMAIN-TRACE-01 (ADR-0048 D3改訂, schemas.md §15): serial number + raw-data
// source on Card.meta. Covers: side-panel editor + selection summary (AC-1/AC-5),
// undoable single-step edit (AC-3), canvas badge default OFF (AC-4), save
// round-trip via PUT (AC-2), and the share default-exclusion toggle (§15.4).

const START_PANEL = '[data-panel="start-document-entry"]';
const PRIMARY_FLOW = '[data-ui-region="primary-flow"]';

function buildDocument() {
  return {
    version: 2,
    id: "doc_phase1_canvas",
    title: "Trace meta fixture",
    createdAt: "2026-07-08T00:00:00.000Z",
    updatedAt: "2026-07-08T00:00:00.000Z",
    transform: { panX: 100, panY: 100, zoom: 1 },
    cards: [
      { id: "c1", text: "trace target card", x: 0, y: 0 },
      { id: "c2", text: "preset meta card", x: 400, y: 0, meta: { seq: 7, source: "field note 3" } },
    ],
    edges: [],
    islands: [],
    readingOrder: [],
    narratives: [],
    evidenceLinks: [],
    mergeSuggestionDecisions: [],
  };
}

type SavedCard = { id: string; meta?: { seq?: number; source?: string } };

async function routeDocument(page: Page): Promise<{ readSavedCards: () => SavedCard[] | null }> {
  let savedCards: SavedCard[] | null = null;

  await page.route("**/packs/index.json", async (route) => {
    await route.fulfill({ status: 404, contentType: "application/json", body: "{}" });
  });
  await page.route("**/docs/doc_phase1_canvas", async (route) => {
    if (route.request().method() === "PUT") {
      const body = route.request().postDataJSON() as { cards?: SavedCard[] };
      savedCards = body.cards ?? [];
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        headers: { ETag: '"trace-meta-2"' },
        body: route.request().postData() ?? "{}",
      });
      return;
    }
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      headers: { ETag: '"trace-meta"' },
      body: JSON.stringify(buildDocument()),
    });
  });
  await page.route("**/ai/provider-status", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ providerKind: "none" }) });
  });

  return { readSavedCards: () => savedCards };
}

async function openSample(page: Page): Promise<void> {
  const startPanel = page.locator(START_PANEL);
  await expect(startPanel).toBeVisible();
  await startPanel.getByRole("button", { name: /Open sample|サンプルを開く/ }).click();
  await expect(startPanel).toBeHidden();
}

async function selectTraceCard(page: Page): Promise<void> {
  const card = page.locator(`${PRIMARY_FLOW} [role="button"]`, { hasText: "trace target card" });
  await card.click();
  await expect(card).toHaveAttribute("aria-pressed", "true");
}

test("side-panel trace editor sets seq/source, the selection summary shows them, and undo reverts one step", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTraceCard(page);

  const editor = page.locator('[data-panel="card-trace-editor"]');
  await expect(editor).toBeVisible();
  await editor.locator('input[type="number"]').fill("12");
  await editor.locator('input[type="text"]').fill("Interview A line 12");

  const summary = page.locator('[data-panel="card-trace-summary"]');
  await expect(summary).toContainText("#12");
  await expect(summary).toContainText("Interview A line 12");

  // Each field edit is exactly one history step: the first undo drops the
  // source, the second drops the seq, and the summary chip disappears.
  await page.keyboard.press("Control+z");
  await expect(summary).not.toContainText("Interview A line 12");
  await page.keyboard.press("Control+z");
  await expect(summary).toHaveCount(0);
});

test("record details distinguish card identity from unavailable responsibility metadata", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTraceCard(page);

  const details = page.locator('[data-panel="card-record-details"]');
  await expect(details).toBeVisible();
  await details.locator("summary").click();
  await expect(details).toContainText("Card ID");
  await expect(details).toContainText("c1");
  await expect(details).toContainText("Canonical card");
  await expect(details).toContainText("Document created");
  await expect(details).toContainText("2026-07-08T00:00:00.000Z");
  await expect(details).toContainText("Not provided in this data model");
  await expect(details).not.toContainText("reviewerRef");
});

test("canvas seq badge is OFF by default and appears only after the view toggle (AC-4)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  // c2 carries meta.seq = 7 from the fixture, but no badge renders by default.
  await expect(page.locator("[data-card-seq-badge]")).toHaveCount(0);

  await page.getByRole("button", { name: VIEW_BUTTON }).click();
  await page.getByLabel("Show serial numbers on cards").check();

  const badge = page.locator("[data-card-seq-badge]");
  await expect(badge).toHaveCount(1);
  await expect(badge).toHaveText("#7");
});

test("card.meta survives the save round-trip verbatim (AC-2)", async ({ page }) => {
  const { readSavedCards } = await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);
  await selectTraceCard(page);

  const editor = page.locator('[data-panel="card-trace-editor"]');
  await editor.locator('input[type="number"]').fill("42");
  await editor.locator('input[type="text"]').fill("survey B p.4");

  await page.getByRole("button", { name: "Save" }).click();
  await expect(page.getByTestId("status-message")).toContainText(/Saved|保存/);

  const cards = readSavedCards();
  expect(cards).not.toBeNull();
  expect(cards?.find((card) => card.id === "c1")?.meta).toEqual({ seq: 42, source: "survey B p.4" });
  expect(cards?.find((card) => card.id === "c2")?.meta).toEqual({ seq: 7, source: "field note 3" });
});

test("share preflight excludes source references by default; opting in surfaces the warning (§15.4)", async ({ page }) => {
  await routeDocument(page);
  await page.setViewportSize({ width: 1400, height: 900 });
  await page.goto("/?locale=en");
  await openSample(page);

  await page.getByRole("button", { name: SHARE_REPRODUCE_BUTTON }).click();
  const shareDialog = page.locator('[data-panel="share-replay"]');
  await expect(shareDialog).toBeVisible();

  const preflightRow = page.locator("[data-share-preflight-source-references]");
  await expect(preflightRow).toContainText(/Excluded by default|既定で含めません/);
  await expect(page.locator("[data-share-source-references-warning]")).toHaveCount(0);

  await page.locator("[data-share-include-source-references] input").check();
  await expect(page.locator("[data-share-source-references-warning]")).toBeVisible();
  await expect(preflightRow).toContainText(/Source references are included|出典参照を含める設定/);
});
